import logging

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import orm
from vortex.Tuple import Tuple
from vortex.Tuple import addTupleType

from peek_core_user._private.PluginNames import userPluginTuplePrefix
from peek_core_user._private.storage.DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)


@addTupleType
class LdapSetting(DeclarativeBase, Tuple):
    """LdapSetting

    This table stores connections and settings to LDAP servers

    """

    __tupleType__ = userPluginTuplePrefix + "LdapSettingTuple"
    __tablename__ = "LdapSetting"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ldapTitle = Column(String, nullable=False, unique=True)
    ldapDomain = Column(String, nullable=False)
    ldapUri = Column(String, nullable=False)
    ldapCNFolders = Column(String, nullable=True)
    ldapOUFolders = Column(String, nullable=True)
    ldapGroups = Column(String, nullable=True)

    adminEnabled = Column(Boolean, nullable=False, server_default="0")
    desktopEnabled = Column(Boolean, nullable=False, server_default="0")
    mobileEnabled = Column(Boolean, nullable=False, server_default="0")

    agentHost = Column(String, nullable=True)

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)
