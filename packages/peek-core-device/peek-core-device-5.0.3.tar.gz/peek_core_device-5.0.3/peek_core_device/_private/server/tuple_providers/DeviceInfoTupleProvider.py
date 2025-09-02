import logging
from typing import Union

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


class DeviceInfoTupleProvider(TuplesProviderABC):
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

        loggedInUsers: list[
            UserLoggedInInfoTuple
        ] = yield self._userApi.infoApi.userLoggedInInfo()

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
        userByDeviceToken = {o.deviceToken: o.userName for o in loggedInUsers}

        ormSession = self._ormSessionCreator()
        try:
            query = ormSession.query(
                DeviceInfoTable, GpsLocationTable
            ).outerjoin(GpsLocationTable)

            if deviceId is not None:
                query = query.filter(DeviceInfoTable.deviceId == deviceId)

            tuples = []
            for deviceInfoTableRow, gpsLocationTableRow in query.all():
                tuples.append(
                    deviceInfoTableRow.toTuple(
                        currentLocationTuple=gpsLocationTableRow,
                        lastCacheCheck=self._offlineCacheController.lastCacheUpdate(
                            deviceInfoTableRow.deviceToken
                        ),
                        loggedInUser=userByDeviceToken.get(
                            deviceInfoTableRow.deviceToken
                        ),
                    )
                )

            # Create the vortex message
            return (
                Payload(filt, tuples=tuples).makePayloadEnvelope().toVortexMsg()
            )

        finally:
            ormSession.close()
