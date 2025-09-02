from odp.dto import MetadataDto
from odp.dto.registry import ObservableClassDto, ObservableClassSpec

static_single_value_class = ObservableClassDto(
    metadata=MetadataDto(
        name="static-observable",
        labels={"catalog.hubocean.io/released": True},
    ),
    spec=ObservableClassSpec(
        observable_schema={
            "$schema": "http://json-schema.org/draft-04/schema#",
            "title": "StaticObservable",
            "type": "object",
            "description": "Single value observable",
            "properties": {"attribute": {"title": "Attribute", "type": "string"}, "value": {"title": "Value"}},
            "required": ["value"],
        }
    ),
)


static_coverage_class = ObservableClassDto(
    metadata=MetadataDto(
        name="static-coverage",
        labels={"catalog.hubocean.io/released": True},
    ),
    spec=ObservableClassSpec(
        observable_schema={
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "title": "StaticCoverage",
            "description": "1D real coverage",
            "required": ["attribute", "value"],
            "properties": {
                "value": {
                    "type": "array",
                    "items": [{"type": "number"}, {"type": "number"}],
                    "title": "Value",
                    "maxItems": 2,
                    "minItems": 2,
                },
                "attribute": {"type": "string", "title": "Attribute"},
            },
        }
    ),
)

