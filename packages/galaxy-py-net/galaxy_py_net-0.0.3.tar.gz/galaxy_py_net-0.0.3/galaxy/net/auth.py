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

from abc import ABC,                                    \
                abstractmethod
from typing import Any
from requests.auth import HTTPBasicAuth
import requests_ntlm
import httpx_ntlm

from galaxy.utils.base import Component,                \
                              Configurable
from galaxy.utils.pattern import Builder
from galaxy.service.log import LogService,              \
                               LogAsyncService


class Credential(object):
    """
    classdocs
    """

    def __init__(self,
                 username: str | None = None,
                 password: str | None = None,
                 domain: str | None = None,
                 private_key: str | None = None,
                 passphrase: str | None = None,
                 tenant_id: str | None = None,
                 client_id: str | None = None,
                 secret: str | None = None) -> None:
        """
        Constructor
        """
        self.username: str | None = username
        self.password: str | None = password
        self.domain: str | None = domain
        self.private_key: str | None = private_key
        self.passphrase: str | None = passphrase
        self.tenant_id: str | None = tenant_id
        self.client_id: str | None = client_id
        self.secret: str | None = secret

    def get_user(self) -> str:
        if self.domain is None:
            return self.username
        return "{}\\{}".format(self.domain, self.username)

    def __str__(self) -> str:
        return self.username

    def __repr__(self) -> str:
        return "<Authentication(username='{}')>".format(self.username)

    def __eq__(self, other: "Credential") -> bool:
        return self.username == other.username and self.domain == other.domain

    def __ne__(self, other: "Credential") -> bool:
        return self.username != other.username or self.domain != other.domain


class CredentialBuilder(Builder):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        super(CredentialBuilder, self).__init__()
        self._username: str | None = None
        self._password: str | None = None
        self._domain: str | None = None
        self._private_key: str | None = None
        self._passphrase: str | None = None
        self._tenant_id: str | None = None
        self._client_id: str | None = None
        self._secret: str | None = None

    def username(self, username: str) -> "CredentialBuilder":
        self._username = username
        return self

    def password(self, password: str) -> "CredentialBuilder":
        self._password = password
        return self

    def domain(self, domain: str) -> "CredentialBuilder":
        self._domain = domain
        return self

    def private_key(self, private_key: str) -> "CredentialBuilder":
        self._private_key = private_key
        return self

    def passphrase(self, passphrase: str) -> "CredentialBuilder":
        self._passphrase = passphrase
        return self

    def tenant_id(self, tenant_id: str) -> "CredentialBuilder":
        self._tenant_id = tenant_id
        return self

    def client_id(self, client_id: str) -> "CredentialBuilder":
        self._client_id = client_id
        return self

    def secret(self, secret: str) -> "CredentialBuilder":
        self._secret = secret
        return self

    def from_conf(self, conf: dict) -> "CredentialBuilder":
        if "username" in conf:
            self._username = conf["username"]
        if "password" in conf:
            self._password = conf["password"]
        if "domain" in conf:
            self._domain = conf["domain"]
        if "private_key" in conf:
            self._private_key = conf["private_key"]
        if "passphrase" in conf:
            self._passphrase = conf["passphrase"]
        if "tenant_id" in conf:
            self._tenant_id = conf["tenant_id"]
        if "client_id" in conf:
            self._client_id = conf["client_id"]
        if "secret" in conf:
            self._secret = conf["secret"]
        return self

    def build(self) -> Credential:
        return Credential(self._username,
                          self._password,
                          self._domain,
                          self._private_key,
                          self._passphrase,
                          self._tenant_id,
                          self._client_id,
                          self._secret)


class HTTPAuthenticationFactory(Component, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(HTTPAuthenticationFactory, self).__init__()
        self.log: LogService | LogAsyncService | None = None

    @abstractmethod
    def create(self, cred: Credential) -> Any:
        raise NotImplementedError("Should implement create()")


class HTTPBasicAuthenticationFactory(HTTPAuthenticationFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(HTTPBasicAuthenticationFactory, self).__init__()

    def create(self, cred: Credential) -> Any:
        raise NotImplementedError("Should implement create()")


class RequestsHTTPBasicAuthenticationFactory(HTTPBasicAuthenticationFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(RequestsHTTPBasicAuthenticationFactory, self).__init__()

    def create(self, cred: Credential) -> HTTPBasicAuth:
        return HTTPBasicAuth(cred.get_user(), cred.password)


class HTTPNTLMAuthenticationFactory(HTTPAuthenticationFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(HTTPNTLMAuthenticationFactory, self).__init__()

    def create(self, cred: Credential) -> Any:
        raise NotImplementedError("Should implement create()")


class RequestsHTTPNTLMAuthenticationFactory(HTTPNTLMAuthenticationFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(RequestsHTTPNTLMAuthenticationFactory, self).__init__()

    def create(self, cred: Credential) -> requests_ntlm.HttpNtlmAuth:
        return requests_ntlm.HttpNtlmAuth(cred.get_user(), cred.password)


class HTTPXHTTPNTLMAuthenticationFactory(HTTPNTLMAuthenticationFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(HTTPXHTTPNTLMAuthenticationFactory, self).__init__()

    def create(self, cred: Credential) -> httpx_ntlm.HttpNtlmAuth:
        return httpx_ntlm.HttpNtlmAuth(cred.get_user(), cred.password)
