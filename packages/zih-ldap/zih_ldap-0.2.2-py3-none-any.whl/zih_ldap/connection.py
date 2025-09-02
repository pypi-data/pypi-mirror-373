"""ldap connection"""

import ssl
from typing import Any, Callable, Literal, TypeVar

from ldap3 import SAFE_RESTARTABLE, SCHEMA, Connection, Server, Tls
from ldap3.core.exceptions import LDAPOperationResult
from pydantic import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


def new_ldap_connection(
    url: str,
    user_bind_dn: str | None = None,
    password: str | None = None,
    port: int = 636,
) -> "LDAPConnection":
    """return new ldap3 connection"""

    def connect() -> Connection:
        tls_config = Tls(
            validate=ssl.CERT_REQUIRED,
            version=ssl.PROTOCOL_TLSv1_2,
        )

        server = Server(
            url,
            port=port,
            use_ssl=True,
            tls=tls_config,
            get_info=SCHEMA,
        )
        return Connection(
            server,
            user_bind_dn,
            password,
            receive_timeout=60,
            auto_bind="TLS_BEFORE_BIND",
            client_strategy=SAFE_RESTARTABLE,
        )

    return LDAPConnection(connect)


class LDAPException(Exception):
    """ldap exception"""


class MultipleObjectsReturned(LDAPException):
    """one expected but multiple objects returned"""


class ObjectDoesNotExist(LDAPException):
    """one expected but nothing found"""


class LDAPConnection:
    """ldap connection"""

    def __init__(
        self,
        connect: Callable[[], Connection],
        paged_size: int = 0,
    ) -> None:
        self._connect = connect
        self._connection_singleton: Connection | None = None
        self._paged_size = paged_size

    @property
    def _connection(self) -> Connection:
        """ldap3 connection"""
        if self._connection_singleton is None:
            self._connection_singleton = self._connect()
        return self._connection_singleton

    def _search_simple(
        self,
        search_base: str,
        filter_term: str,
        search_scope: Literal["BASE", "LEVEL", "SUBTREE"],
        attributes: list[str],
    ) -> list[dict[str, Any]]:
        _, result, response, _ = self._connection.search(
            search_base,
            filter_term,
            search_scope,
            attributes=attributes,
        )

        if result["result"] not in (0, 4) or response is None:
            raise LDAPException(f"LDAP search failed: {result['description']}")
        assert isinstance(response, list)
        return response

    def _search_paged(
        self,
        search_base: str,
        filter_term: str,
        search_scope: Literal["BASE", "LEVEL", "SUBTREE"],
        attributes: list[str],
    ) -> list[dict[str, Any]]:
        try:
            response = self._connection.extend.standard.paged_search(
                search_base,
                filter_term,
                search_scope,
                attributes=attributes,
                paged_size=self._paged_size,
                generator=False,
            )
            assert isinstance(response, list)
            return response
        except LDAPOperationResult as e:
            raise LDAPException(f"LDAP error: {e}") from e

    def _search(
        self,
        search_base: str,
        filter_term: str,
        search_scope: Literal["BASE", "LEVEL", "SUBTREE"],
        attributes: list[str],
    ) -> list[dict[str, Any]]:
        if self._paged_size:
            return self._search_paged(
                search_base, filter_term, search_scope, attributes
            )
        return self._search_simple(
            search_base, filter_term, search_scope, attributes
        )

    @staticmethod
    def fix_result(entry: dict[str, Any]) -> dict[str, str | list[Any]]:
        """fix result"""
        return {
            key: value if isinstance(value, list) else [value]
            for key, value in entry["attributes"].items()
        } | {"dn": entry["dn"]}

    def get(
        self,
        filter_term: str,
        search_base: str,
        attributes_model: type[ModelT],
        search_scope: Literal["LEVEL", "SUBTREE"] = "LEVEL",
        ignored_attributes: list[str] | None = None,
    ) -> ModelT:
        """Get one object from LDAP by filter term.

        raise:
          MultipleObjectsReturned - if more than one element found
          ObjectDoesNotExist - if no element was found
        """
        finds = self.filter(
            filter_term,
            search_base,
            attributes_model,
            search_scope,
            ignored_attributes,
        )
        if len(finds) > 1:
            raise MultipleObjectsReturned(
                "Got multiple results from ldap, but only one was expected!"
            )
        if len(finds) == 0:
            raise ObjectDoesNotExist(
                "No object was found, but one was expected!"
            )
        return finds[0]

    def filter(
        self,
        filter_term: str,
        search_base: str,
        attributes_model: type[ModelT],
        search_scope: Literal["BASE", "LEVEL", "SUBTREE"] = "LEVEL",
        ignored_attributes: list[str] | None = None,
    ) -> list[ModelT]:
        """query all elements for given python ldap3 search term"""
        if ignored_attributes is None:
            ignored_attributes = []
        ignored_attributes.append("dn")

        response = self._search(
            search_base,
            filter_term,
            search_scope,
            attributes=[
                attr
                for attr in attributes_model.model_json_schema(
                    mode="serialization"
                )["properties"]
                if attr not in ignored_attributes
            ],
        )

        return [
            attributes_model.model_validate(self.fix_result(entry))
            for entry in response
        ]
