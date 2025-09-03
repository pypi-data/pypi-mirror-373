#  Copyright (c) 2022 bastien.saltel
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import stat
import threading
import socket
import sys
import traceback
import os
import asyncio
import logging
from abc import ABC,                                                    \
                abstractmethod
import paramiko
from paramiko import sftp_client,                                       \
                     sftp_server
from paramiko.server import ServerInterface
from paramiko.sftp_attr import SFTPAttributes
from pysftp import CnOpts
from typing import Callable,                                            \
                   Awaitable,                                           \
                   Any
from asyncssh.connection import listen
from asyncssh.channel import SSHServerChannel
from asyncssh import sftp
from asyncssh.misc import ConnectionLost
from asyncssh.sftp import SFTPNoConnection
import asyncssh
from tenacity.asyncio import AsyncRetrying
from tenacity.retry import retry_if_result,                             \
                           retry_if_exception_type
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_fixed
from tenacity import RetryError
from tenacity.before import before_log
from tenacity.after import after_log

from galaxy.service import constant
from galaxy.net.net import Client,                                      \
                           AsyncClient,                                 \
                           Server,                                      \
                           AsyncServer
from galaxy.net.auth import CredentialBuilder
from galaxy.net.ssh.ssh import SSHAsyncConnectionFactory,               \
                               SSHClientConnection
from galaxy.net.ssh.transport import SSHTransportFactory
from galaxy.net.ssh.protocol import AsyncSSHProtocol
from galaxy.perfo.decorator import timed,                               \
                                   async_timed
from galaxy.kernel.loop import AsyncioLoop


class SFTPClient(Client, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SFTPClient, self).__init__()

    @abstractmethod
    def _connect(self) -> None:
        raise NotImplementedError("Should implement _connect()")

    @abstractmethod
    def chdir(self, path: str) -> None:
        raise NotImplementedError("Should implement chdir()")

    @abstractmethod
    def chmod(self, path: str, mode: int) -> None:
        raise NotImplementedError("Should implement chmod()")

    @abstractmethod
    def chown(self, path: str, uid: int, gid: int) -> None:
        raise NotImplementedError("Should implement chown()")

    @abstractmethod
    def get(self, remote_path: str, local_path: str) -> None:
        raise NotImplementedError("Should implement get()")

    @abstractmethod
    def getcwd(self) -> str:
        raise NotImplementedError("Should implement getcwd()")

    @abstractmethod
    def listdir(self, path: str = ".") -> list[str]:
        raise NotImplementedError("Should implement listdir()")

    @abstractmethod
    def mkdir(self, path: str, mode: int | None = 511) -> None:
        raise NotImplementedError("Should implement mkdir()")

    @abstractmethod
    def put(self, local_path: str, remote_path: str) -> None:
        raise NotImplementedError("Should implement put()")

    @abstractmethod
    def rm(self, path: str) -> None:
        raise NotImplementedError("Should implement remove()")

    @abstractmethod
    def mv(self, old_path: str, new_path: str) -> None:
        raise NotImplementedError("Should implement rename()")

    @abstractmethod
    def rmdir(self, path: str, force: bool | None = False) -> None:
        raise NotImplementedError("Should implement rmdir()")

    @abstractmethod
    def _close(self) -> None:
        raise NotImplementedError("Should implement _close()")

    def __repr__(self) -> str:
        return "<SFTPClient(id='{}')>".format(self.id)


