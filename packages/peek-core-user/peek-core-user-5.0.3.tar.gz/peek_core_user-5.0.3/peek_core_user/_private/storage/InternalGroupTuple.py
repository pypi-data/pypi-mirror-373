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
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import orm
from vortex.Tuple import Tuple
from vortex.Tuple import addTupleType

from peek_core_user._private.PluginNames import userPluginTuplePrefix
from peek_core_user._private.storage.DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)


@addTupleType
class InternalGroupTuple(DeclarativeBase, Tuple):
    """Group Table

    This table contains the user plugin groups, for the internal directory.

    """

    __tupleType__ = userPluginTuplePrefix + "InternalGroupTuple"
    __tablename__ = "InternalGroup"

    id = Column(Integer, primary_key=True, autoincrement=True)
    groupName = Column(String, unique=True, nullable=False)
    groupTitle = Column(String, unique=True, nullable=False)

    importHash = Column(String)

    __table_args__ = (Index("idx_InternalGroupTable_importHash", importHash),)

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)
