Admin Tasks
-----------

This section describes how to perform administration tasks for the Peek Diagram.

The database can be updated either via PGAdmin4, or with SQL statements and
:command:`psql`.

Updating Coord Set List
```````````````````````

The coordinate sets can be edited in the database, they are located in the table
 :code:`pl_diagram."ModelCoordSet"`

The fields most often customised are as follows :

:name:  The name of the coordinate set, this is displayed to the user.

:enabled: Is the coordinate set enabled, It's best to delete it if it's not.

:initialPanX: The initial canvas X position when the coordinate set is loaded.

:initialPanY: The initial canvas Y position when the coordinate set is loaded.

:initialZoom: The initial canvas zoom level when the coordinate set is loaded.

Update the values in the table accordingly, then restart the Peek Client service.

.. _diagram_delete_coord_sets:

Deleting Coord Sets
```````````````````

To delete a coordinate set, delete the required coordinate set from the
:code:`pl_diagram."ModelCoordSet"` table.

The delete will cascade to the related tables, this may take some time.

Once the delete is complete, restart the Peek Client service.

Updating Layers
```````````````

Updating the layers is a common admin task when first setting up the diagram.
Since layers can contain display items that are used for debug, or alternate views
such as simulated states, it's important that the right layers are enabled.

Edit the "selectable" and "visible" columns for each layer in the
:code:`pl_diagram."DispLayer"` table.

You have completed updating the table, restart the Peek Client service.


Updating Coord Set Z Grids
``````````````````````````

To optimise the display of the diagram it's important to optimise the
:code:`pl_diagram."ModelCoordSetGridSize"` table for each coordinate set.

This represents the rules used by the Diagram compiler to compile the grids.

Zoom ranges should not overlap.

:min: The minimum zoom level that this Z Grid will be shown at.

:max: The maximum zoom level that this Z Grid will be shown at.

:xGrid: The horizontal size of each grid.

:yGrid: The vertical size of each grid.

:smallestTextSize: Text pixel size at **max** zoom that is smaller than this value
    will not be included in this set of grids.

:smallestShapeSize: Shape pixel size at **max** zoom that is smaller than this value
    will not be included in this set of grids.

After updating the Z Grid sizes, the grids for the coordinate set need to be recompiled.

Setting the Zoom Limits
```````````````````````

This admin task will set the maximum and minimum zoom levels for a world view
in the DMS diagram.

Stop the Peek Services :code:`p_stop.sh`

----

#. Navigate to the :code:`pl.diagram."ModelCoordSet"` table.
#. Update the :code:`minZoom` value for the required world view.
#. update the :code:`maxZoom` value for the required world view.
#. Save the changes.

.. image:: edit_zoom_limit.png

----

Restart the Peek services. :code:`p_restart.sh`

Enabling Markup Support
```````````````````````

This admin task will enable Markup support for a world view.

Stop the Peek Services :code:`p_stop.sh`

----

#. Navigate to :code:`pl_diagram."ModelCoordSet"`
#. Update :code:`editEnabled` to :code:`True`
#. Update :code:`editDefaultColorId` to the default Fault Colour.
#. Update :code:`editDefaultLayerId` to the Default Layer Id.
#. Update :code:`editDefaultLevelId` to the default Level Id.
#. Update :code:`editDefaultLineStyleId` to the default Line Style.
#. Update :code:`editDefaultTextStyleId` to the default Text Style.

.. image:: enable_markup.png

----

Restart the Peek Services :code:`p_restart.sh`

Recompiling Coord Sets
``````````````````````

This admin task will recompile all grids for a given coordinate set.

----

#.  Find the :code:`coordSetId` of the coordinate set to be recompiled.

#.  Stop all peek services

#.  Execute the following SQL replacing :code:`<ID>` with the :code:`coordSetId` ::


        -- Delete the existing grids for this coord set.
        DELETE FROM pl_diagram."GridKeyIndex" WHERE "coordSetId" = <ID>;
        DELETE FROM pl_diagram."GridKeyIndexCompiled" WHERE "coordSetId" = <ID>;
        DELETE FROM pl_diagram."GridKeyCompilerQueue" WHERE "coordSetId" = <ID>;

        -- Queue the display items for re-calculation
        INSERT INTO pl_diagram."DispCompilerQueue" ("dispId")
        SELECT id
        FROM pl_diagram."DispBase"
        WHERE "coordSetId" = <ID>;


#.  Start all Peek services

----

Peek will now rebuild the new grids.


Recompiling Location Index
``````````````````````````

The admin task recompiles the location index for a given model set.

The location data for each display item is stored in one of 8192 hash buckets.
Recompiling the Location Index will rebuild these bash buckets.

Each model set has it's own location index.

.. note:: You should not expect to need to recompile the index.

----

#.  Find the ID of the model set to recompile the location index for.

#.  Stop all peek services

#.  Execute the following, replacing <ID> with the :code:`modeSetId` ::


        -- Delete the existing index data.
        DELETE FROM pl_diagram."LocationIndexCompilerQueue" WHERE "modelSetId" = <ID>;
        DELETE FROM pl_diagram."LocationIndexCompiled" WHERE "modelSetId" = <ID>;

        -- Queue the chunks for compiling
        INSERT INTO pl_diagram."LocationIndexCompilerQueue" ("modelSetId", "indexBucket")
        SELECT DISTINCT "modelSetId", "indexBucket"
        FROM pl_diagram."LocationIndex"
        WHERE "modelSetId" = <ID>;


#.  Start all Peek services

----

Peek will now rebuild the location index.

Edit Settings Tab
-----------------

The compilers can be toggled on an off in the **Edit Settings** Tab.

To Toggle the Compilers on and off
``````````````````````````````````

#. Click on the **Value** to toggle.
#. Click on the **Save** Button.

.. image:: plugin_diagram_edit_settings.png

To Discard your Changes
```````````````````````

