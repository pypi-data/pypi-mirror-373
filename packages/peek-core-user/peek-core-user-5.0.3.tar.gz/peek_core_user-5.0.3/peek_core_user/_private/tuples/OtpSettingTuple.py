import logging

from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_core_user._private.PluginNames import userPluginTuplePrefix

logger = logging.getLogger(__name__)


@addTupleType
class OtpSettingTuple(Tuple):
    """OtpSetting

    This table stores settings to generate one-time passwords

    """

    __tupleType__ = userPluginTuplePrefix + "OtpSettingTuple"

    id: int = TupleField()
    otpNumberOfWords: int = TupleField()
    otpNumberOfCandidates: int = TupleField()
    otpValidSeconds: int = TupleField()