class ParamikoSFTPClient(SFTPClient):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ParamikoSFTPClient, self).__init__()
        self.transport_fact: SSHTransportFactory | None = None
        self.client: sftp_client.SFTPClient | None = None

    @timed
    def _load(self) -> None:
        super(ParamikoSFTPClient, self)._load()

    def _connect(self) -> None:
        opt = CnOpts()
        opt.hostkeys = None
        cred = CredentialBuilder().from_conf(self.conf["cred"]).build()
        transport = self.transport_fact.create()
        transport.connect(username=cred.username,
                          password=cred.password)
        self.client = sftp_client.SFTPClient.from_transport(transport)
        if self.client is None:
            raise

    def chdir(self, path: str) -> None:
        return self.client.chdir(path)

    def chmod(self, path: str, mode: int) -> None:
        return self.client.chmod(path, mode)

    def chown(self, path: str, uid: int, gid: int) -> None:
        return self.client.chown(uid, gid)

    def get(self, remote_path: str, local_path: str) -> None:
        return self.client.get(remote_path, local_path)

    def getcwd(self) -> str:
        return self.client.getcwd()

    def listdir(self, path: str = ".") -> list[str]:
        output = self.client.listdir_attr(path)
        return output

    def mkdir(self, path: str, mode: int | None = 511) -> None:
        return self.client.mkdir(path, mode)

    def put(self, local_path: str, remote_path: str) -> None:
        return self.client.put(local_path, remote_path)

    def rm(self, path: str) -> None:
        return self.client.remove(path)

    def mv(self, old_path: str, new_path: str) -> None:
        return self.client.rename(old_path, new_path)

    def rmdir(self, path: str, force: bool | None = False) -> None:
        if force:
            self._rmdir(path)
        else:
            self.client.rmdir(path)

    def _rmdir(self, path: str) -> None:
        for item in list(self.client.listdir_iter(path)):
            filepath = "/".join([path, item.filename])
            if stat.S_IFMT(item.st_mode) == stat.S_IFDIR:
                self._rmdir(filepath)
                continue
            self.client.remove(filepath)
        return self.client.rmdir(path)

    def _close(self) -> None:
        return self.client.close()

    def __repr__(self) -> str:
        return "<ParamikoSFTPClient(id='{}')>".format(self.id)


class SFTPAsyncClient(AsyncClient, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SFTPAsyncClient, self).__init__()
        self.loop: AsyncioLoop | None = None

        # Factory
        self.conn_fact: SSHAsyncConnectionFactory | None = None

    @async_timed
    async def _load(self) -> None:
        await super(SFTPAsyncClient, self)._load()

    @abstractmethod
    async def _connect(self) -> None:
        raise NotImplementedError("Should implement _connect()")

    @abstractmethod
    async def chdir(self, path: str) -> None:
        raise NotImplementedError("Should implement chdir()")

    @abstractmethod
    async def chmod(self, path: str, mode: int) -> None:
        raise NotImplementedError("Should implement chmod()")

    @abstractmethod
    async def chown(self, path: str, uid: int, gid: int) -> None:
        raise NotImplementedError("Should implement chown()")

    @abstractmethod
    async def get(self, remote_path: str, local_path: str) -> None:
        raise NotImplementedError("Should implement get()")

    @abstractmethod
    async def getcwd(self) -> str:
        raise NotImplementedError("Should implement getcwd()")

    @abstractmethod
    async def listdir(self, path: str = ".") -> list[str]:
        raise NotImplementedError("Should implement listdir()")

    @abstractmethod
    async def mkdir(self, path: str, mode: int | None = 511) -> None:
        raise NotImplementedError("Should implement mkdir()")

    @abstractmethod
    async def put(self, local_path: str, remote_path: str) -> None:
        raise NotImplementedError("Should implement put()")

    @abstractmethod
    async def rm(self, path: str) -> None:
        raise NotImplementedError("Should implement remove()")

    @abstractmethod
    async def mv(self, old_path: str, new_path: str) -> None:
        raise NotImplementedError("Should implement rename()")

    @abstractmethod
    async def rmdir(self, path: str, force: bool | None = False) -> None:
        raise NotImplementedError("Should implement rmdir()")

    @abstractmethod
    async def _close(self) -> None:
        raise NotImplementedError("Should implement _close()")

    def __repr__(self) -> str:
        return "<SFTPAsyncClient(id='{}')>".format(self.id)


