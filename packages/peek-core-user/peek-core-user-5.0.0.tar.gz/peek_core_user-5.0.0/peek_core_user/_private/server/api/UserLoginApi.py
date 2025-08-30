import logging

from twisted.internet.defer import Deferred

from peek_core_device.server.DeviceApiABC import DeviceApiABC
from peek_core_user._private.server.controller.LoginLogoutController import (
    LoginLogoutController,
)
from peek_core_user.server.UserLoginApiABC import UserLoginApiABC
from peek_core_user.tuples.login.UserLoginAction import UserLoginAction
from peek_core_user.tuples.login.UserLogoutAction import UserLogoutAction
from peek_core_user.tuples.login.UserLoginAuthMethodAction import (
    UserLoginAuthMethodAction,
)
from peek_core_user.tuples.login.UserLoginOtpAction import UserLoginOtpAction

logger = logging.getLogger(__name__)


class UserLoginApi(UserLoginApiABC):
    #: A reference to the core device plugins API
    _deviceApi: DeviceApiABC

    def __init__(self):
        self._loginLogoutController = None

    def setStartValues(self, loginLogoutController: LoginLogoutController):
        self._loginLogoutController = loginLogoutController

    def shutdown(self):
        self._loginLogoutController = None

    def logout(self, logoutTuple: UserLogoutAction) -> Deferred:
        return self._loginLogoutController.logout(logoutTuple)

    def login(self, loginTuple: UserLoginAction) -> Deferred:
        return self._loginLogoutController.login(loginTuple)

    def queryUserLoginAuthMethod(
        self, userLoginAuthMethod: UserLoginAuthMethodAction
    ) -> Deferred:
        return self._loginLogoutController.queryUserLoginAuthMethod(
            userLoginAuthMethod
        )

    def loginRequestOtp(self, userLoginOtpAction: UserLoginOtpAction):
        return self._loginLogoutController.loginRequestOtp(userLoginOtpAction)
