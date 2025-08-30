import hashlib
import json
import logging
import random
from datetime import datetime
from datetime import timedelta
from smtplib import SMTPException
from typing import List
from typing import NamedTuple
from typing import Tuple

import pytz
from peek_core_email.server.EmailApiABC import EmailApiABC
from twisted.cred.error import LoginFailed
from twisted.internet import reactor
from twisted.internet import task
from twisted.internet.defer import Deferred
from twisted.internet.defer import inlineCallbacks
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from peek_core_device.server.DeviceApiABC import DeviceApiABC
from peek_core_user._private.server.api.UserFieldHookApi import UserFieldHookApi
from peek_core_user._private.server.api.UserInfoApi import UserInfoApi
from peek_core_user._private.server.auth_connectors.AuthABC import AuthABC
from peek_core_user._private.server.auth_connectors.CryptoUtil import (
    decryptAES256GCM,
)
from peek_core_user._private.server.auth_connectors.InternalAuth import (
    InternalAuth,
)
from peek_core_user._private.server.auth_connectors.LdapAuth import LdapAuth
from peek_core_user._private.server.util.OtpWordlist import OTP_WORDLIST
from peek_core_user._private.storage.InternalUserTuple import InternalUserTuple
from peek_core_user._private.storage.Setting import OTP_NUMBER_OF_OPTIONS
from peek_core_user._private.storage.Setting import OTP_NUMBER_OF_WORDS
from peek_core_user._private.storage.Setting import OTP_VALID_SECONDS
from peek_core_user._private.storage.Setting import oneTimePasscodeSetting
from peek_core_user._private.storage.UserLoggedIn import UserLoggedIn
from peek_core_user._private.tuples.LoggedInUserStatusTuple import (
    LoggedInUserStatusTuple,
)
from peek_core_user._private.tuples.UserLoggedInTuple import UserLoggedInTuple
from peek_core_user.server.UserDbErrors import (
    UserIsNotLoggedInToThisDeviceError,
)
from peek_core_user.tuples.login.UserLoginAction import UserLoginAction
from peek_core_user.tuples.login.UserLoginAuthMethodAction import (
    UserLoginAuthMethodAction,
)
from peek_core_user.tuples.login.UserLoginAuthMethodResponseTuple import (
    UserLoginAuthMethodResponseTuple,
)
from peek_core_user.tuples.login.UserLoginOtpAction import UserLoginOtpAction
from peek_core_user.tuples.login.UserLoginOtpResponseTuple import (
    UserLoginOtpResponseTuple,
)
from peek_core_user.tuples.login.UserLoginResponseTuple import (
    UserLoginResponseTuple,
)
from peek_core_user.tuples.login.UserLogoutAction import UserLogoutAction
from peek_core_user.tuples.login.UserLogoutResponseTuple import (
    UserLogoutResponseTuple,
)
from peek_plugin_base.storage.DbConnection import DbSessionCreator

logger = logging.getLogger(__name__)

USER_ALREADY_LOGGED_ON_KEY = "pl-user.USER_ALREADY_LOGGED_ON"
DEVICE_ALREADY_LOGGED_ON_KEY = "pl-user.DEVICE_ALREADY_LOGGED_ON_KEY"


class _ForceLogout:
    def __init__(self, userUuid, deviceToken):
        self._userUuid = userUuid
        self._deviceToken = deviceToken

    def forceDbLogout(self, ormSession):
        ormSession.query(UserLoggedIn).filter(
            UserLoggedIn.userUuid == self._userUuid
        ).filter(UserLoggedIn.deviceToken == self._deviceToken).delete(
            synchronize_session=False
        )

    def notify(self, clientTupleObservable):
        clientTupleObservable.notifyOfTupleUpdate(
            TupleSelector(
                UserLoggedInTuple.tupleType(),
                selector=dict(deviceToken=self._deviceToken),
            )
        )


class _GeneratedOtp(NamedTuple):
    otp: list[str]
    otpOptions: list[str]
    forMobile: str
    otpValidFrom: datetime
    otpValidTo: datetime


