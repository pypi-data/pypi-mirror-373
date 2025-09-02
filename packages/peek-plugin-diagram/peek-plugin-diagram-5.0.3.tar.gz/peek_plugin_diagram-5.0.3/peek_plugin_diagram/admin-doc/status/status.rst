.. _diagram_admin_status:

======
Status
======

The Diagram compilers can be monitored from the **Status** tab on the Peek Admin UI.

The compilers are :

:Display Compiler: This compiler compiles the display items into json and calculates
    the grids that they belong to.

:Grid Compiler: This compiler compiles the display items into the grid chunks.

:Location Compiler: This compiler compiles the data used to locate display items by
    their key into hash buckets.

----

The labels have the following meaning :

:Is Running: Is the compiler running

:Queue Size: The number of chunks that the worker is currently compiling.

:Total Processed: The total number of chunks sent to the worker for compile,
    since the last Peek Server restart.

:Last Error: The last error for this compiler.

----

.. image:: status.png
