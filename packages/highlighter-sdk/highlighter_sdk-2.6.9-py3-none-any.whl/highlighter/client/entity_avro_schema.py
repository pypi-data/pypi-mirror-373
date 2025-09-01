ENTITY_AVRO_SCHEMA = [
    {
        "name": "Point",
        "namespace": "tracking",
        "type": "record",
        "fields": [{"name": "x", "type": "double"}, {"name": "y", "type": "double"}],
    },
    {
        "name": "Bounds",
        "namespace": "tracking",
        "type": "record",
        "fields": [{"name": "min", "type": "Point"}, {"name": "max", "type": "Point"}],
    },
    {
        "name": "Detection",
        "namespace": "tracking",
        "type": "record",
        "fields": [
            {"name": "frame_id", "type": "int"},
            {"name": "bounds", "type": ["null", "Bounds"]},
            {"name": "geometry_type", "type": "int"},
            {"name": "wkt", "type": ["null", "string"]},
            {"name": "confidence", "type": "float"},
        ],
    },
    {
        "name": "EntityDatumSource",
        "namespace": "tracking",
        "type": "record",
        "fields": [{"name": "confidence", "type": "double"}, {"name": "frameId", "type": "int"}],
    },
    {
        "name": "Eavt",
        "namespace": "tracking",
        "type": "record",
        "fields": [
            {"name": "entityId", "type": "string"},
            {"name": "entityAttributeId", "type": "string"},
            {"name": "entityAttributeEnumId", "type": "string"},
            {"name": "entityDatumSource", "type": "EntityDatumSource"},
            {"name": "value", "type": ["string", "int", "long", "float", "double", "null"]},
            {"name": "time", "type": {"type": "long", "logicalType": "timestamp-micros"}},
        ],
    },
    {
        "name": "Track",
        "namespace": "tracking",
        "type": "record",
        "fields": [
            {"name": "track_id", "type": "string"},
            {"name": "data_file_id", "type": "string"},
            {"name": "detections", "type": {"type": "array", "items": "Detection"}},
            {"name": "eavts", "type": {"type": "array", "items": "Eavt"}},
        ],
    },
    {
        "name": "Entity",
        "namespace": "tracking",
        "type": "record",
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "object_class", "type": "string"},
            {"name": "tracks", "type": {"type": "array", "items": "Track"}},
            {"name": "embeddings", "type": {"type": "array", "items": {"type": "array", "items": "int"}}},
        ],
    },
]