static_geometric_coverage_class = ObservableClassDto(
    metadata=MetadataDto(
        name="static-geometric-coverage",
        labels={"catalog.hubocean.io/released": True},
    ),
    spec=ObservableClassSpec(
        observable_schema={
            "$schema": "http://json-schema.org/draft-04/schema#",
            "title": "StaticGeometricCoverage",
            "description": "Geometric coverage",
            "type": "object",
            "required": ["attribute", "value"],
            "properties": {
                "attribute": {"title": "Attribute", "type": "string"},
                "value": {"$ref": "#/definitions/Feature"},
            },
            "definitions": {
                "Point": {
                    "title": "Point",
                    "description": "Point Model",
                    "type": "object",
                    "properties": {
                        "type": {"title": "Type", "default": "Point", "const": "Point", "type": "string"},
                        "coordinates": {
                            "title": "Coordinates",
                            "anyOf": [
                                {
                                    "type": "array",
                                    "minItems": 2,
                                    "maxItems": 2,
                                    "items": [{"type": "number"}, {"type": "number"}],
                                },
                                {
                                    "type": "array",
                                    "minItems": 3,
                                    "maxItems": 3,
                                    "items": [{"type": "number"}, {"type": "number"}, {"type": "number"}],
                                },
                            ],
                        },
                    },
                    "required": ["coordinates"],
                },
                "MultiPoint": {
                    "title": "MultiPoint",
                    "description": "MultiPoint Model",
                    "type": "object",
                    "properties": {
                        "type": {"title": "Type", "default": "MultiPoint", "const": "MultiPoint", "type": "string"},
                        "coordinates": {
                            "title": "Coordinates",
                            "minItems": 1,
                            "type": "array",
                            "items": {
                                "anyOf": [
                                    {
                                        "type": "array",
                                        "minItems": 2,
                                        "maxItems": 2,
                                        "items": [{"type": "number"}, {"type": "number"}],
                                    },
                                    {
                                        "type": "array",
                                        "minItems": 3,
                                        "maxItems": 3,
                                        "items": [{"type": "number"}, {"type": "number"}, {"type": "number"}],
                                    },
                                ]
                            },
                        },
                    },
                    "required": ["coordinates"],
                },
                "LineString": {
                    "title": "LineString",
                    "description": "LineString Model",
                    "type": "object",
                    "properties": {
                        "type": {"title": "Type", "default": "LineString", "const": "LineString", "type": "string"},
                        "coordinates": {
                            "title": "Coordinates",
                            "minItems": 2,
                            "type": "array",
                            "items": {
                                "anyOf": [
                                    {
                                        "type": "array",
                                        "minItems": 2,
                                        "maxItems": 2,
                                        "items": [{"type": "number"}, {"type": "number"}],
                                    },
                                    {
                                        "type": "array",
                                        "minItems": 3,
                                        "maxItems": 3,
                                        "items": [{"type": "number"}, {"type": "number"}, {"type": "number"}],
                                    },
                                ]
                            },
                        },
                    },
                    "required": ["coordinates"],
                },
                "MultiLineString": {
                    "title": "MultiLineString",
                    "description": "MultiLineString Model",
                    "type": "object",
                    "properties": {
                        "type": {
                            "title": "Type",
                            "default": "MultiLineString",
                            "const": "MultiLineString",
                            "type": "string",
                        },
                        "coordinates": {
                            "title": "Coordinates",
                            "minItems": 1,
                            "type": "array",
                            "items": {
                                "type": "array",
                                "items": {
                                    "anyOf": [
                                        {
                                            "type": "array",
                                            "minItems": 2,
                                            "maxItems": 2,
                                            "items": [{"type": "number"}, {"type": "number"}],
                                        },
                                        {
                                            "type": "array",
                                            "minItems": 3,
                                            "maxItems": 3,
                                            "items": [{"type": "number"}, {"type": "number"}, {"type": "number"}],
                                        },
                                    ]
                                },
                                "minItems": 2,
                            },
                        },
                    },
                    "required": ["coordinates"],
                },
                "Polygon": {
                    "title": "Polygon",
                    "description": "Polygon Model",
                    "type": "object",
                    "properties": {
                        "type": {"title": "Type", "default": "Polygon", "const": "Polygon", "type": "string"},
                        "coordinates": {
                            "title": "Coordinates",
                            "minItems": 1,
                            "type": "array",
                            "items": {
                                "type": "array",
                                "items": {
                                    "anyOf": [
                                        {
                                            "type": "array",
                                            "minItems": 2,
                                            "maxItems": 2,
                                            "items": [{"type": "number"}, {"type": "number"}],
                                        },
                                        {
                                            "type": "array",
                                            "minItems": 3,
                                            "maxItems": 3,
                                            "items": [{"type": "number"}, {"type": "number"}, {"type": "number"}],
                                        },
                                    ]
                                },
                                "minItems": 4,
                            },
                        },
                    },
                    "required": ["coordinates"],
                },
                "MultiPolygon": {
                    "title": "MultiPolygon",
                    "description": "MultiPolygon Model",
                    "type": "object",
                    "properties": {
                        "type": {"title": "Type", "default": "MultiPolygon", "const": "MultiPolygon", "type": "string"},
                        "coordinates": {
                            "title": "Coordinates",
                            "minItems": 1,
                            "type": "array",
                            "items": {
                                "type": "array",
                                "items": {
                                    "type": "array",
                                    "items": {
                                        "anyOf": [
                                            {
                                                "type": "array",
                                                "minItems": 2,
                                                "maxItems": 2,
                                                "items": [{"type": "number"}, {"type": "number"}],
                                            },
                                            {
                                                "type": "array",
                                                "minItems": 3,
                                                "maxItems": 3,
                                                "items": [{"type": "number"}, {"type": "number"}, {"type": "number"}],
                                            },
                                        ]
                                    },
                                    "minItems": 4,
                                },
                                "minItems": 1,
                            },
                        },
                    },
                    "required": ["coordinates"],
                },
                "GeometryCollection": {
                    "title": "GeometryCollection",
                    "description": "GeometryCollection Model",
                    "type": "object",
                    "properties": {
                        "type": {
                            "title": "Type",
                            "default": "GeometryCollection",
                            "const": "GeometryCollection",
                            "type": "string",
                        },
                        "geometries": {
                            "title": "Geometries",
                            "type": "array",
                            "items": {
                                "anyOf": [
                                    {"$ref": "#/definitions/Point"},
                                    {"$ref": "#/definitions/MultiPoint"},
                                    {"$ref": "#/definitions/LineString"},
                                    {"$ref": "#/definitions/MultiLineString"},
                                    {"$ref": "#/definitions/Polygon"},
                                    {"$ref": "#/definitions/MultiPolygon"},
                                ]
                            },
                        },
                    },
                    "required": ["geometries"],
                },
                "BaseModel": {"title": "BaseModel", "type": "object", "properties": {}},
                "Feature": {
                    "title": "Feature",
                    "description": "Feature Model",
                    "type": "object",
                    "properties": {
                        "type": {"title": "Type", "default": "Feature", "const": "Feature", "type": "string"},
                        "geometry": {
                            "title": "Geometry",
                            "anyOf": [
                                {"$ref": "#/definitions/Point"},
                                {"$ref": "#/definitions/MultiPoint"},
                                {"$ref": "#/definitions/LineString"},
                                {"$ref": "#/definitions/MultiLineString"},
                                {"$ref": "#/definitions/Polygon"},
                                {"$ref": "#/definitions/MultiPolygon"},
                                {"$ref": "#/definitions/GeometryCollection"},
                            ],
                        },
                        "properties": {
                            "title": "Properties",
                            "anyOf": [{"type": "object"}, {"$ref": "#/definitions/BaseModel"}],
                        },
                        "id": {"title": "Id", "type": "string"},
                        "bbox": {
                            "title": "Bbox",
                            "anyOf": [
                                {
                                    "type": "array",
                                    "minItems": 4,
                                    "maxItems": 4,
                                    "items": [
                                        {"type": "number"},
                                        {"type": "number"},
                                        {"type": "number"},
                                        {"type": "number"},
                                    ],
                                },
                                {
                                    "type": "array",
                                    "minItems": 6,
                                    "maxItems": 6,
                                    "items": [
                                        {"type": "number"},
                                        {"type": "number"},
                                        {"type": "number"},
                                        {"type": "number"},
                                        {"type": "number"},
                                        {"type": "number"},
                                    ],
                                },
                            ],
                        },
                    },
                },
            },
        }
    ),
)
