import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import Column
from sqlalchemy import orm
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.sql.sqltypes import Integer
from sqlalchemy.sql.sqltypes import String
from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_core_device.tuples.DeviceInfoTuple import DeviceInfoTuple
from .DeclarativeBase import DeclarativeBase
from ..PluginNames import deviceTuplePrefix
from ...tuples.DeviceGpsLocationTuple import DeviceGpsLocationTuple

logger = logging.getLogger(__name__)


@addTupleType
class DeviceInfoTable(DeclarativeBase, Tuple):
    """DeviceInfoTable

    This table stores information about devices.

    """

    __tablename__ = "DeviceInfo"
    __tupleType__ = deviceTuplePrefix + "DeviceInfoTable"

    TYPE_FIELD_IOS = DeviceInfoTuple.TYPE_FIELD_IOS
    TYPE_FIELD_ANDROID = DeviceInfoTuple.TYPE_FIELD_ANDROID
    TYPE_FIELD_WEB = DeviceInfoTuple.TYPE_FIELD_WEB
    TYPE_OFFICE_WEB = DeviceInfoTuple.TYPE_OFFICE_WEB
    TYPE_DESKTOP_WINDOWS = DeviceInfoTuple.TYPE_DESKTOP_WINDOWS
    TYPE_DESKTOP_MACOS = DeviceInfoTuple.TYPE_DESKTOP_MACOS

    DEVICE_OFFLINE = DeviceInfoTuple.DEVICE_OFFLINE
    DEVICE_ONLINE = DeviceInfoTuple.DEVICE_ONLINE
    DEVICE_BACKGROUND = DeviceInfoTuple.DEVICE_BACKGROUND

    id = Column(Integer, primary_key=True)
    description = Column(String(100), nullable=False, unique=True)
    deviceId = Column(String(50), nullable=False, unique=True)
    deviceType = Column(String(20), nullable=False)
    deviceToken = Column(String(50), nullable=False, unique=True)
    appVersion = Column(String(15), nullable=False)
    updateVersion = Column(String(15))  # Null means it hasn't updated
    lastOnline = Column(DateTime(True))
    lastUpdateCheck = Column(DateTime(True))
    createdDate = Column(DateTime(True), nullable=False)
    deviceStatus = Column(Integer, nullable=False, server_default="0")
    isEnrolled = Column(Boolean, nullable=False, server_default="0")
    isOfflineCacheEnabled = Column(Boolean, nullable=False, server_default="0")
    lastBandwidthMetric = Column(Integer, nullable=True)
    currentLocation: DeviceGpsLocationTuple = TupleField()
    lastCacheUpdate: Optional[datetime] = TupleField()
    loggedInUser: Optional[str] = TupleField()
    lastDeviceIp = Column(String(15), nullable=True, server_default="")
    mdmDeviceName = Column(String(), nullable=True)
    mdmDeviceSerialNumber = Column(String(), nullable=True)
    mdmDeviceAssetId = Column(String(), nullable=True)
    mdmDeviceAllocatedTo = Column(String(), nullable=True)

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)

    def toTuple(
        self,
        currentLocationTuple: DeviceGpsLocationTuple = None,
        lastCacheCheck: Optional[datetime] = None,
        loggedInUser: Optional[str] = None,
    ):
        return self.toTupleStatic(
            self, currentLocationTuple, lastCacheCheck, loggedInUser
        )

    @staticmethod
    def toTupleStatic(
        table: "DeviceInfoTable",
        currentLocationTuple: Optional[DeviceGpsLocationTuple] = None,
        lastCacheCheck: Optional[datetime] = None,
        loggedInUser: Optional[str] = None,
    ):
        return DeviceInfoTuple(
            description=table.description,
            deviceId=table.deviceId,
            deviceType=table.deviceType,
            deviceToken=table.deviceToken,
            appVersion=table.appVersion,
            updateVersion=table.updateVersion,
            lastOnline=table.lastOnline,
            lastUpdateCheck=table.lastUpdateCheck,
            createdDate=table.createdDate,
            deviceStatus=table.deviceStatus,
            isEnrolled=table.isEnrolled,
            isOfflineCacheEnabled=table.isOfflineCacheEnabled,
            lastBandwidthMetric=table.lastBandwidthMetric,
            currentLocation=currentLocationTuple,
            lastCacheCheck=lastCacheCheck,
            loggedInUser=loggedInUser,
            lastDeviceIp=table.lastDeviceIp,
            mdmDeviceName=table.mdmDeviceName,
            mdmDeviceSerialNumber=table.mdmDeviceSerialNumber,
            mdmDeviceAssetId=table.mdmDeviceAssetId,
            mdmDeviceAllocatedTo=table.mdmDeviceAllocatedTo,
        )
