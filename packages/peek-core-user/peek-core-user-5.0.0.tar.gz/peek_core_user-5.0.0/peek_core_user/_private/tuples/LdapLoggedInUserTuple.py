import logging

from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_core_user._private.PluginNames import userPluginTuplePrefix

logger = logging.getLogger(__name__)


@addTupleType
class LdapLoggedInUserTuple(Tuple):
    """Ldap Logged In User Tuple

    Aggregates the result of a successfully logged in user from LDAP

    """

    __tupleType__ = userPluginTuplePrefix + "LdapLoggedInUserTuple"

    username: str = TupleField()
    userTitle: str = TupleField()
    userUuid: str = TupleField()
    email: str = TupleField()
    ldapName: str = TupleField()
    objectSid: str = TupleField()
    ldapDomain: str = TupleField()
