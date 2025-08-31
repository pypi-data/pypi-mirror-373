import logging
from typing import Union

from sqlalchemy import desc
from twisted.internet.defer import inlineCallbacks

from peek_core_device._private.server.controller.OfflineCacheController import (
    OfflineCacheController,
)
from peek_core_device._private.storage.DeviceInfoTable import DeviceInfoTable
from peek_core_device._private.storage.GpsLocationTable import GpsLocationTable
from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)


class DeviceInfoTableTupleProvider(TuplesProviderABC):
    def __init__(
        self,
        ormSessionCreator,
        offlineCacheController: OfflineCacheController,
        userApi,
    ):
        from peek_core_user.server.UserApiABC import UserApiABC

        self._ormSessionCreator = ormSessionCreator
        self._offlineCacheController = offlineCacheController
        self._userApi: UserApiABC = userApi

    @inlineCallbacks
    def makeVortexMsg(
        self, filt: dict, tupleSelector: TupleSelector
    ) -> Union[Deferred, bytes]:
        from peek_core_user.tuples.UserLoggedInInfoTuple import (
            UserLoggedInInfoTuple,
        )

        # noinspection PyTypeChecker
        loggedInUsers: list[UserLoggedInInfoTuple] = (
            yield self._userApi.infoApi.userLoggedInInfo()
        )

        return (
            yield self._makeVortexMsgDeferred(
                filt, tupleSelector, loggedInUsers
            )
        )

    @deferToThreadWrapWithLogger(logger)
    def _makeVortexMsgDeferred(
        self, filt: dict, tupleSelector: TupleSelector, loggedInUsers
    ) -> Union[Deferred, bytes]:
        deviceId = tupleSelector.selector.get("deviceId")
        userByDeviceToken = {
            o.deviceToken: f"{o.userTitle}\n({o.userName})"
            for o in loggedInUsers
        }

        ormSession = self._ormSessionCreator()
        try:
            query = (
                ormSession.query(DeviceInfoTable, GpsLocationTable)
                .outerjoin(GpsLocationTable)
                .order_by(desc(DeviceInfoTable.lastOnline))
            )

            if deviceId is not None:
                query = query.filter(DeviceInfoTable.deviceId == deviceId)

            # Add the current location to each DeviceInfo row
            tuples = []
            for deviceInfoTableRow, gpsLocationTableRow in query.all():
                deviceInfoTableRow.currentLocation = gpsLocationTableRow
                deviceInfoTableRow.lastCacheCheck = (
                    self._offlineCacheController.lastCacheUpdate(
                        deviceInfoTableRow.deviceToken
                    ),
                )
                deviceInfoTableRow.loggedInUser = userByDeviceToken.get(
                    deviceInfoTableRow.deviceToken
                )
                tuples.append(deviceInfoTableRow)

            # Create the vortex message
            return (
                Payload(filt, tuples=tuples).makePayloadEnvelope().toVortexMsg()
            )

        finally:
            ormSession.close()
