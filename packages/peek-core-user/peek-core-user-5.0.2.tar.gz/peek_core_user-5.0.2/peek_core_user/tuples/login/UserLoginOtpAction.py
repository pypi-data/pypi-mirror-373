from vortex.Tuple import addTupleType, TupleField
from vortex.TupleAction import TupleActionABC

from peek_core_user._private.PluginNames import userPluginTuplePrefix


@addTupleType
class UserLoginOtpAction(TupleActionABC):
    __tupleType__ = userPluginTuplePrefix + "UserLoginOtpAction"

    userName: str = TupleField()