class AsyncSSHSFTPAsyncClient(SFTPAsyncClient):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(AsyncSSHSFTPAsyncClient, self).__init__()
        self.protocol: AsyncSSHProtocol | None = None
        self.transport: SSHClientConnection | None = None
        self.client: asyncssh.sftp.SFTPClient | None = None

    @async_timed
    async def _load(self) -> None:
        await super(AsyncSSHSFTPAsyncClient, self)._load()

    @async_timed
    async def _connect(self) -> None:
        self.transport, self.protocol = await self.conn_fact.from_conf(self.conf).create(self)
        self.client = await self.transport.start_sftp_client()
        self.transport.set_keepalive(interval=self.conf["keepalive"])

    @async_timed
    async def _exec(self, attempt_nb: int, func: Callable[[...], Awaitable[Any]], *args, **kwargs) -> Any:
        self.log.logger.debug("Execute the function '{}' (Attempt {})".format(getattr(func, "__name__", repr(callable)),
                                                                              attempt_nb))
        try:
            resp = await func(*args, **kwargs)
            self.log.logger.debug("The function '{}' (Attempt {}) has been executed successfully".format(getattr(func, "__name__", repr(callable)),
                                                                                                         attempt_nb))
        except Exception as e:
            self.log.logger.error("The execution of the function '{}' (Attempt {}) fails with the exception '{}'".format(getattr(func, "__name__", repr(callable)),
                                                                                                                         attempt_nb,
                                                                                                                         str(e)))
            raise e
        return resp

    @async_timed
    async def _exec_with_retries(self, func: Callable[[...], Awaitable[Any]], *args, **kwargs) -> Any:
        resp = None
        tenacity_kwargs = {
                           "retry": (retry_if_exception_type(asyncio.TimeoutError) |
                                     retry_if_exception_type(asyncio.CancelledError)),
                           "before": before_log(self.log.logger, logging.DEBUG),
                           "after": after_log(self.log.logger, logging.DEBUG),
                           "reraise": True
                          }
        if self.is_connected:
            if "retries" in self.conf:
                retries = self.conf["retries"].get("total", 1)
                tenacity_kwargs["stop"] = stop_after_attempt(retries)
        if "req_interval" in self.conf:
            tenacity_kwargs["wait"] = wait_fixed(self.conf["req_interval"])
        try:
            async for attempt in AsyncRetrying(**tenacity_kwargs):
                with attempt:
                    resp = await self._exec(attempt.retry_state.attempt_number, func, *args, **kwargs)
        except RetryError:
            pass
        return resp

    async def exec(self, func: Callable[[...], Awaitable[Any]], *args, **kwargs):
        tenacity_kwargs = {
                           "retry": (retry_if_exception_type(ConnectionLost) |
                                     retry_if_exception_type(SFTPNoConnection)),
                           "before": before_log(self.log.logger, logging.DEBUG),
                           "after": after_log(self.log.logger, logging.DEBUG)
                          }
        if "reconnect_interval" in self.conf:
            tenacity_kwargs["wait"] = wait_fixed(self.conf["reconnect_interval"])
        reconnecting = False
        try:
            async for attempt in AsyncRetrying(**tenacity_kwargs):
                resp = None
                with attempt:
                    if reconnecting:
                        await self.connect()
                        reconnecting = False
                    try:
                        resp = await self._exec_with_retries(func, *args, **kwargs)
                    except (ConnectionLost, SFTPNoConnection) as e:
                        if self.state != constant.STATE_CLOSED:
                            if "reconnect_interval" in self.conf:
                                self.log.logger.error("The execution of function '{}' fails : starting to reconnect after {} sec".format(getattr(func, "__name__", repr(callable)),
                                                                                                                                         self.conf["reconnect_interval"]))
                            else:
                                self.log.logger.error("The execution of function '{}' fails : starting to reconnect".format(getattr(func, "__name__", repr(callable))))
                            await self.close()
                            reconnecting = True
                        raise e
        except RetryError:
            pass
        return resp

    async def chdir(self, path: str) -> None:
        await self.exec(self.client.chdir, path)

    async def chmod(self, path: str, mode: int) -> None:
        await self.exec(self.client.chmod, path, mode)

    async def chown(self, path: str, uid: int, gid: int) -> None:
        await self.exec(self.client.chown, path, uid, gid)

    async def get(self, remote_path: str, local_path: str) -> None:
        await self.exec(self.client.get, remote_path, local_path)

    async def getcwd(self) -> str:
        return await self.exec(self.client.getcwd)

    async def listdir(self, path: str = ".") -> list[str]:
        return await self.exec(self.client.listdir, path)

    async def mkdir(self, path: str, mode: int | None = 511) -> None:
        attr = sftp.SFTPAttrs()
        attr.permissions = mode
        await self.exec(self.client.mkdir, path, attr)

    async def put(self, local_path: str, remote_path: str) -> None:
        await self.exec(self.client.put, local_path, remote_path)

    async def rm(self, path: str) -> None:
        await self.exec(self.client.remove, path)

    async def mv(self, old_path: str, new_path: str) -> None:
        await self.exec(self.client.rename, old_path, new_path)

    async def rmdir(self, path: str, force: bool | None = False) -> None:
        await self.exec(self.client.rmdir, path)

    @async_timed
    async def _close(self) -> None:
        self.client.exit()
        await self.client.wait_closed()
        self.transport.close()
        await self.transport.wait_closed()


