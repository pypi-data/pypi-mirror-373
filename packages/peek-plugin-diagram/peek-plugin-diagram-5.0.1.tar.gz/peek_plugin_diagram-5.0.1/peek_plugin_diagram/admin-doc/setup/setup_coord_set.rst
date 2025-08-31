.. _diagram_setup_coord_set:

Setup Coord Set
---------------

This section describes how to configure the various coordinate sets loaded
 into the diagram.


Setup Landing Coord Set
```````````````````````

A landing page can be configured to specify the default coord-set that the diagram will
load when no coord-set is specified.

This config can be set in the :code:`pl_diagram.ModelSet.landingCoordSetId`.
Set this to the ID of the coord-set that should be loaded, then restart the client.


Setup Editing
`````````````
TODO

..
    To get started, configure the plugin from the admin section of Peek Admin.

    ----

    Configure the App Server Settings,
    this connects the connectivity loader to the PowerOn Fusion/Advantage app server.

    .. image:: setup_app_server_settings.png

    ----

    :App Server Hosts: Set the IP of the app server, this will be used for the oracle
        connection.

    :Oracle Username: The user to connect to oracle with.

    :Oracle Password: The password to connect to oracle with.

    ----

    #.  Select the "Edit App Server Settings"

    #.  Fill out the connection details.

    #.  Set the "Enabled" button.

    #.  Click Save

    ----