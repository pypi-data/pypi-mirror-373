from datetime import datetime

from peek_core_user._private.PluginNames import userPluginTuplePrefix
from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType


@addTupleType
class UserLoginOtpResponseTuple(Tuple):
    __tupleType__ = userPluginTuplePrefix + "UserLoginOtpResponseTuple"

    STATUS_OTP_REQUEST_ACCEPTED = 0
    STATUS_OTP_REQUEST_REJECTED = 1

    otpRequestStatus: int = TupleField()
    userName: str = TupleField()
    otpOptions: list[str] = TupleField()
    otpValidFrom: datetime = TupleField()
    otpValidTo: datetime = TupleField()