class ParamikoServerInterface(ServerInterface):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        super(ParamikoServerInterface, self).__init__()
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if (username == "robey") and (password == "foo"):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username, key):
        return paramiko.AUTH_SUCCESSFUL

    def check_auth_gssapi_with_mic(self, username, gss_authenticated=paramiko.AUTH_FAILED, cc_file = None):

        if gss_authenticated == paramiko.AUTH_SUCCESSFUL:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_gssapi_keyex(self, username, gss_authenticated=paramiko.AUTH_FAILED, cc_file = None):
        if gss_authenticated == paramiko.AUTH_SUCCESSFUL:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def enable_auth_gssapi(self):
        return True

    def get_allowed_auths(self, username):
        return "gssapi-keyex,gssapi-with-mic,password,publickey"

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self,
                                  channel,
                                  term,
                                  width,
                                  height,
                                  pixelwidth,
                                  pixelheight,
                                  modes):
        return True


class SFTPServer(Server, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SFTPServer, self).__init__()

    @abstractmethod
    def _start(self) -> None:
        raise NotImplementedError("Should implement _start()")

    @abstractmethod
    def _stop(self) -> None:
        raise NotImplementedError("Should implement _stop()")

    def __repr__(self) -> str:
        return "<SFTPServer(id='{}')>".format(self.id)


class ParamikoSFTPServer(SFTPServer):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ParamikoSFTPServer, self).__init__()
        self.event = threading.Event()
        self.host_key = paramiko.RSAKey(filename="test_rsa.key")

    def _start(self) -> None:
        # now connect
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("", 2200))
        except Exception as e:
            print("*** Bind failed: " + str(e))
            traceback.print_exc()
            sys.exit(1)

        try:
            sock.listen(100)
            print("Listening for connection ...")
            client, addr = sock.accept()
        except Exception as e:
            print("*** Listen/accept failed: " + str(e))
            traceback.print_exc()
            sys.exit(1)

        print("Got a connection!")

        try:
            t = paramiko.Transport(client, gss_kex=True)
            t.set_gss_host(socket.getfqdn(""))
            try:
                t.load_server_moduli()
            except:
                print("(Failed to load moduli -- gex will be unsupported.)")
                raise
            t.add_server_key(self.host_key)
            server = ParamikoServerInterface()
            try:
                t.start_server(server=server)
            except paramiko.SSHException:
                print("*** SSH negotiation failed.")
                sys.exit(1)

            # wait for auth
            chan = t.accept(20)
            if chan is None:
                print("*** No channel.")
                sys.exit(1)
            print("Authenticated!")

            server.event.wait(10)
            if not server.event.is_set():
                print("*** Client never asked for a shell.")
                sys.exit(1)

            chan.send("\r\n\r\nWelcome to my dorky little BBS!\r\n\r\n")
            chan.send("We are on fire all the time!  Hooray!  Candy corn for everyone!\r\n")
            chan.send("Happy birthday to Robot Dave!\r\n\r\n")
            chan.send("Username: ")
            f = chan.makefile("rU")
            username = f.readline().strip("\r\n")
            chan.send("\r\nI don't like you, " + username + ".\r\n")
            chan.close()

        except Exception as e:
            print("*** Caught exception: " + str(e.__class__) + ": " + str(e))
            traceback.print_exc()
            try:
                t.close()
            except:
                pass
            sys.exit(1)

    def _stop(self) -> None:
        pass

    def __repr__(self) -> str:
        return "<ParamikoSFTPServer(id='{}')>".format(self.id)


class SFTPAsyncServer(AsyncServer, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SFTPAsyncServer, self).__init__()

    @abstractmethod
    async def _start(self) -> None:
        raise NotImplementedError("Should implement _start()")

    @abstractmethod
    async def _stop(self) -> None:
        raise NotImplementedError("Should implement _stop()")

    def __repr__(self) -> str:
        return "<SFTPAsyncServer(id='{}')>".format(self.id)


class AsyncSSHSFTPServer(sftp.SFTPServer):
    """
    classdocs
    """

    def __init__(self, channel: SSHServerChannel) -> None:
        """
        Constructor
        """
        root = "/tmp/sftp/" + channel.get_extra_info("username")
        os.makedirs(root, exist_ok=True)
        super(AsyncSSHSFTPServer, self).__init__(channel, chroot=root)


class AsyncSSHSFTPAsyncServer(SFTPAsyncServer):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(AsyncSSHSFTPAsyncServer, self).__init__()

    async def _start(self) -> None:
        await listen("",
                     8022,
                     server_host_keys=["ssh_host_key"],
                     authorized_client_keys="ssh_user_ca",
                     sftp_factory=AsyncSSHSFTPServer)

    async def _stop(self) -> None:
        pass

    def __repr__(self) -> str:
        return "<SFTPAsyncServer(id='{}')>".format(self.id)
