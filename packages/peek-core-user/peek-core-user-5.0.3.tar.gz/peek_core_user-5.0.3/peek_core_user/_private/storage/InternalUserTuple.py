""" 
 *  Copyright Synerty Pty Ltd 2017
 *
 *  MIT License
 *
 *  All rights to this software are reserved by 
 *  Synerty Pty Ltd
 *
"""

import logging

from peek_core_user._private.PluginNames import userPluginTuplePrefix
from peek_core_user._private.storage.DeclarativeBase import DeclarativeBase
from peek_core_user._private.storage.InternalGroupTuple import (
    InternalGroupTuple,
)
from peek_core_user._private.storage.InternalUserGroupTuple import (
    InternalUserGroupTuple,
)
from peek_core_user.tuples.UserDetailTuple import UserDetailTuple
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import orm
from sqlalchemy.orm import relationship
from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

logger = logging.getLogger(__name__)


@addTupleType
class InternalUserTuple(DeclarativeBase, Tuple):
    """Internal

    This table doesn't do anything

    """

    __tupleType__ = userPluginTuplePrefix + "InternalUserTuple"
    __tablename__ = "InternalUser"

    id = Column(Integer, primary_key=True, autoincrement=True)
    userName = Column(String, unique=True, nullable=False)
    userKey = Column(String, unique=True, nullable=True)
    userTitle = Column(String, unique=True, nullable=False)
    userUuid = Column(String, unique=True, nullable=False)
    # `authenticationTarget` is a custom type in postgres, see migration script
    #  43df0e05c728_added_user_import_source.py
    authenticationTarget = Column(String, nullable=False)
    # an arbitrary string of user import source
    importSource = Column(String, nullable=False)

    importHash = Column(String)

    mobile = Column(String)
    email = Column(String)

    oneTimePasscode = Column(String)
    oneTimePasscodeExpiry = Column(DateTime(timezone=True))

    groups = relationship(
        InternalGroupTuple, secondary=InternalUserGroupTuple.__table__
    )

    #: This field is ussed for the admin-app to edit the groups
    groupIds = TupleField()

    lastLoginDate = Column(DateTime(timezone=True))
    lastLoginDeviceToken = Column(String)

    __table_args__ = (Index("idx_InternalUserTable_importHash", importHash),)

    # noinspection PyMissingConstructor
    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)

    def toUserDetailTuple(self):
        return UserDetailTuple(
            userName=self.userName,
            userTitle=self.userTitle,
            userUuid=self.userUuid,
            mobile=self.mobile,
            email=self.email,
            groupNames=None,
            data=None,
            authenticationTarget=self.authenticationTarget,
            importSource=self.importSource,
        )
