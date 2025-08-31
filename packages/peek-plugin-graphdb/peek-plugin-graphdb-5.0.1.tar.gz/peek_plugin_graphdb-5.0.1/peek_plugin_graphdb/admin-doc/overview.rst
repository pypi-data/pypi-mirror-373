Overview
--------

The following sections describe the parts of the GraphDB plugin.

Importers
`````````

The GraphDB is populated by other plugins using the GraphDB import APIs.

The the import APIs take segments of the graph.

Model Set
`````````

The GraphDB plugin supports multiple model sets. Each model set has it's own connectivity
model.

Segments
````````

To allow Peek to support incremental updates to, the whole graph is dealt with as segments.
These segments determined by the import plugins.

Segments contain edges and vertices that link to other, vertices that are on the edge
of the segment are duplicated in the next segment, with a reference to the next
segment it belongs in.

Segmenting the graph is needed to allow for incremental loads of small parts
of the graphdb (aka segments).

This is for performance reasons, it's not practical to load the entire graph
on every change.

Trace Config
````````````

The GraphDB is queried via traces. Traces are run based on predefined configurations.

The trace configuration is a list of trace rules that define the behavior of
traces run on the GraphDB.

Trace configs can be imported via the GraphDB import APIs.

..
    Trace configs can be imported via GraphDB import APIs or edited via the Peek Admin UI.


Client Cache
````````````

The GraphDB caches the segment index,
in memory in the Peek Client service as compressed chunks/blocks of data.

The GraphDB also maintains a memory resident linked model of the
graph in the Peek Client service.

Segment Index
`````````````

The Segment Index contains the graph segments, grouped into 8192 hash buckets
based on their key.

This index follows the Peek Index Blueprint.

Key Index
`````````

The keys of each edge and vertex are stored in the key index.
This allows a lookup of which edge and vertices are in which trace segment.