from peek_core_device._private.PluginNames import deviceFilt
from peek_core_device._private.PluginNames import deviceObservableName
from peek_core_device._private.server.controller.OfflineCacheController import (
    OfflineCacheController,
)
from peek_core_device._private.server.tuple_providers.ClientSettingsTupleProvider import (
    ClientSettingsTupleProvider,
)
from peek_core_device._private.server.tuple_providers.DeviceGpsLocationTupleProvider import (
    DeviceGpsLocationTupleProvider,
)
from peek_core_device._private.server.tuple_providers.DeviceInfoTableTupleProvider import (
    DeviceInfoTableTupleProvider,
)
from peek_core_device._private.server.tuple_providers.DeviceInfoTupleProvider import (
    DeviceInfoTupleProvider,
)
from peek_core_device._private.server.tuple_providers.DeviceUpdateTupleProvider import (
    DeviceUpdateTupleProvider,
)
from peek_core_device._private.server.tuple_providers.OfflineCacheCombinedStatusTupleProvider import (
    OfflineCacheCombinedStatusTupleProvider,
)
from peek_core_device._private.server.tuple_providers.OfflineCacheSettingTupleProvider import (
    OfflineCacheSettingTupleProvider,
)
from peek_core_device._private.storage.DeviceInfoTable import DeviceInfoTable
from peek_core_device._private.storage.DeviceUpdateTuple import (
    DeviceUpdateTuple,
)
from peek_core_device._private.tuples.ClientSettingsTuple import (
    ClientSettingsTuple,
)
from peek_core_device._private.tuples.OfflineCacheCombinedStatusTuple import (
    OfflineCacheCombinedStatusTuple,
)
from peek_core_device._private.tuples.OfflineCacheSettingTuple import (
    OfflineCacheSettingTuple,
)
from peek_core_device.tuples.DeviceGpsLocationTuple import (
    DeviceGpsLocationTuple,
)
from peek_core_device.tuples.DeviceInfoTuple import DeviceInfoTuple
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler


def makeTupleDataObservableHandler(
    ormSessionCreator, offlineCacheController: OfflineCacheController, userApi
):
    """ " Make Tuple Data Observable Handler

    This method creates the observable object, registers the tuple providers and then
    returns it.

    :param userApi:
    :param ormSessionCreator: A function that returns a SQLAlchemy session when called
    :param offlineCacheController:

    :return: An instance of :code:`TupleDataObservableHandler`

    """
    tupleObservable = TupleDataObservableHandler(
        observableName=deviceObservableName, additionalFilt=deviceFilt
    )

    # Register TupleProviders here
    tupleObservable.addTupleProvider(
        DeviceUpdateTuple.tupleName(),
        DeviceUpdateTupleProvider(ormSessionCreator),
    )

    tupleObservable.addTupleProvider(
        DeviceInfoTuple.tupleName(),
        DeviceInfoTupleProvider(
            ormSessionCreator, offlineCacheController, userApi
        ),
    )

    tupleObservable.addTupleProvider(
        OfflineCacheCombinedStatusTuple.tupleName(),
        OfflineCacheCombinedStatusTupleProvider(offlineCacheController),
    )

    tupleObservable.addTupleProvider(
        DeviceInfoTable.tupleName(),
        DeviceInfoTableTupleProvider(
            ormSessionCreator, offlineCacheController, userApi
        ),
    )

    tupleObservable.addTupleProvider(
        ClientSettingsTuple.tupleName(),
        ClientSettingsTupleProvider(ormSessionCreator),
    )

    tupleObservable.addTupleProvider(
        DeviceGpsLocationTuple.tupleName(),
        DeviceGpsLocationTupleProvider(ormSessionCreator),
    )

    tupleObservable.addTupleProvider(
        OfflineCacheSettingTuple.tupleName(),
        OfflineCacheSettingTupleProvider(ormSessionCreator),
    )

    return tupleObservable
