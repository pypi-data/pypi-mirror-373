import logging

from vortex.Payload import Payload
from vortex.PayloadEnvelope import PayloadEnvelope
from vortex.sqla_orm.OrmCrudHandler import OrmCrudHandler

from peek_core_user._private.PluginNames import userPluginFilt
from peek_core_user._private.storage.Setting import OTP_NUMBER_OF_OPTIONS
from peek_core_user._private.storage.Setting import OTP_NUMBER_OF_WORDS
from peek_core_user._private.storage.Setting import OTP_VALID_SECONDS
from peek_core_user._private.storage.Setting import oneTimePasscodeSetting
from peek_core_user._private.tuples.OtpSettingTuple import OtpSettingTuple

logger = logging.getLogger(__name__)

# This dict matches the definition in the Admin angular app.
filtKey = {"key": "admin.Edit.OtpSetting"}
filtKey.update(userPluginFilt)


# This is the CRUD hander
class __CrudHandler(OrmCrudHandler):

    def createDeclarative(self, session, payloadFilt):
        return [self._getDeclarativeById(session, None)]

    def _getDeclarativeById(self, session, id_=None):
        settings = oneTimePasscodeSetting(session)
        return OtpSettingTuple(
            otpNumberOfWords=settings[OTP_NUMBER_OF_WORDS],
            otpNumberOfCandidates=settings[OTP_NUMBER_OF_OPTIONS],
            otpValidSeconds=settings[OTP_VALID_SECONDS],
        )

    def _update(self, session, tuples, payloadFilt) -> PayloadEnvelope:
        # Update the OTP settings in the database
        settings = oneTimePasscodeSetting(session)
        settings[OTP_NUMBER_OF_WORDS] = tuples[0].otpNumberOfWords
        settings[OTP_NUMBER_OF_OPTIONS] = tuples[0].otpNumberOfCandidates
        settings[OTP_VALID_SECONDS] = tuples[0].otpValidSeconds

        # Commit the changes
        session.commit()

        returnTuples = self._getDeclarativeById(session)
        # Return the updated settings
        return Payload(tuples=returnTuples).makePayloadEnvelope(result=True)


# This method creates an instance of the handler class.
def makeOtpSettingsHandler(tupleObservable, dbSessionCreator):
    handler = __CrudHandler(
        dbSessionCreator, OtpSettingTuple, filtKey, retreiveAll=True
    )

    return handler
