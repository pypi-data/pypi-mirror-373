from vortex.Tuple import addTupleType, TupleField, Tuple

from peek_core_user._private.PluginNames import userPluginTuplePrefix


@addTupleType
class UserLoginAuthMethodResponseTuple(Tuple):
    __tupleType__ = userPluginTuplePrefix + "UserLoginAuthMethodResponseTuple"

    AUTH_METHOD_NONE = -1
    AUTH_METHOD_OTP = 0
    AUTH_METHOD_PASSWORD = 1

    userName: str = TupleField()
    authMethod: str = TupleField(defaultValue=AUTH_METHOD_NONE)
