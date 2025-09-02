import json
import logging
from datetime import datetime
from datetime import timedelta
from pathlib import Path

import pytz
from twisted.internet.task import LoopingCall
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.DeferUtil import vortexLogFailure
from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_core_user._private.PluginNames import userPluginTuplePrefix
from peek_core_user._private.storage.InternalUserTuple import InternalUserTuple
from peek_core_user._private.storage.UserLoggedIn import UserLoggedIn
from peek_plugin_base.LoopingCallUtil import peekCatchErrbackWithLogger

logger = logging.getLogger(__name__)


@addTupleType
class UserMetricsTuple(Tuple):
    __tupleType__ = userPluginTuplePrefix + "UserMetricsTuple"

    lastUpdateDate: datetime = TupleField()

    # User metrics
    totalUsers: int = TupleField()
    loginsLast365Days: int = TupleField()
    loginsLast30Days: int = TupleField()
    loginsLast7Days: int = TupleField()
    loginsLast24Hours: int = TupleField()
    totalLoggedInDevices: int = TupleField()
    totalFieldLogins: int = TupleField()


class MetricsController:
    LOOPING_CALL_PERIOD = 30.0 * 60  # 30 minutes

    def __init__(self, writeDir: Path, ormSessionCreator):
        self._writeDir = writeDir
        self._ormSessionCreator = ormSessionCreator
        self._loopingCall = LoopingCall(
            peekCatchErrbackWithLogger(logger)(self.writeMetrics)
        )

    def start(self):
        d = self._loopingCall.start(self.LOOPING_CALL_PERIOD, now=True)
        d.addErrback(vortexLogFailure, logger, consumeError=True)

    def shutdown(self):
        if self._loopingCall is not None:
            self._loopingCall.stop()
            self._loopingCall = None

    def _maybeNaive(self, dt: datetime | None) -> datetime | None:
        """Convert datetime to UTC if it has a timezone, or assume UTC if naive.

        Args:
            dt: The datetime to convert

        Returns:
            UTC datetime or None if input is None
        """
        if dt is None:
            return None

        if dt.tzinfo is None:
            return dt.replace(tzinfo=pytz.UTC)

        return dt.astimezone(pytz.UTC)

    @deferToThreadWrapWithLogger(logger)
    def writeMetrics(self) -> None:
        """Collect and write system metrics to a JSON file.

        Raises:
            OSError: If there are file permission issues
            psutil.Error: If there are errors collecting system metrics
        """
        try:
            metrics = self._collectMetrics()
            jsonFilePath = self._writeDir / "metrics.json"

            # Convert datetime to string for JSON serialization
            metricsDict = metrics.tupleToRestfulJsonDict()

            with jsonFilePath.open("w") as f:
                json.dump(metricsDict, f, indent=4)

        except Exception as e:
            logger.exception(f"Error writing metrics: {e}")
            raise

    def _collectUserMetrics(self, metrics: UserMetricsTuple) -> None:
        """Collect user-related metrics."""
        ormSession = self._ormSessionCreator()
        try:
            now = datetime.now(pytz.utc)

            # Time thresholds
            oneYearAgo = now - timedelta(days=365)
            oneMonthAgo = now - timedelta(days=30)
            oneWeekAgo = now - timedelta(days=7)
            todayStart = now - timedelta(days=1)

            # Get all users and their last login dates
            users = list(ormSession.query(InternalUserTuple))
            metrics.totalUsers = len(users)

            # Calculate login metrics based on lastLoginDate
            metrics.loginsLast365Days = sum(
                1
                for user in users
                if self._maybeNaive(user.lastLoginDate)
                and self._maybeNaive(user.lastLoginDate) >= oneYearAgo
            )
            metrics.loginsLast30Days = sum(
                1
                for user in users
                if self._maybeNaive(user.lastLoginDate)
                and self._maybeNaive(user.lastLoginDate) >= oneMonthAgo
            )
            metrics.loginsLast7Days = sum(
                1
                for user in users
                if self._maybeNaive(user.lastLoginDate)
                and self._maybeNaive(user.lastLoginDate) >= oneWeekAgo
            )
            metrics.loginsLast24Hours = sum(
                1
                for user in users
                if self._maybeNaive(user.lastLoginDate)
                and self._maybeNaive(user.lastLoginDate) >= todayStart
            )

            # Get current logged in sessions
            loggedInSessions = list(ormSession.query(UserLoggedIn))

            # Count total logged in devices (all active sessions)
            metrics.totalLoggedInDevices = len(loggedInSessions)

            # Count field logins (only one allowed per user)
            metrics.totalFieldLogins = sum(
                1 for session in loggedInSessions if session.isFieldLogin
            )

        finally:
            ormSession.close()

    def _collectMetrics(self) -> UserMetricsTuple:
        """Collect all user metrics and return as a UserMetricsTuple."""
        metrics = UserMetricsTuple(lastUpdateDate=datetime.now(pytz.utc))
        self._collectUserMetrics(metrics)
        return metrics
