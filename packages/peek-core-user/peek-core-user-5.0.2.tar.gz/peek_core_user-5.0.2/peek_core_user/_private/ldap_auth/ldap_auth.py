"""
{'objectClass': [b'top', b'person', b'organizationalPerson', b'user'], 'cn': [b'attest'],
 'givenName': [b'attest'],
 'distinguishedName': [b'CN=attest,OU=testou,DC=synad,DC=synerty,DC=com'],
 'instanceType': [b'4'], 'whenCreated': [b'20170505160836.0Z'],
 'whenChanged': [b'20190606130621.0Z'], 'displayName': [b'attest'],
 'uSNCreated': [b'16498'],
 'memberOf': [b'CN=Domain Admins,CN=Users,DC=synad,DC=synerty,DC=com',
              b'CN=Enterprise Admins,CN=Users,DC=synad,DC=synerty,DC=com',
              b'CN=Administrators,CN=Builtin,DC=synad,DC=synerty,DC=com'],
 'uSNChanged': [b'73784'], 'name': [b'attest'],
 'objectGUID': [b'\xee\x1bV\x8dQ\xackE\x82\xd9%_\x18\xadjO'],
 'userAccountControl': [b'66048'], 'badPwdCount': [b'0'], 'codePage': [b'0'],
 'countryCode': [b'0'], 'badPasswordTime': [b'132042996316396717'], 'lastLogoff': [b'0'],
 'lastLogon': [b'132042996806397639'], 'pwdLastSet': [b'132042997225927009'],
 'primaryGroupID': [b'513'], 'objectSid': [
    b'\x01\x05\x00\x00\x00\x00\x00\x05\x15\x00\x00\x00D:3|X\x8f\xc7\x08\xe6\xeaV\xc8Q\x04\x00\x00'],
 'adminCount': [b'1'], 'accountExpires': [b'9223372036854775807'], 'logonCount': [b'36'],
 'sAMAccountName': [b'attest'], 'sAMAccountType': [b'805306368'],
 'userPrincipalName': [b'attest@synad.synerty.com'], 'lockoutTime': [b'0'],
 'objectCategory': [b'CN=Person,CN=Schema,CN=Configuration,DC=synad,DC=synerty,DC=com'],
 'dSCorePropagationData': [b'20190606130621.0Z', b'20190606130016.0Z',
                           b'20170506090346.0Z', b'16010101000000.0Z'],
 'lastLogonTimestamp': [b'132042996806397639']}
"""

import logging
from typing import List
from typing import Optional
from typing import Tuple

import ldap
from twisted.cred.error import LoginFailed

from peek_core_user._private.PluginNames import userPluginTuplePrefix
from peek_core_user._private.storage import LdapSetting
from peek_core_user._private.storage.InternalUserTuple import InternalUserTuple
from peek_core_user._private.tuples.LdapLoggedInUserTuple import (
    LdapLoggedInUserTuple,
)
from peek_core_user.tuples.constants.UserAuthTargetEnum import (
    UserAuthTargetEnum,
)

logger = logging.getLogger(__name__)


