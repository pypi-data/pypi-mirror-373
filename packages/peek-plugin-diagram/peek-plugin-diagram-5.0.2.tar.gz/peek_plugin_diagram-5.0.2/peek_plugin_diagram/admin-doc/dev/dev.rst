.. _diagram_dev:

===========
Development
===========


Other Plugin Integration
------------------------

This section describes how the nativescript and web frontends hang together.

Web Integration
***************

The peek-plugin-diagram doesn't have it's own UI, It exposes an angular component
<peek-plugin-diagram>, this is then used by a plugin built to display a specific
diagram that's been loaded. GIS, SCADA, DMS, etc.

Both nativescript and the web version integrate with the <peek-plugin-diagram> component
with the same API. The <peek-plugin-diagram> component then talks to the canvas,
See the "NativeScript Support" section.

The "Diagram" component handles displaying of the toolbars and ItemPopup,
and takes in the "ItemSelect" event.

The "Canvas" component handles the ItemSelect and the Position services

.. image:: web_integration.png

NativeScript Support
********************

The diagram mobile app ONLY comes as a web app.
This section describes how the nativescript support works.

The <pl-diagram-canvas> component is for NativeScript uses the
nativescript-webview-interface ns plugin to achive an integration between
the <peek-plugin-diagram> component and the <pl-diagram-canvas> component.

The web version links these directly and it all runs like normal
in peek / the web browser.

In NativeScript this plugin builds a very straight forward Angular-CLI application
that just serves the <pl-diagram-canvas> web component.
The nativescript-webview-interface allows the nativescript <peek-plugin-diagram>
to talk to the <pl-diagram-canvas> running in the nativescript webview component.

.. image:: ns_integration.png

Other Diagram Integration
*************************

Each plugin that embeds the diagram provides it's own services,
these are more specific to the type of diagram displayed.
For example, the DMS diagram will have service methods to position on equipment,
while the GIS diagram will have service methods for positioning on
latitude + longitude coordinates.

.. image:: other_diagram_integration.png

Structure
---------

This section notes down some less straight forward things that occur in the diagram plugin.

Initialisation
**************

The diagram loads a bunch of cached lists, these include all the lookups
(colours, line styles, etc), coordSet lists, everything but the grids.

Once this loading is done, the canvas notifies the PositionService.isReady observable,
the integrating plugin then calls the PositionService position methods.

.. image:: structure_Initial_load.png

Location Index
**************

When Disp objects are imported, they can have a "key" attribute.
This string is meaningless to the diagram plugin, but it allows other plugins to
reference graphical objects on the diagram.

The peek-plugin-diagram compiles an index of these disp keys,
providing a fast lookup to locate where disp objects with a key are located
and position on them. This index is called the "Location Index"

DispGroup and DispGroupPtr (TODO)
*********************************

A disp group is a group of disps, when the diagram is edited,
this group of disps will look like one object, able to be moved,
or rotated as one object.

DispGroups will be stored at two levels.

-   Level 1 - If the DispGroup is linked to multiple times with-in the ModelSet,
    it's stored in a special template data structure,
    this is loaded into the browser when ever a diagram is displayed.

-   Level 2 - If the DispGroup is unique and referenced by only one place,
    it is compiled into the grid in which it's used.

The level used is determined by the plugin importing the data,
peek-plugin-diagram makes no guesses about this.

DispGroups are linked into the diagram with a "DispGroupPtr".
A DispGroupPtr is it's self a Disp, and as such can belong in a
DispGroup (a group in a group? Why not)

TODO - DispGroups are partially implemented and need to be completed
before the editing feature.

Branches and Stages (TODO)
**************************

The diagram needs a concept of branches and stages.
Branches are an alternate view of a section of the network diagram,
these could represent a proposed change being made, or the lifeclcye of a
change that will occur.

For example:

#.  A branch with one default stage could represent a proposed patch to the diagram.

#.  A branch with multiple stages could represent the diagram at different proposed states
    of a change life cycle, as in the steps of a distribution switching job.

Branches are the concept of an alternate view, stages represent a difference to
the diagram.

Branches can cover multiple grids, and they will be compiled into each grid.

A branch relates to a coordSet, – There should probably be a bit more design in
this so a branch can relate to a model set, and effect multiple coord sets.

Editing (TODO)
**************

Editing is basically creating a branch and a stage from the browser, then providing a download button.
Editing needs to have access to a "Display Group", so new items can be dropped on the diagram.

Colour Overwrite (TODO)
***********************

Other plugins can overwrite the colours of display items by providing a list of keys
and their corresponding new background and line colours.

The idea here is to allow a trace plugin to tell the diagram to highlight conductors
and switches along a trace path.

Developing
**********

How to develop with a different backend of data.

#.  For native script, this is easy. Delete the app, and redeploy it.
    When the app asks for the websocket port,
    send it to the peek_office_service that has the data. EG 10.2.56.135

#.  For web :

.. image:: dev_with_diagram_data_backend.png

