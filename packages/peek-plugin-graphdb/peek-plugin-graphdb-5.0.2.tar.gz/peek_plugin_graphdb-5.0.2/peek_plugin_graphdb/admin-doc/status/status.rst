.. _graphdb_admin_status:

======
Status
======

The GraphDB compilers can be monitored from the **Status** tab on the Peek Admin UI.

The compilers are :

:Segment Storage: This compiler compiles the graph segments into the hash buckets.

:Item Key Index: This compiler compiles the graph item keys into the hash buckets.

----

The labels have the following meaning :

:Is Running: Is the compiler running

:Queue Size: The number of chunks that the worker is currently compiling.

:Total Processed: The total number of chunks sent to the worker for compile,
    since the last Peek Server restart.

:Last Error: The last error for this compiler.

----

.. image:: status.png