Click **Reset** at any time to discard your changed and return the value to the previous saved settings.

.. image:: plugin_diagram_edit_settings_reset.png

Edit Light Mode Colours
------------------------

.. note:: The colour fields only accept hexadecimal colour codes in the form
    #000000

#. Using PSQL, update the blockApiUpdate value and new light colour::

        UPDATE pl_diagram."DispColor"
        SET
        "blockApiUpdate" = TRUE,
        "lightColor" = [New Color]
        WHERE "lightColor" = [Old Color]


#. Restart the Office and Field services.::

        sudo systemctl restart peek_office
        sudo systemctl restart peek_field

.. _set_default_background_colour:

Set the Default Background Colour
---------------------------------

The default background colour in a World View can be set using the following
instruction.

#. Update the Peek database: ::

        UPDATE pl_diagram."ModelCoordSet"
        SET
            "backgroundDarkColor" = '[HEX COLOUR]',
            "backgroundLightColor" = '[HEX COLOUR]'
        WHERE "name" = '[WORLD VIEW NAME]'

#. Restart Peek: ::

        restart_peek.sh

.. note:: The colour fields only accept hexadecimal colour codes in the form
          #000000 and the World View Name is case sensitive.

Enable or Disable Light Mode
----------------------------

From a ssh session:

#. Enter :code:`psql`

#. Update the Peek database: ::

    UPDATE pl_diagram."ModelCoordSet"
    SET
        "lightModeEnabled" = [BOOLEAN]
    WHERE "name" = '[WORLD VIEW NAME]';

#. Restart Peek: ::

    restart_peek.sh

.. note:: TRUE will show the Light Mode button and FALSE will not show the
          Light Mode button in the World View.

Restrict World Views to Active Directory Groups
```````````````````````````````````````````````

World View access can be restricted to specific Active Directory Groups when
Peek is configured for LDAP Authentication. This is done by either adding a
comma separated list of Active Directory groups to the
:code:`userGroupsAllowed` column or :code:`userGroupsDenied` column of the
:code:`pl_diagram.ModeCoordSet` table.

The rules are applied as follows:

If :code:`userGroupsAllowed` is *not* configured, and :code:`userGroupsDenied` is *not* conifgured,
 all users can view the world view.

If :code:`userGroupsAllowed` is configured, and :code:`userGroupsDenied` is *not* configured,
 then only users in :code:`userGroupsAllowed` will be allowed, all other users will be denied.

If :code:`userGroupsAllowed` is *not* configured, and :code:`userGroupsDenied` is configured,
 then only users in :code:`userGroupsDenied` will be denied, all other users will be allowed.

If :code:`userGroupsAllowed` is configured, and :code:`userGroupsDenied` is configured,
 then deny will be applied before allow.

+------------------------+------------------------+-------------------------------------------------------+
| ``userGroupsAllowed``  | ``userGroupsDenied``   | Result                                                |
+========================+========================+=======================================================+
| Not configured         | Not configured         | All users can view the world view.                    |
+------------------------+------------------------+-------------------------------------------------------+
| Configured             | Not configured         | Only users in ``userGroupsAllowed`` will be allowed,  |
|                        |                        | all other users will be denied.                       |
+------------------------+------------------------+-------------------------------------------------------+
| Not configured         | Configured             | Only users in ``userGroupsDenied`` will be denied,    |
|                        |                        | all other users will be allowed.                      |
+------------------------+------------------------+-------------------------------------------------------+
| Configured             | Configured             | Deny will be applied before allow.                    |
+------------------------+------------------------+-------------------------------------------------------+

To configure world views with approved Active Directory Groups:

#. Log into a terminal session as the Peek user.
#. Run

    .. code-block::

        psql <<'EOF'
        INSERT INTO pl_diagram."ModelCoordSet"
        SET "<userGroupAllowed | userGroupDeny>" = '<AD GROUPS>'
        WHERE "name" = '<WORLD VIEW NAME>'
        ;
        EOF

#. Restart Peek