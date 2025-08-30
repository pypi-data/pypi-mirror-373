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

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import orm
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.schema import Index
from vortex.Tuple import Tuple
from vortex.Tuple import addTupleType

from peek_core_user._private.PluginNames import userPluginTuplePrefix
from peek_core_user._private.storage.DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)


@addTupleType
class InternalUserGroupTuple(DeclarativeBase, Tuple):
    """Internal User Group Tuple

    This table stores the relationships between the users and the groups.

    """

    __tupleType__ = userPluginTuplePrefix + "InternalUserGroupTuple"
    __tablename__ = "InternalUserGroup"

    userId = Column(
        Integer,
        ForeignKey("InternalUser.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    groupId = Column(
        Integer,
        ForeignKey("InternalGroup.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    __table_args__ = (
        Index("idx_InternalUserGroup_map", userId, groupId, unique=True),
    )

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)