def checkLdapAuth(
    username: str,
    password: str,
    ldapSetting: LdapSetting,
    userUuid: Optional[str],
) -> Tuple[List[str], LdapLoggedInUserTuple]:
    try:
        conn = ldap.initialize(ldapSetting.ldapUri)
        conn.protocol_version = 3
        conn.set_option(ldap.OPT_REFERRALS, 0)

        # make the connection
        conn.simple_bind_s(
            "%s@%s" % (username.split("@")[0], ldapSetting.ldapDomain), password
        )
        logger.info(
            "User=%s, Connected to LDAP server %s",
            username,
            ldapSetting.ldapDomain,
        )

        if userUuid:
            ldapFilter = (
                "(&(objectCategory=person)(objectClass=user)(objectSid=%s))"
                % userUuid
            )
        else:
            ldapFilter = (
                "(&(objectCategory=person)(objectClass=user)(sAMAccountName=%s))"
                % username.split("@")[0]
            )
        logger.debug("User=%s, LDAP user query: %s", username, ldapFilter)

        dcParts = ",".join(
            ["DC=%s" % part for part in ldapSetting.ldapDomain.split(".")]
        )

        ldapBases = []
        if ldapSetting.ldapOUFolders:
            ldapBases += _makeLdapBase(
                ldapSetting.ldapOUFolders, username, "OU"
            )
        if ldapSetting.ldapCNFolders:
            ldapBases += _makeLdapBase(
                ldapSetting.ldapCNFolders, username, "CN"
            )

        if not ldapBases:
            logger.debug(
                "User=%s, LDAP OU and/or CN search paths must be set.", username
            )
            raise LoginFailed(
                "LDAPAuth: LDAP OU and/or CN search paths must be set."
            )

        userDetails = None
        for ldapBase in ldapBases:
            ldapBase = "%s,%s" % (ldapBase, dcParts)
            logger.debug(
                "User=%s, Searching in LDAP Base: %s, for LDAP Filter: %s",
                username,
                ldapBase,
                ldapFilter,
            )

            try:
                # Example Base: 'CN=atuser1,CN=Users,DC=synad,DC=synerty,DC=com'
                userDetails = conn.search_st(
                    ldapBase, ldap.SCOPE_SUBTREE, ldapFilter, None, 0, 10
                )

                if userDetails:
                    break

                logger.debug(
                    "User=%s, Checking next, user was not found in: %s",
                    username,
                    ldapBase,
                )

            except ldap.NO_SUCH_OBJECT:
                logger.warning(
                    "User=%s, CN or OU doesn't exist : %s", username, ldapBase
                )

    except ldap.NO_SUCH_OBJECT:
        logger.info(
            "User=%s, was not found in any LDAP bases, NO_SUCH_OBJECT", username
        )
        raise LoginFailed(
            "LDAPAuth: A user with username %s was not found, ask admin to "
            "check Peek logs" % username
        )

    except ldap.INVALID_CREDENTIALS:
        logger.info(
            "User=%s, provided an incorrect username or password, INVALID_CREDENTIALS"
        )
        raise LoginFailed(
            "LDAPAuth: Username or password is incorrect for %s" % username
        )

    if not userDetails:
        logger.info(
            "User=%s, was not found in any LDAP bases, 'not userDetails'",
            username,
        )
        raise LoginFailed(
            "LDAPAuth: User %s doesn't belong to the correct CN/OUs" % username
        )

    userDetails = userDetails[0][1]

    distinguishedName = userDetails.get("distinguishedName")[0].decode()
    primaryGroupId = userDetails.get("primaryGroupID")[0].decode()
    objectSid = userDetails.get("objectSid")[0]
    # python-ldap doesn't include key `memberOf` in search result
    #  if the user doesn't belong to any groups.
    memberOfSet = set(userDetails.get("memberOf", []))

    decodedSid = _decodeSid(objectSid)
    primaryGroupSid = (
        "-".join(decodedSid.split("-")[:-1]) + "-" + primaryGroupId
    )

    ldapFilter = "(objectSid=%s)" % primaryGroupSid
    logger.debug(
        "User=%s, Primary group details LDAP filter: %s", username, ldapFilter
    )
    primGroupDetails = conn.search_st(
        dcParts, ldap.SCOPE_SUBTREE, ldapFilter, None, 0, 10
    )
    memberOfSet.add(primGroupDetails[0][1].get("distinguishedName")[0])

    # find all it's groups and groups of those groups
    # The magic number in this filter allows us to fetch the groups of
    # a group.
    ldapFilter = (
        "(&(objectCategory=group)(member:1.2.840.113556.1.4.1941:=%s))"
        % (_escapeParensForLdapFilter(distinguishedName),)
    )
    logger.debug(
        "User=%s, Using recursive groups filter: %s", username, ldapFilter
    )
    logger.info("Fetching groups from the LDAP server for user %s", username)
    groupDetails = conn.search_st(
        ",".join(distinguishedName.split(",")[1:]),
        ldap.SCOPE_SUBTREE,
        ldapFilter,
        None,
        0,
        10,
    )

    if groupDetails:
        for group in groupDetails:
            groupMemberOf = group[1].get("memberOf", [])
            memberOfSet.update(groupMemberOf)

    groups = []
    for memberOf in memberOfSet:
        group = memberOf.decode().split(",")[0]
        if "=" in group:
            group = group.split("=")[1]
        groups.append(group)

    logger.debug("User %s, is a member of groups: %s", username, groups)

    userTitle = None
    if userDetails.get("displayName"):
        userTitle = userDetails["displayName"][0].decode()

    email = None
    if userDetails.get("userPrincipalName"):
        email = userDetails["userPrincipalName"][0].decode()

    if not userUuid:
        userUuid = _decodeSid(objectSid)

    if ldapSetting.ldapGroups:
        ldapGroups = set([s.strip() for s in ldapSetting.ldapGroups.split(",")])

        logger.debug(
            "User=%s, Checking if user is a member of groups: %s",
            username,
            groups,
        )

        if not ldapGroups & set(groups):
            logger.info(
                "User=%s, is not a member of any authorised group, 'not ldapGroups & set(groups)'",
                username,
            )
            raise LoginFailed(
                "User %s is not a member of an authorised group" % username
            )

        logger.debug(
            "User=%s, is a member of specified groups. Proceeding with login",
            username,
        )

    ldapLoggedInUser = LdapLoggedInUserTuple(
        username=username,
        userTitle=userTitle,
        userUuid=userUuid,
        email=email,
        ldapName=ldapSetting.ldapTitle,
        objectSid=objectSid,
        ldapDomain=ldapSetting.ldapDomain,
    )

    return list(groups), ldapLoggedInUser


