from datetime import datetime
from typing import Dict
from typing import List
from typing import Optional

from peek_core_user._private.PluginNames import userPluginTuplePrefix
from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType


@addTupleType
class UserDetailTuple(Tuple):
    __tupleType__ = userPluginTuplePrefix + "UserDetailTuple"

    #:  The username / userid of the user, EG C917
    userName: str = TupleField()

    #:  The title of the user, EG 'Chief Wiggum'
    userTitle: str = TupleField()

    #:  An external system user uuid, EG 715903a7ebc14fb0afb00d432676c51c
    userUuid: str = TupleField()

    #:  The mobile number, EG +61 419 123 456
    mobile: Optional[str] = TupleField()

    #:  The email address, EG guy@place.com
    email: Optional[str] = TupleField()

    #:  A list of group names that this user belongs to
    groupNames: List[str] = TupleField()

    #: A field for additional data
    data: Optional[Dict] = TupleField()

    #: user creation stream
    importSource: str = TupleField()

    #:  The last date that the user logged in
    lastLoginDate: Optional[datetime] = TupleField()

    #:  The device token of the last device the user logged in on.
    lastLoginDeviceToken: Optional[str] = TupleField()

    #: user authenticator target - a value from
    #  `peek_core_user.tuples.UserAuthTargetEnum`
    authenticationTarget: str = TupleField()

    @property
    def userKey(self):
        return self.userName.lower()
