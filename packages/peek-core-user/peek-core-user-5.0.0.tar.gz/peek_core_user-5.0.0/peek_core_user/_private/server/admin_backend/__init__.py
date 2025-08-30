from peek_core_user._private.server.admin_backend.InternalGroupTableHandler import (
    makeInternalGroupTableHandler,
)
from peek_core_user._private.server.admin_backend.LdapSettingsHandler import (
    makeLdapSettingeHandler,
)
from peek_core_user._private.server.admin_backend.OtpSettingsHandler import (
    makeOtpSettingsHandler,
)
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from .InternalUserTableHandler import makeInternalUserTableHandler
from .SettingPropertyHandler import makeSettingPropertyHandler


def makeAdminBackendHandlers(
    tupleObservable: TupleDataObservableHandler, dbSessionCreator
):
    yield makeInternalUserTableHandler(tupleObservable, dbSessionCreator)
    yield makeInternalGroupTableHandler(tupleObservable, dbSessionCreator)

    yield makeSettingPropertyHandler(tupleObservable, dbSessionCreator)

    yield makeLdapSettingeHandler(tupleObservable, dbSessionCreator)
    yield makeOtpSettingsHandler(tupleObservable, dbSessionCreator)
