"""test ldap"""

from datetime import date
from typing import ClassVar
from unittest import TestCase

import pytest
from typing_extensions import override

from .conftest import Settings
from .connection import LDAPConnection, ObjectDoesNotExist, new_ldap_connection
from .models import (
    LdapOrgUnitManager,
    LdapUserManager,
    newLdapFacilityBuildingManager,
    newLdapFacilityFloorManager,
    newLdapFacilityInstitutionManager,
    newLdapFacilityMacroLocationManager,
    newLdapFacilityMicroLocationManager,
    newLdapFacilityRoomManager,
)


@pytest.fixture(scope="class")
def external_connection(
    request: pytest.FixtureRequest, external_settings: Settings
) -> None:
    """make connection"""
    request.cls.external_connection = new_ldap_connection(
        external_settings.ldap_address,
        external_settings.ldap_user_bind_dn,
        external_settings.ldap_password.get_secret_value(),
        port=external_settings.ldap_port,
    )


@pytest.mark.usefixtures("external_connection")
class TestLDAP(TestCase):
    """test LDAP

    Some simple tests against the productive ldap via LDAPConnection
    """

    external_connection: ClassVar[LDAPConnection]

    @override
    def setUp(
        self,
    ) -> None:
        super().setUp()
        self.user_manager = LdapUserManager(self.external_connection)
        self.ou_manager = LdapOrgUnitManager(self.external_connection)

    def test_get_user_by_uid(self) -> None:
        """get user by uid"""

        expected = self.user_manager.get("teal858d")
        self.assertIsNotNone(expected)
        assert expected
        self.assertEqual(
            expected.displayName, "Alleskönner, Testobjekt (SSP-Tester)"
        )

    def test_try_get_user_with_wrong_uid(self) -> None:
        """try get user with wrong uid"""

        with self.assertRaises(ObjectDoesNotExist):
            self.user_manager.get("gdjfgjsdfjksdh")

    def test_try_get_user_with_escape(self) -> None:
        """try get user with uid that needs to be escaped"""

        with self.assertRaises(ObjectDoesNotExist):
            self.user_manager.get("teal858d)")

    def test_get_users_by_searchterm(self) -> None:
        """get users by searchterm"""
        expected = self.user_manager.filter("(sn=Schmidt)")
        self.assertNotEqual(len(expected), 0)
        # https://github.com/pylint-dev/astroid/issues/1015
        # pylint: disable=not-an-iterable
        for user in expected:
            self.assertEqual(user.last_name, "Schmidt")

    def test_get_users_by_bulk_request(self) -> None:
        """get users by a set of uids"""
        usernames = {"teal858d", "tete554d"}
        users = self.user_manager.get_bulk(usernames)
        self.assertNotEqual(users, {})
        self.assertCountEqual(usernames, users.keys())

    def test_get_orgunit_by_ou(self) -> None:
        """get orgUnit by ou"""

        expected = self.ou_manager.get("10000009")
        self.assertIsNotNone(expected)
        assert expected
        self.assertEqual(expected.zihExpiryDate, date(9999, 12, 31))

    def test_try_get_orgunit_with_wrong_ou(self) -> None:
        """try get orgunit with wrong ou"""
        with self.assertRaises(ObjectDoesNotExist):
            self.ou_manager.get("1000sgfsggdfgd dgdg 0009")

    def test_try_get_orgunit_with_escape(self) -> None:
        """try get orgunit with ou that needs to be escaped"""

        with self.assertRaises(ObjectDoesNotExist):
            self.ou_manager.get("10000009)")

    def test_get_orgunit_by_searchterm(self) -> None:
        """get orgunit by searchterm"""
        expected = self.ou_manager.filter("(zihExpiryDate=99991231)")
        self.assertNotEqual(len(expected), 0)
        # https://github.com/pylint-dev/astroid/issues/1015
        # pylint: disable=not-an-iterable
        for org_unit in expected:
            self.assertEqual(org_unit.zihExpiryDate, date(9999, 12, 31))


@pytest.mark.usefixtures("external_connection")
class TestLDAPFacilities(TestCase):
    """test LDAP facilities"""

    external_connection: ClassVar[LDAPConnection]

    def test_get_institution_by_id(self) -> None:
        """get institution by id"""
        expected = newLdapFacilityInstitutionManager(
            self.external_connection
        ).get("TU")
        self.assertEqual(
            expected.zihFacilityName, "Technische Universität Dresden"
        )

    def test_get_macro_location_by_id(self) -> None:
        """get macro location by id"""
        expected = newLdapFacilityMacroLocationManager(
            self.external_connection
        ).get("TU-DD")
        self.assertEqual(expected.zihFacilityName, "Dresden")

    def test_get_micro_location_by_id(self) -> None:
        """get micro location by id"""
        expected = newLdapFacilityMicroLocationManager(
            self.external_connection
        ).get("TU-DD-200")
        self.assertEqual(expected.zihFacilityName, "Hörsaalzentrum")

    def test_get_building_by_id(self) -> None:
        """get building by id"""
        expected = newLdapFacilityBuildingManager(
            self.external_connection
        ).get("TU-DD-200-1361")
        self.assertEqual(
            expected.zihFacilityName, "HSZ Hörsaalzentrum, Bergstr. 64"
        )

    def test_get_floor_by_id(self) -> None:
        """get floor by id"""
        expected = newLdapFacilityFloorManager(self.external_connection).get(
            "TU-DD-200-1361-01"
        )
        self.assertEqual(expected.zihFacilityName, "01")

    def test_get_room_by_id(self) -> None:
        """get room by id"""
        expected = newLdapFacilityRoomManager(self.external_connection).get(
            "TU-DD-200-1361-01-0140"
        )
        self.assertEqual(expected.zihFacilityName, "114")
