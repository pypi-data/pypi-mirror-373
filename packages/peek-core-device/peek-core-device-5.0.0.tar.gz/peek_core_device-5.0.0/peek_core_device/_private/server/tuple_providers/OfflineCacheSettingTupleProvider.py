import logging
from typing import Union

import sqlalchemy
from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_core_device._private.storage.DeviceInfoTable import DeviceInfoTable
from peek_core_device._private.tuples.OfflineCacheSettingTuple import (
    OfflineCacheSettingTuple,
)

logger = logging.getLogger(__name__)


class OfflineCacheSettingTupleProvider(TuplesProviderABC):
    def __init__(self, ormSessionCreator):
        self._ormSessionCreator = ormSessionCreator

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(
        self, filt: dict, tupleSelector: TupleSelector
    ) -> Union[Deferred, bytes]:
        deviceToken = tupleSelector.selector.get("deviceToken")

        ormSession = self._ormSessionCreator()
        try:
            try:
                deviceTuple = (
                    ormSession.query(DeviceInfoTable)
                    .filter(DeviceInfoTable.deviceToken == deviceToken)
                    .one()
                )

            except sqlalchemy.orm.exc.NoResultFound:
                deviceTuple = DeviceInfoTable(isOfflineCacheEnabled=False)

            tuples = [
                OfflineCacheSettingTuple(
                    offlineEnabled=deviceTuple.isOfflineCacheEnabled
                )
            ]

            # Create the vortex message
            return (
                Payload(filt, tuples=tuples).makePayloadEnvelope().toVortexMsg()
            )

        finally:
            ormSession.close()
