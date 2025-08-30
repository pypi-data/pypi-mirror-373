from typing import Callable

from abc import ABCMeta, abstractmethod
from twisted.internet.defer import Deferred

from peek_core_user.tuples.login.UserLoginAction import UserLoginAction
from peek_core_user.tuples.login.UserLoginResponseTuple import (
    UserLoginResponseTuple,
)
from peek_core_user.tuples.login.UserLogoutAction import UserLogoutAction
from peek_core_user.tuples.login.UserLogoutResponseTuple import (
    UserLogoutResponseTuple,
)
from peek_core_user.tuples.login.UserLoginAuthMethodAction import (
    UserLoginAuthMethodAction,
)
from peek_core_user.tuples.login.UserLoginOtpAction import UserLoginOtpAction

UserPostLoginHookCallable = Callable[[UserLoginResponseTuple], Deferred]

UserPostLogoutHookCallable = Callable[[UserLogoutResponseTuple], Deferred]


class UserLoginApiABC(metaclass=ABCMeta):
    @abstractmethod
    def logout(
        self, logoutTuple: UserLogoutAction
    ) -> Deferred:  # [UserLogoutResponseTuple]:
        """Logout

        :param logoutTuple
        """

    @abstractmethod
    def login(
        self, loginTuple: UserLoginAction
    ) -> Deferred:  # [UserLoginResponseTuple]:
        """Login

        :param loginTuple
        """

    @abstractmethod
    def queryUserLoginAuthMethod(
        self, userLoginAuthMethod: UserLoginAuthMethodAction
    ) -> Deferred:
        """query for user authentication method

        :param userLoginAuthMethod
        :return: UserLoginAuthMethodResponseTuple
        """

    @abstractmethod
    def loginRequestOtp(self, userLoginOtpAction: UserLoginOtpAction):
        """Offer one-time password challenge for user authentication

        :param userLoginOtpAction
        :return: UserLoginOtpResponseTuple
        """
