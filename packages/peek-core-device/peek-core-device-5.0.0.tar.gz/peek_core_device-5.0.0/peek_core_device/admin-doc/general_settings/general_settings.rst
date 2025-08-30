.. _core_device_configuration:

Configuration
-------------

Configure the General Settings to configure the device plugin.

:Field Enrollment Enabled: Devices will enroll for the Field Service.

:Slow Network Threshold: This is the network speed threshold for
    offline caching. When a device exceeds the threshold, offline caching
    is disabled on the device for 5 minutes.

:Offline Cache Refresh Seconds: This is the period of time a device will have
    its offline cache refreshed.

:Office Enrollemt Enabled: Devices will enroll for the Office Service.

:Offline Master Switch Enabled: This allows an Administrator to enable or
    disable offline caching for all devices registered for caching.

:Device Auto Enrollment: Devices will be automatically enrolled without the
    intervention of an Administrator.

:Abort Retry Seconds: The time the offline caching state machine will wait
    for caching to abort before moving on to the next state.

:Pause Timeout Seconds: The time the offline caching state machine will wait
    for caching to pause before moving on to the next state.

:Check Bandwidth Seconds: The time in seconds that the iOS Field Application
    checks the connection bandwidth to the server.

:Send Statistics to Server Seconds: The time in seconds which the iOS Field
    application sends the caching statistics to the server.

.. image:: general_settings.png
    :align: center

