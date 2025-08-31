Overview
--------

The following sections describe the parts of the Peek Diagram plugin.

Importers
`````````

The diagram needs to be populated with data, this task is carried out by other plugins.

The loader plugins populate the Lookups, Display items an Display LiveDB Links.

Multiple importers can import into the one coordinate set, the Diagram will merge these
data sets into one diagram.

Importers can import a group of display items that are positioned at any level, at any
position and on any coord set with in a model.

Client Cache
````````````

For performance reasons, all data for the Peek Diagram is cached in memory in the client
service.

.. warning:: Manual database changes outside of Peek Admin will
    require a restart of the Peek Client.

If you find you are making manual changes outside of Peek Admin on a regular
basis, please log a enhancement issue with Synerty.

Display Items
`````````````

Display items, or shapes in the Peek Diagram are shapes, either simple shapes such as lines and text,
or a group of simple shapes.

The Diagram supports the following shapes:

:Text: Simple - Draw text on the canvas.

:Polyline: Simple - Draw a line on the canvas, this line can have multiple segments.

:Polygon: Simple - Draw a polygon on the canvas, this is a closed polyline.
    The polygon can be filled with a colour and can be used
    to create rectangles, squares, and more complex shapes with any number of sides.

:Ellipse: Simple - An ellipse can be used to create circles, ellipses, or any kind of arc
    based on a start and stop angle.
    Ellipses can be filled with colour.

:Group: A display group is a group of simple shapes, with a group key.
    Groups can be drawn multiple times on the canvas.

:Group Pointer: A group pointer specifices the group key and positoon to draw a group
    on the canvas.

All display items can be assigned a key and additional data that can be leveraged by
other plugins. Using the DocDB to store the additional data is prefered.

Display LiveDB Links
````````````````````

Display items properties can have links to values the LiveDB plugin.

This allows values in the LiveDB plugin to change the colour, text value, etc of a shape
displayed on the diagram.

The Peek Diagram is aware of the LiveDB values that are currently being viewed by all
viewers and continuously updates the LiveDB plugin with this list as "Priority Items".


Model Set
`````````

The diagram can have multiple isolated data/model sets in it.
Each model set has it's own set of lookups, coordinate sets and display items.

Coordinate Set
``````````````

A coordinate set is where the display items live. One or more coordinate sets live
within each model set, using the lookups within the model set.

Lookups
```````

The Peek Diagram has several lookup types. Lookups are used to store display details
for each display item.

This provides easier global changes and a smaller display item object.


:Color: This lookup provides the colour of the shape

:Text Style: This lookup provides the font size, font type, font style, etc.

:Line Style: This lookup provides the line style, dashed or solid, and thickness.

:Level: This lookup describes the level the display item is on.
        Levels are assigned minimum and maximum zoom ranges, shapes in this level will
        only be visible when the canvas zoom is within this range.
        This is known as "Declutter".

:Layer: This lookup describes the layer that the display item is on.
        Layers can be toggled on and off via the user interface, showing and hiding
        diferent display items, for example, turning off boundary lines, etc.



Grids
`````

A Grid in the diagram represents a square area of the diagram. Display Items are grouped
and stored in the grids that they are shown in. If a display item covers multiple grids
then the display item will be duplicated in each grid that it's displayed in.

Z Grids
```````

A coordinate set specifices a range of Z-Grids. Z grids is the term used for compiling
different grids for different zoom ranges.

The zoom ranges / Z Grids are configured per a coordinate set.

Z grids decrease in size as you zoom in, so that the UI is loading a minimum number of
grids for each zoom range.

Grids will only show display items that can be seen at the maximum zoom for that grid.
the real screen size of the shape is calculated and if it's too small at the grids
maximum zoom, it's not included in the grid.

Display items includeded in grids are also filtered based on the Level lookup,
if the declutter level won't show the shape within the grids zoom range, the shape
is not included in the grids data.

This provides both loading and rendering performance.

.. image:: diagram_layers.jpg

Display / Grid Compiling
````````````````````````

The Diagram processes all the dispaly items provided by the importer plugins.
This allows the diagram to optimise the grids, for rendering in browsers. It also
provides the ability to merge multiple display sources into one canvas.

Display items are first compiled into a terse json format, and allocated the grid
keys that they will be represented in.

A second stage compiler then efficiontly packs the display items into highly compressed
grids.

Replacing a chunk of data in the canvas is the most effeciont way to process the display
items in the user interface. This has a much lower cost then updating just the display
items that have changed within a grid when multiple changes are occuring.


Location Index
``````````````

The location index follows Peeks
`Index Blueprint <https://bitbucket.org/synerty/peek-plugin-index-blueprint>`_

Given a key of a display item, the location index will return the positions that the
display item is located at within a model set.


Branches
````````

Branches represent a change to the diagram. These branches can be created via the UI
or via the server backend importers.

Deltas
~~~~~~

A delta is a change that belongs to a branch. Some examples of deltas are :

* Change the colour
* Move display items
* Delete display items
* Create display items
* Change display item properties.

