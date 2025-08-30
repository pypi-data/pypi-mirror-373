import logging
from collections import defaultdict
from datetime import datetime
from typing import List
from typing import Optional

from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.DeferUtil import vortexLogFailure
from vortex.Tuple import Tuple
from vortex.TupleAction import TupleActionABC

from peek_core_device._private.server.controller.NotifierController import (
    NotifierController,
)
from peek_core_device._private.storage.DeviceInfoTable import DeviceInfoTable
from peek_core_device._private.tuples.OfflineCacheCombinedStatusTuple import (
    OfflineCacheCombinedStatusTuple,
)
from peek_core_device._private.tuples.OfflineCacheStatusAction import (
    OfflineCacheStatusAction,
)
from peek_core_device._private.tuples.OfflineCacheLoaderStatusTuple import (
    OfflineCacheLoaderStatusTuple,
)
from peek_core_device._private.tuples.UpdateOfflineCacheSettingAction import (
    UpdateOfflineCacheSettingAction,
)

logger = logging.getLogger(__name__)


class OfflineCacheController:
    def __init__(self, dbSessionCreator):
        self._dbSessionCreator = dbSessionCreator
        self._notifierController = None

        self._lastUpdateByDeviceToken = {}
        self._lastStatusEncodedPayloadByDeviceToken: dict[str, str] = {}

    def setNotificationController(self, notifierController: NotifierController):
        self._notifierController = notifierController

    def lastCacheUpdate(self, deviceToken: str) -> Optional[datetime]:
        return self._lastUpdateByDeviceToken.get(deviceToken)

    def lastCacheStatusEncodedPayload(self, deviceToken: str) -> str:
        return self._lastStatusEncodedPayloadByDeviceToken.get(deviceToken)

    def shutdown(self):
        self._lastUpdateByDeviceToken = {}

    def processTupleAction(self, tupleAction: TupleActionABC) -> List[Tuple]:
        if isinstance(tupleAction, UpdateOfflineCacheSettingAction):
            d = self._processOfflineCacheSettingUpdate(tupleAction)
            d.addErrback(vortexLogFailure, logger)
            return []

        if isinstance(tupleAction, OfflineCacheStatusAction):
            d = self._processOfflineCacheStatusUpdate(tupleAction)
            d.addErrback(vortexLogFailure, logger)
            return []

    @deferToThreadWrapWithLogger(logger)
    def _processOfflineCacheSettingUpdate(
        self, action: UpdateOfflineCacheSettingAction
    ) -> List[Tuple]:
        """Process Offline Cache Update

        :rtype: Deferred
        """
        ormSession = self._dbSessionCreator()
        try:
            # There should only be one item that exists if it exists.
            deviceInfo = (
                ormSession.query(DeviceInfoTable)
                .filter(DeviceInfoTable.id == action.deviceInfoId)
                .one()
            )

            # There should one be one
            deviceInfo.isOfflineCacheEnabled = action.offlineCacheEnabled

            ormSession.commit()

            self._notifierController.notifyDeviceOfflineCacheSetting(
                deviceToken=deviceInfo.deviceToken
            )

        finally:
            # Always close the session after we create it
            ormSession.close()

    @deferToThreadWrapWithLogger(logger)
    def _processOfflineCacheStatusUpdate(
        self, action: OfflineCacheStatusAction
    ) -> List[Tuple]:
        # lastDate = min([s.lastCheckDate for s in action.loaderStatusList])
        self._lastUpdateByDeviceToken[
            action.deviceToken
        ] = action.lastCachingStartDate

        self._lastStatusEncodedPayloadByDeviceToken[
            action.deviceToken
        ] = action.encodedCombinedTuplePayload

        self._notifierController.notifyOfflineCacheCombinedStatusTuple(
            deviceToken=action.deviceToken
        )