class LoginLogoutController:
    def __init__(
        self,
        deviceApi: DeviceApiABC,
        emailApi: EmailApiABC,
        dbSessionCreator: DbSessionCreator,
    ):
        self._deviceApi: DeviceApiABC = deviceApi
        self._emailApi: EmailApiABC = emailApi
        self._fieldServiceHookApi: UserFieldHookApi = None
        self._infoApi: UserInfoApi = None
        self._dbSessionCreator: DbSessionCreator = dbSessionCreator
        self._clientTupleObservable: TupleDataObservableHandler = None
        self._adminTupleObservable: TupleDataObservableHandler = None

    def setup(
        self,
        clientTupleObservable,
        adminTupleObservable,
        hookApi: UserFieldHookApi,
        infoApi: UserInfoApi,
    ):
        self._clientTupleObservable = clientTupleObservable
        self._adminTupleObservable = adminTupleObservable
        self._fieldServiceHookApi = hookApi
        self._infoApi = infoApi

    def shutdown(self):
        self._clientTupleObservable = None
        self._fieldServiceHookApi = None
        self._infoApi = None

    @inlineCallbacks
    def _checkPassAsync(
        self,
        userName,
        encryptedPassword,
        passphrase,
        isFieldService: bool,
        userUuid=None,
    ) -> Tuple[List[str], InternalUserTuple]:
        if not encryptedPassword or not passphrase:
            raise LoginFailed("Password is empty")

        password = decryptAES256GCM(
            encodedBase64String=encryptedPassword, passphrase=passphrase
        )

        # TODO Make the client tell us if it's for office or field

        lastException = None

        forService = AuthABC.FOR_SERVICE_OFFICE
        if isFieldService:
            forService = AuthABC.FOR_SERVICE_FIELD

        internalAuth = InternalAuth(self._dbSessionCreator)
        authSettings = yield internalAuth.getAuthSettings()

        try:
            # TRY INTERNAL IF ITS ENABLED
            if (
                forService == AuthABC.FOR_SERVICE_FIELD
                and authSettings.internalFieldEnabled
            ):
                return (
                    yield internalAuth.checkPassAsync(
                        userName, password, forService
                    )
                )

            if (
                forService == AuthABC.FOR_SERVICE_OFFICE
                and authSettings.internalOfficeEnabled
            ):
                return (
                    yield internalAuth.checkPassAsync(
                        userName, password, forService
                    )
                )

        except Exception as e:
            lastException = e

        # TRY LDAP IF ITS ENABLED
        try:
            ldapAuth = LdapAuth(self._dbSessionCreator)
            if authSettings.ldapAuthEnabled:
                return (
                    yield ldapAuth.checkPassAsync(
                        userName, password, forService, userUuid
                    )
                )

        except Exception as e:
            lastException = e

        if lastException:
            # ALWAYS pause for 2 seconds if there is a failure, it could be
            # an incorrect password attempt.
            # noinspection PyTypeChecker
            yield task.deferLater(reactor, 2, lambda: None)
            raise lastException

        raise Exception(
            "No authentication handlers are enabled, enable one in settings"
        )

    @deferToThreadWrapWithLogger(logger)
    def _logoutInDb(
        self, logoutTuple: UserLogoutAction, raiseNotLoggedInException=True
    ):
        """
        Returns Deferred[UserLogoutResponseTuple]
        """

        ormSession = self._dbSessionCreator()
        try:
            # Check if the user is actually logged into this device.
            qry = (
                ormSession.query(UserLoggedIn)
                .filter(UserLoggedIn.userName == logoutTuple.userName.lower())
                .filter(UserLoggedIn.deviceToken == logoutTuple.deviceToken)
            )

            if qry.count() == 0:
                if raiseNotLoggedInException:
                    raise UserIsNotLoggedInToThisDeviceError(
                        logoutTuple.userName
                    )
                else:
                    return

            ormSession.delete(qry.one())
            ormSession.commit()

        finally:
            ormSession.close()

    @inlineCallbacks
    def logout(self, logoutTuple: UserLogoutAction) -> Deferred:
        """Logout

        :param logoutTuple: The tuple containing the information to process
                                for the logout.

        :return A deferred that fires with List[UserLogoutResponseTuple]
        """

        deviceDescription = yield self._deviceApi.deviceDescription(
            logoutTuple.deviceToken
        )

        response = UserLogoutResponseTuple(
            userName=logoutTuple.userName,
            deviceToken=logoutTuple.deviceToken,
            deviceDescription=deviceDescription,
            acceptedWarningKeys=logoutTuple.acceptedWarningKeys,
            succeeded=True,
        )

        if logoutTuple.isFieldService:
            # Give the hooks a chance to fail the logout
            yield self._fieldServiceHookApi.callLogoutHooks(response)

        # If there are no problems, proceed with the logout.
        try:
            if response.succeeded:
                yield self._logoutInDb(logoutTuple)

        finally:
            # Delay this, otherwise the user gets kicked off before getting
            # the nice success message
            reactor.callLater(
                0.05, self._sendLogoutUpdate, logoutTuple.deviceToken
            )

        self._adminTupleObservable.notifyOfTupleUpdateForTuple(
            LoggedInUserStatusTuple.tupleType()
        )

        return response

    def _sendLogoutUpdate(self, deviceToken: str):
        self._clientTupleObservable.notifyOfTupleUpdate(
            TupleSelector(
                UserLoggedInTuple.tupleType(),
                selector=dict(deviceToken=deviceToken),
            )
        )

    @inlineCallbacks
    def _loginInDb(self, loginTuple: UserLoginAction):
        blockMultipleLogins = loginTuple.isFieldService

        userDetail = yield self._infoApi.user(loginTuple.userName.lower())

        # This will login from the internal user if one already exists or
        # login from LDAP and create a user if an internal does not exist
        groups, _ = yield self._checkPassAsync(
            userName=loginTuple.userName.lower(),
            encryptedPassword=loginTuple.password,
            passphrase=loginTuple.uuid,
            isFieldService=blockMultipleLogins,
            userUuid=userDetail.userUuid if userDetail else None,
        )
        return (yield self._loginInDbInThread(loginTuple, groups))

    @deferToThreadWrapWithLogger(logger)
    def _loginInDbInThread(
        self, loginTuple: UserLoginAction, groups: list[str]
    ):
        """
        Returns Deferred[UserLoginResponseTuple]

        """

        userName = loginTuple.userName
        acceptedWarningKeys = set(loginTuple.acceptedWarningKeys)
        deviceToken = loginTuple.deviceToken
        vehicle = loginTuple.vehicleId
        isFieldService = loginTuple.isFieldService
        blockMultipleLogins = isFieldService

        forceLogouter = None

        responseTuple = UserLoginResponseTuple(
            userName=userName,
            userToken="Not implemented",
            succeeded=False,
            acceptedWarningKeys=loginTuple.acceptedWarningKeys,
            vehicleId=loginTuple.vehicleId,
        )

        if not deviceToken:
            raise Exception("peekToken must be supplied")

        thisDeviceDescription = self._deviceApi.deviceDescriptionBlocking(
            deviceToken
        )

        userDetail = self._infoApi.userBlocking(userName.lower())

        # check user group and user password
        ormSession = self._dbSessionCreator()
        try:
            if not userDetail:
                logger.debug(
                    "Peek LoginLogoutController: "
                    " _loginInDbInThread,"
                    " Login failed, userDetail is None",
                    userName,
                )
                responseTuple.setFailed()
                return responseTuple

            userKey = userDetail.userKey
            userUuid = userDetail.userUuid
            loginTuple.userName = userDetail.userName
            responseTuple.userName = userDetail.userName
            responseTuple.userDetail = userDetail

            # Find any current login sessions
            userLoggedIn = (
                ormSession.query(UserLoggedIn)
                .filter(UserLoggedIn.userUuid == userUuid)
                .filter(UserLoggedIn.isFieldLogin == isFieldService)
                .all()
            )
            userLoggedIn = userLoggedIn[0] if userLoggedIn else None

            loggedInElsewhere = (
                ormSession.query(UserLoggedIn)
                .filter(UserLoggedIn.deviceToken != deviceToken)
                .filter(UserLoggedIn.userUuid == userUuid)
                .filter(UserLoggedIn.isFieldLogin == isFieldService)
                .all()
            )

            if blockMultipleLogins and len(loggedInElsewhere) not in (0, 1):
                raise Exception(
                    "Found more than 1 ClientDevice for"
                    + (" token %s" % deviceToken)
                )

            loggedInElsewhere = (
                loggedInElsewhere[0] if loggedInElsewhere else None
            )

            sameDevice = userLoggedIn and loggedInElsewhere is None

            # If the user is logged in, but not to this client device, raise exception
            if blockMultipleLogins and userLoggedIn and not sameDevice:
                if USER_ALREADY_LOGGED_ON_KEY in acceptedWarningKeys:
                    forceLogouter = _ForceLogout(
                        userUuid, loggedInElsewhere.deviceToken
                    )

                    forceLogouter.forceDbLogout(ormSession)

                    userLoggedIn = False

                else:
                    otherDeviceDescription = (
                        self._deviceApi.deviceDescriptionBlocking(
                            loggedInElsewhere.deviceToken
                        )
                    )

                    # This is false if the logged in device has been removed from
                    # enrollment
                    if otherDeviceDescription:
                        responseTuple.setFailed()
                        responseTuple.addWarning(
                            USER_ALREADY_LOGGED_ON_KEY,
                            "User %s is already logged in, on device %s"
                            % (userName, otherDeviceDescription),
                        )

                        return responseTuple

                    # Else, The old device has been deleted,
                    # Just let them login to the same device.

                    forceLogouter = _ForceLogout(
                        loggedInElsewhere.userUuid,
                        loggedInElsewhere.deviceToken,
                    )
                    forceLogouter.forceDbLogout(ormSession)

            # If we're logging into the same device, but already logged in
            if sameDevice:  # Logging into the same device
                sameDeviceDescription = (
                    self._deviceApi.deviceDescriptionBlocking(
                        userLoggedIn.deviceToken
                    )
                )

                responseTuple.deviceToken = userLoggedIn.deviceToken
                responseTuple.deviceDescription = sameDeviceDescription
                responseTuple.succeeded = True
                return responseTuple

            anotherUserOnThatDevice = (
                ormSession.query(UserLoggedIn)
                .filter(UserLoggedIn.deviceToken == deviceToken)
                .filter(UserLoggedIn.userUuid != userUuid)
                .all()
            )

            if anotherUserOnThatDevice:
                anotherUserOnThatDevice = anotherUserOnThatDevice[0]
                if DEVICE_ALREADY_LOGGED_ON_KEY in acceptedWarningKeys:
                    forceLogouter = _ForceLogout(
                        anotherUserOnThatDevice.userUuid,
                        anotherUserOnThatDevice.deviceToken,
                    )
                    forceLogouter.forceDbLogout(ormSession)

                else:
                    responseTuple.setFailed()
                    responseTuple.addWarning(
                        DEVICE_ALREADY_LOGGED_ON_KEY,
                        "User %s is currently logged into this device : %s"
                        % (
                            anotherUserOnThatDevice.userName,
                            thisDeviceDescription,
                        ),
                    )

                    return responseTuple

            # Create the user logged in entry
            newUser = UserLoggedIn(
                userTitle=userDetail.userTitle,
                userName=userName.lower(),
                userKey=userKey.lower(),
                userUuid=userUuid,
                loggedInDateTime=datetime.now(pytz.utc),
                deviceToken=deviceToken,
                vehicle=vehicle,
                isFieldLogin=isFieldService,
                loggedInWithGroups=json.dumps(groups if groups else []),
            )
            ormSession.add(newUser)

            # Update the last login details
            updatedInternalUser = (
                ormSession.query(InternalUserTuple)
                .filter(InternalUserTuple.userUuid == userUuid)
                .one()
            )
            updatedInternalUser.lastLoginDate = datetime.now(pytz.utc)
            updatedInternalUser.lastLoginDeviceToken = deviceToken

            ormSession.commit()

            # Respond with a successful login
            responseTuple.deviceToken = deviceToken
            responseTuple.deviceDescription = thisDeviceDescription
            responseTuple.succeeded = True
            return responseTuple

        finally:
            ormSession.close()

            if forceLogouter:
                forceLogouter.notify(self._clientTupleObservable)

    @inlineCallbacks
    def login(self, loginTuple: UserLoginAction):
        """
        Returns Deferred[UserLoginResponseTuple]

        """
        loginResponse = None
        try:
            loginResponse = yield self._loginInDb(loginTuple)

            if loginTuple.isFieldService:
                yield self._fieldServiceHookApi.callLoginHooks(loginResponse)

        # except UserAlreadyLoggedInError as e:
        #     pass
        #
        # except DeviceAlreadyLoggedInError as e:
        #     pass
        #
        # except UserIsNotLoggedInToThisDeviceError as e:
        #     pass

        except Exception as e:
            # Log the user out again if the hooks fail
            logoutTuple = UserLogoutAction(
                userName=loginTuple.userName, deviceToken=loginTuple.deviceToken
            )

            # Force logout, we don't care if it works or not.
            try:
                yield self._logoutInDb(
                    logoutTuple, raiseNotLoggedInException=False
                )
            except UserIsNotLoggedInToThisDeviceError:
                pass

            logger.debug(f"User login failed: {e}")
            raise e

        self._clientTupleObservable.notifyOfTupleUpdate(
            TupleSelector(
                UserLoggedInTuple.tupleType(),
                selector=dict(deviceToken=loginTuple.deviceToken),
            )
        )

        self._adminTupleObservable.notifyOfTupleUpdateForTuple(
            LoggedInUserStatusTuple.tupleType()
        )

        return loginResponse

    def _forceLogout(self, ormSession, userUuid, deviceToken):
        ormSession.query(UserLoggedIn).filter(
            UserLoggedIn.userUuid == userUuid
        ).filter(UserLoggedIn.deviceToken == deviceToken).delete(
            synchronize_session=False
        )

        self._clientTupleObservable.notifyOfTupleUpdate(
            TupleSelector(
                UserLoggedInTuple.tupleType(),
                selector=dict(deviceToken=deviceToken),
            )
        )

    @inlineCallbacks
    def queryUserLoginAuthMethod(
        self, userLoginAuthMethodAction: UserLoginAuthMethodAction
    ) -> Deferred[UserLoginAuthMethodResponseTuple]:
        responseTuple = UserLoginAuthMethodResponseTuple()
        responseTuple.userName = userLoginAuthMethodAction.userName

        if not userLoginAuthMethodAction.AUTH_FOR_FIELD:
            responseTuple.authMethod = (
                UserLoginAuthMethodResponseTuple.AUTH_METHOD_PASSWORD
            )
        else:
            internalAuth = InternalAuth(self._dbSessionCreator)
            isOtpAvailableForUser = (
                yield internalAuth.checkIfUserAbleToLoginWithOtp(
                    userName=userLoginAuthMethodAction.userName
                )
            )

            if isOtpAvailableForUser:
                responseTuple.authMethod = (
                    UserLoginAuthMethodResponseTuple.AUTH_METHOD_OTP
                )
            else:
                responseTuple.authMethod = (
                    UserLoginAuthMethodResponseTuple.AUTH_METHOD_PASSWORD
                )

        return responseTuple

    @deferToThreadWrapWithLogger(logger)
    def _generateOtpForUser(self, userName: str) -> _GeneratedOtp:
        startTime = datetime.now(pytz.utc)

        ormSession = self._dbSessionCreator()
        try:
            settings = oneTimePasscodeSetting(ormSession)

            validDuration = timedelta(seconds=settings[OTP_VALID_SECONDS])  # z
            otpOptions = list(
                sorted(
                    random.sample(OTP_WORDLIST, settings[OTP_NUMBER_OF_OPTIONS])
                )
            )  # y
            otp = list(
                random.sample(otpOptions, settings[OTP_NUMBER_OF_WORDS])
            )  # x
            _otpCode = "_".join(otp)
            otpCodeHashed = hashlib.sha256(_otpCode.encode()).hexdigest()

            from sqlalchemy import func
            user = (
                ormSession.query(InternalUserTuple)
                .filter(func.lower(InternalUserTuple.userName) == userName.lower())
                .one()
            )

            user.oneTimePasscode = otpCodeHashed
            user.oneTimePasscodeExpiry = datetime.now(pytz.utc) + validDuration

            ormSession.commit()

            return _GeneratedOtp(
                otp=otp,
                otpOptions=otpOptions,
                forMobile=str(user.mobile),
                otpValidTo=startTime + validDuration,
                otpValidFrom=startTime,
            )

        finally:
            ormSession.close()

    @inlineCallbacks
    def _sendOtpCode(self, generatedOtp: _GeneratedOtp):
        otpStr = " ".join(generatedOtp.otp)
        mobile = generatedOtp.forMobile
        smsMessage = (
            f'Your one-time password is "{otpStr}". '
            f"Do not share this with anyone. "
            f"We will never contact you to request this code."
        )
        yield self._emailApi.sendSms(mobile, contents=smsMessage)

    @inlineCallbacks
    def loginRequestOtp(self, userLoginOtpAction: UserLoginOtpAction):
        responseTuple = UserLoginOtpResponseTuple()
        responseTuple.userName = userLoginOtpAction.userName

        internalAuth = InternalAuth(self._dbSessionCreator)
        isOtpAvailableForUser = (
            yield internalAuth.checkIfUserAbleToLoginWithOtp(
                userName=userLoginOtpAction.userName
            )
        )
        if not isOtpAvailableForUser:
            responseTuple.otpRequestStatus = (
                UserLoginOtpResponseTuple.STATUS_OTP_REQUEST_REJECTED
            )
        else:
            responseTuple.otpRequestStatus = (
                UserLoginOtpResponseTuple.STATUS_OTP_REQUEST_ACCEPTED
            )
            generatedOtp = yield self._generateOtpForUser(
                userName=userLoginOtpAction.userName
            )
            responseTuple.otpOptions = generatedOtp.otpOptions
            responseTuple.otpValidFrom = generatedOtp.otpValidFrom
            responseTuple.otpValidTo = generatedOtp.otpValidTo

            try:
                yield self._sendOtpCode(generatedOtp)

            except Exception as e:
                raise SMTPException(
                    "failed to send SMS, "
                    "please contact Peek Admin for email settings."
                )
        return responseTuple
