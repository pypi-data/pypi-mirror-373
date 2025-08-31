Admin Tasks
-----------

This section describes how to perform administration tasks for the GraphDB plugin.

..
    Trace Config
    ````````````

    The trace configs can be edited by via the admin UI.
    To edit the names, follow this procedure:

    ----

    #.  Open the Peek Admin UI and navigate to the GraphDB plugin.

    #.  Click on the **Edit Property Names** tab

    #.  Update the **Title** column.

    #.  Click save.


    .. image:: admin_task_update_property_name.png

    ----

    The user will see the updated property name when next they view the document.

Recompile Segment Index
```````````````````````

The admin task recompiles the GraphDB Segment Index for a given model set.

The graph segments are stored in one of 8192 hash buckets.
Recompiling the index will rebuild these hash buckets.

Each model set has it's own graph segment index.

.. note:: You should not expect to need to recompile the index.

----

#.  Find the ID of the model set to recompile the index for.

#.  Stop all peek services

#.  Execute the following, replacing <ID> with the :code:`modeSetId` ::


        -- Delete the existing index data.
        DELETE FROM pl_graphdb."GraphDbChunkQueue" WHERE "modelSetId" = <ID>;
        DELETE FROM pl_graphdb."GraphDbEncodedChunk" WHERE "modelSetId" = <ID>;

        -- Queue the chunks for compiling.
        INSERT INTO pl_graphdb."GraphDbChunkQueue" ("modelSetId", "chunkKey")
        SELECT DISTINCT "modelSetId", "chunkKey"
        FROM pl_graphdb."GraphDbSegment"
        WHERE "modelSetId" = <ID>;


#.  Start all Peek services

----

Peek will now rebuild the graph segment index for that model set.

Recompile Key Index
```````````````````

The admin task recompiles the GraphDB ItemKey Index for a given model set.

The ItemKeys are stored in one of 8192 hash buckets.
Recompiling the index will rebuild these hash buckets.

Each model set has it's own graph Item Key Index.

.. note:: You should not expect to need to recompile the index.

----

#.  Find the ID of the model set to recompile the index for.

#.  Stop all peek services

#.  Execute the following, replacing <ID> with the :code:`modeSetId` ::


        -- Delete the existing index data.
        DELETE FROM pl_graphdb."ItemKeyIndexCompilerQueue" WHERE "modelSetId" = <ID>;
        DELETE FROM pl_graphdb."ItemKeyIndexEncodedChunk" WHERE "modelSetId" = <ID>;

        -- Queue the chunks for compiling.
        INSERT INTO pl_graphdb."ItemKeyIndexCompilerQueue" ("modelSetId", "chunkKey")
        SELECT DISTINCT "modelSetId", "chunkKey"
        FROM pl_graphdb."ItemKeyIndex"
        WHERE "modelSetId" = <ID>;


#.  Start all Peek services

----

Peek will now rebuild the graph Item Key Index for that model set.