from vortex.Tuple import addTupleType, TupleField
from vortex.TupleAction import TupleActionABC

from peek_core_user._private.PluginNames import userPluginTuplePrefix


@addTupleType
class UserLoginAuthMethodAction(TupleActionABC):
    __tupleType__ = userPluginTuplePrefix + "UserLoginAuthMethodAction"

    AUTH_FOR_ADMIN = 1
    AUTH_FOR_OFFICE = 2
    AUTH_FOR_FIELD = 3

    userName: str = TupleField()
    authForService: int = TupleField()