def _decodeSid(sid: [bytes]) -> str:
    strSid = "S-"
    sid = iter(sid)

    # Byte 0 is the revision
    revision = next(sid)
    strSid += "%s" % (revision,)

    # Byte 1 is the count of sub-authorities
    countSubAuths = next(sid)

    # Byte 2-7 (big endian) form the 48-bit authority code
    bytes27 = [next(sid) for _ in range(2, 8)]
    authority = int.from_bytes(bytes27, byteorder="big")
    strSid += "-%s" % (authority,)

    for _ in range(countSubAuths):
        # Each is 4 bytes (32-bits) in little endian
        subAuthBytes = [next(sid) for _ in range(4)]
        subAuth = int.from_bytes(subAuthBytes, byteorder="little")
        strSid += "-%s" % (subAuth,)

    return strSid


def _escapeParensForLdapFilter(value: str) -> str:
    """Escape parenthesis () in a string

    Escape special characters in a string to be able to use it as a value
    in an LDAP filter. `(` are replaced with \28 and `)` are replaced
    with \29 and so on.

    Reference: https://tools.ietf.org/search/rfc2254#page-5

    :return: Escaped string
    """
    # The \ character must always be escaped first
    value = value.replace("\\", "\\5C")

    value = value.replace("(", "\\28")
    value = value.replace(")", "\\29")
    value = value.replace("*", "\\2A")
    value = value.replace("\0", "\\00")
    return value


def _makeLdapBase(ldapFolders, userName, propertyName):
    try:
        ldapBases = []
        for folder in ldapFolders.split(","):
            folder = folder.strip()
            if not folder:
                continue

            parts = []
            for part in folder.split("/"):
                part = part.strip()
                if not part:
                    continue
                parts.append("%s=%s" % (propertyName, part))

            ldapBases.append(",".join(reversed(parts)))

        return ldapBases

    except Exception as e:
        logger.error(
            "Login failed for %s, failed to parse LDAP %s Folders setting",
            propertyName,
            userName,
        )

        logger.exception(e)

        raise LoginFailed(
            "An internal error occurred, ask admin to check Attune logs"
        )
