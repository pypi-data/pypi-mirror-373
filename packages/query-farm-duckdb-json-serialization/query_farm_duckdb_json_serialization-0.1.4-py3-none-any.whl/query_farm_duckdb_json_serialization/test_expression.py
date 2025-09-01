import json
from typing import Any

import pytest

from . import expression, value

owner_type_info = {
    "Owner": 'STRUCT("DisplayName" VARCHAR,"ID" VARCHAR)',
    "aws_region": "VARCHAR",
}

bucket_type_info = {
    "Buckets": 'STRUCT("Name" VARCHAR,"CreationDate" TIMESTAMP_S)[]',
    "aws_region": "VARCHAR",
}


@pytest.mark.parametrize(
    "parser_cls,input",
    [
        (
            expression.BoundConstant,
            {
                "expression_class": "BOUND_CONSTANT",
                "type": "VALUE_CONSTANT",
                "alias": "",
                "query_location": 18446744073709552000,
                "value": {
                    "type": {
                        "id": "MAP",
                        "type_info": {
                            "type": "LIST_TYPE_INFO",
                            "alias": "",
                            "extension_info": None,
                            "child_type": {
                                "id": "STRUCT",
                                "type_info": {
                                    "type": "STRUCT_TYPE_INFO",
                                    "alias": "",
                                    "extension_info": None,
                                    "child_types": [
                                        {
                                            "first": "key",
                                            "second": {
                                                "id": "VARCHAR",
                                                "type_info": None,
                                            },
                                        },
                                        {
                                            "first": "value",
                                            "second": {
                                                "id": "VARCHAR",
                                                "type_info": None,
                                            },
                                        },
                                    ],
                                },
                            },
                        },
                    },
                    "is_null": False,
                    "value": {
                        "children": [
                            {
                                "type": {
                                    "id": "STRUCT",
                                    "type_info": {
                                        "type": "STRUCT_TYPE_INFO",
                                        "alias": "",
                                        "extension_info": None,
                                        "child_types": [
                                            {
                                                "first": "key",
                                                "second": {
                                                    "id": "VARCHAR",
                                                    "type_info": None,
                                                },
                                            },
                                            {
                                                "first": "value",
                                                "second": {
                                                    "id": "VARCHAR",
                                                    "type_info": None,
                                                },
                                            },
                                        ],
                                    },
                                },
                                "is_null": False,
                                "value": {
                                    "children": [
                                        {
                                            "type": {
                                                "id": "VARCHAR",
                                                "type_info": None,
                                            },
                                            "is_null": False,
                                            "value": "color",
                                        },
                                        {
                                            "type": {
                                                "id": "VARCHAR",
                                                "type_info": None,
                                            },
                                            "is_null": False,
                                            "value": "red",
                                        },
                                    ]
                                },
                            }
                        ]
                    },
                },
            },
        ),
        (
            expression.BoundFunction,
            {
                "expression_class": "BOUND_FUNCTION",
                "type": "BOUND_FUNCTION",
                "alias": "",
                "query_location": 40,
                "return_type": {
                    "id": "STRUCT",
                    "type_info": {
                        "type": "STRUCT_TYPE_INFO",
                        "alias": "",
                        "extension_info": None,
                        "child_types": [
                            {
                                "first": "color",
                                "second": {"id": "VARCHAR", "type_info": None},
                            }
                        ],
                    },
                },
                "children": [
                    {
                        "expression_class": "BOUND_FUNCTION",
                        "type": "BOUND_FUNCTION",
                        "alias": "color",
                        "query_location": 49,
                        "return_type": {"id": "VARCHAR", "type_info": None},
                        "children": [
                            {
                                "expression_class": "BOUND_COLUMN_REF",
                                "type": "BOUND_COLUMN_REF",
                                "alias": "mapping",
                                "query_location": 18446744073709552000,
                                "return_type": {
                                    "id": "MAP",
                                    "type_info": {
                                        "type": "LIST_TYPE_INFO",
                                        "alias": "",
                                        "extension_info": None,
                                        "child_type": {
                                            "id": "STRUCT",
                                            "type_info": {
                                                "type": "STRUCT_TYPE_INFO",
                                                "alias": "",
                                                "extension_info": None,
                                                "child_types": [
                                                    {
                                                        "first": "key",
                                                        "second": {
                                                            "id": "VARCHAR",
                                                            "type_info": None,
                                                        },
                                                    },
                                                    {
                                                        "first": "value",
                                                        "second": {
                                                            "id": "VARCHAR",
                                                            "type_info": None,
                                                        },
                                                    },
                                                ],
                                            },
                                        },
                                    },
                                },
                                "binding": {"table_index": 0, "column_index": 0},
                                "depth": 0,
                            },
                            {
                                "expression_class": "BOUND_CONSTANT",
                                "type": "VALUE_CONSTANT",
                                "alias": "",
                                "query_location": 18446744073709552000,
                                "value": {
                                    "type": {"id": "VARCHAR", "type_info": None},
                                    "is_null": False,
                                    "value": "color",
                                },
                            },
                        ],
                        "name": "map_extract_value",
                        "arguments": [
                            {"id": "ANY", "type_info": None},
                            {"id": "VARCHAR", "type_info": None},
                        ],
                        "original_arguments": [],
                        "catalog_name": "system",
                        "schema_name": "main",
                        "has_serialize": False,
                        "is_operator": False,
                    }
                ],
                "name": "struct_pack",
                "arguments": [],
                "original_arguments": [],
                "catalog_name": "system",
                "schema_name": "main",
                "has_serialize": True,
                "function_data": {
                    "variable_return_type": {
                        "id": "STRUCT",
                        "type_info": {
                            "type": "STRUCT_TYPE_INFO",
                            "alias": "",
                            "extension_info": None,
                            "child_types": [
                                {
                                    "first": "color",
                                    "second": {"id": "VARCHAR", "type_info": None},
                                }
                            ],
                        },
                    }
                },
                "is_operator": False,
            },
        ),
        (
            value.ValueType_map,
            {
                "id": "MAP",
                "type_info": {
                    "type": "LIST_TYPE_INFO",
                    "alias": "",
                    "extension_info": None,
                    "child_type": {
                        "id": "STRUCT",
                        "type_info": {
                            "type": "STRUCT_TYPE_INFO",
                            "alias": "",
                            "extension_info": None,
                            "child_types": [
                                {
                                    "first": "key",
                                    "second": {"id": "VARCHAR", "type_info": None},
                                },
                                {
                                    "first": "value",
                                    "second": {"id": "VARCHAR", "type_info": None},
                                },
                            ],
                        },
                    },
                },
            },
        ),
        (
            expression.BoundColumnRef,
            {
                "expression_class": "BOUND_COLUMN_REF",
                "type": "BOUND_COLUMN_REF",
                "alias": "mapping",
                "query_location": 18446744073709551615,
                "return_type": {
                    "id": "MAP",
                    "type_info": {
                        "type": "LIST_TYPE_INFO",
                        "alias": "",
                        "extension_info": None,
                        "child_type": {
                            "id": "STRUCT",
                            "type_info": {
                                "type": "STRUCT_TYPE_INFO",
                                "alias": "",
                                "extension_info": None,
                                "child_types": [
                                    {
                                        "first": "key",
                                        "second": {"id": "VARCHAR", "type_info": None},
                                    },
                                    {
                                        "first": "value",
                                        "second": {"id": "VARCHAR", "type_info": None},
                                    },
                                ],
                            },
                        },
                    },
                },
                "binding": {"table_index": 0, "column_index": 0},
                "depth": 0,
            },
        ),
        (
            expression.BoundFunction,
            {
                "expression_class": "BOUND_FUNCTION",
                "type": "BOUND_FUNCTION",
                "alias": "",
                "query_location": 39,
                "return_type": {"id": "VARCHAR", "type_info": None},
                "children": [
                    {
                        "expression_class": "BOUND_COLUMN_REF",
                        "type": "BOUND_COLUMN_REF",
                        "alias": "mapping",
                        "query_location": 18446744073709551615,
                        "return_type": {
                            "id": "MAP",
                            "type_info": {
                                "type": "LIST_TYPE_INFO",
                                "alias": "",
                                "extension_info": None,
                                "child_type": {
                                    "id": "STRUCT",
                                    "type_info": {
                                        "type": "STRUCT_TYPE_INFO",
                                        "alias": "",
                                        "extension_info": None,
                                        "child_types": [
                                            {
                                                "first": "key",
                                                "second": {
                                                    "id": "VARCHAR",
                                                    "type_info": None,
                                                },
                                            },
                                            {
                                                "first": "value",
                                                "second": {
                                                    "id": "VARCHAR",
                                                    "type_info": None,
                                                },
                                            },
                                        ],
                                    },
                                },
                            },
                        },
                        "binding": {"table_index": 0, "column_index": 0},
                        "depth": 0,
                    },
                    {
                        "expression_class": "BOUND_CONSTANT",
                        "type": "VALUE_CONSTANT",
                        "alias": "",
                        "query_location": 18446744073709551615,
                        "value": {
                            "type": {"id": "VARCHAR", "type_info": None},
                            "is_null": False,
                            "value": "color",
                        },
                    },
                ],
                "name": "map_extract_value",
                "arguments": [
                    {"id": "ANY", "type_info": None},
                    {"id": "VARCHAR", "type_info": None},
                ],
                "original_arguments": [],
                "catalog_name": "system",
                "schema_name": "main",
                "has_serialize": False,
                "is_operator": False,
            },
        ),
        (
            expression.BoundComparison,
            {
                "expression_class": "BOUND_COMPARISON",
                "type": "COMPARE_EQUAL",
                "alias": "",
                "query_location": 18446744073709551615,
                "left": {
                    "expression_class": "BOUND_FUNCTION",
                    "type": "BOUND_FUNCTION",
                    "alias": "",
                    "query_location": 39,
                    "return_type": {"id": "VARCHAR", "type_info": None},
                    "children": [
                        {
                            "expression_class": "BOUND_COLUMN_REF",
                            "type": "BOUND_COLUMN_REF",
                            "alias": "mapping",
                            "query_location": 18446744073709551615,
                            "return_type": {
                                "id": "MAP",
                                "type_info": {
                                    "type": "LIST_TYPE_INFO",
                                    "alias": "",
                                    "extension_info": None,
                                    "child_type": {
                                        "id": "STRUCT",
                                        "type_info": {
                                            "type": "STRUCT_TYPE_INFO",
                                            "alias": "",
                                            "extension_info": None,
                                            "child_types": [
                                                {
                                                    "first": "key",
                                                    "second": {
                                                        "id": "VARCHAR",
                                                        "type_info": None,
                                                    },
                                                },
                                                {
                                                    "first": "value",
                                                    "second": {
                                                        "id": "VARCHAR",
                                                        "type_info": None,
                                                    },
                                                },
                                            ],
                                        },
                                    },
                                },
                            },
                            "binding": {"table_index": 0, "column_index": 0},
                            "depth": 0,
                        },
                        {
                            "expression_class": "BOUND_CONSTANT",
                            "type": "VALUE_CONSTANT",
                            "alias": "",
                            "query_location": 18446744073709551615,
                            "value": {
                                "type": {"id": "VARCHAR", "type_info": None},
                                "is_null": False,
                                "value": "color",
                            },
                        },
                    ],
                    "name": "map_extract_value",
                    "arguments": [
                        {"id": "ANY", "type_info": None},
                        {"id": "VARCHAR", "type_info": None},
                    ],
                    "original_arguments": [],
                    "catalog_name": "system",
                    "schema_name": "main",
                    "has_serialize": False,
                    "is_operator": False,
                },
                "right": {
                    "expression_class": "BOUND_CONSTANT",
                    "type": "VALUE_CONSTANT",
                    "alias": "",
                    "query_location": 18446744073709551615,
                    "value": {
                        "type": {"id": "VARCHAR", "type_info": None},
                        "is_null": False,
                        "value": "red",
                    },
                },
            },
        ),
        (
            value.ValueType_list,
            {
                "id": "LIST",
                "type_info": {
                    "type": "LIST_TYPE_INFO",
                    "alias": "",
                    "extension_info": None,
                    "child_type": {"id": "INTEGER", "type_info": None},
                },
            },
        ),
        (
            expression.BoundFunction,
            {
                "expression_class": "BOUND_FUNCTION",
                "type": "BOUND_FUNCTION",
                "alias": "",
                "query_location": 18446744073709552000,
                "return_type": {"id": "INTEGER", "type_info": None},
                "children": [
                    {
                        "expression_class": "BOUND_COLUMN_REF",
                        "type": "BOUND_COLUMN_REF",
                        "alias": "switches",
                        "query_location": 18446744073709552000,
                        "return_type": {
                            "id": "LIST",
                            "type_info": {
                                "type": "LIST_TYPE_INFO",
                                "alias": "",
                                "extension_info": None,
                                "child_type": {"id": "INTEGER", "type_info": None},
                            },
                        },
                        "binding": {"table_index": 0, "column_index": 0},
                        "depth": 0,
                    },
                    {
                        "expression_class": "BOUND_CONSTANT",
                        "type": "VALUE_CONSTANT",
                        "alias": "",
                        "query_location": 18446744073709552000,
                        "value": {
                            "type": {"id": "BIGINT", "type_info": None},
                            "is_null": False,
                            "value": 0,
                        },
                    },
                ],
                "name": "array_extract",
                "arguments": [
                    {
                        "id": "LIST",
                        "type_info": {
                            "type": "LIST_TYPE_INFO",
                            "alias": "",
                            "extension_info": None,
                            "child_type": {"id": "INTEGER", "type_info": None},
                        },
                    },
                    {"id": "BIGINT", "type_info": None},
                ],
                "original_arguments": [],
                "catalog_name": "system",
                "schema_name": "main",
                "has_serialize": False,
                "is_operator": False,
            },
        ),
    ],
)
def test_parse(parser_cls: Any, input: dict[str, Any]) -> None:
    parser_cls.model_validate(input)


@pytest.mark.parametrize(
    "json_source,expected_sql,expected_bound_types",
    [
        (
            '{"filters":[{"expression_class":"BOUND_FUNCTION","type":"BOUND_FUNCTION","alias":"","query_location":18446744073709551615,"return_type":{"id":"BOOLEAN","type_info":null},"children":[{"expression_class":"BOUND_COLUMN_REF","type":"BOUND_COLUMN_REF","alias":"aws_region","query_location":70,"return_type":{"id":"VARCHAR","type_info":null},"binding":{"table_index":0,"column_index":0},"depth":0},{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"bar"}}],"name":"prefix","arguments":[{"id":"VARCHAR","type_info":null},{"id":"VARCHAR","type_info":null}],"original_arguments":[],"has_serialize":false,"is_operator":false},{"expression_class":"BOUND_COMPARISON","type":"COMPARE_EQUAL","alias":"","query_location":18446744073709551615,"left":{"expression_class":"BOUND_COLUMN_REF","type":"BOUND_COLUMN_REF","alias":"aws_region","query_location":18446744073709551615,"return_type":{"id":"VARCHAR","type_info":null},"binding":{"table_index":0,"column_index":0},"depth":0},"right":{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"us-east-1"}}}],"column_binding_names_by_index":["aws_region","Buckets","Owner","aws_profile_name"]}',
            "prefix(\"aws_region\", 'bar') AND \"aws_region\" = 'us-east-1'",
            {"aws_region": "VARCHAR"},
        ),
        (
            '{"filters":[{"expression_class":"BOUND_OPERATOR","type":"COMPARE_IN","alias":"","query_location":81,"return_type":{"id":"BOOLEAN","type_info":null},"children":[{"expression_class":"BOUND_COLUMN_REF","type":"BOUND_COLUMN_REF","alias":"aws_region","query_location":70,"return_type":{"id":"VARCHAR","type_info":null},"binding":{"table_index":0,"column_index":0},"depth":0},{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"us-east-1"}},{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"us-east-2"}}]},{"expression_class":"BOUND_COMPARISON","type":"COMPARE_EQUAL","alias":"","query_location":18446744073709551615,"left":{"expression_class":"BOUND_COLUMN_REF","type":"BOUND_COLUMN_REF","alias":"aws_region","query_location":18446744073709551615,"return_type":{"id":"VARCHAR","type_info":null},"binding":{"table_index":0,"column_index":0},"depth":0},"right":{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"us-east-1"}}}],"column_binding_names_by_index":["aws_region","Buckets","Owner","aws_profile_name"]}',
            "\"aws_region\" IN ('us-east-1', 'us-east-2') AND \"aws_region\" = 'us-east-1'",
            {"aws_region": "VARCHAR"},
        ),
        (
            '{"filters":[{"expression_class":"BOUND_COMPARISON","type":"COMPARE_EQUAL","alias":"","query_location":18446744073709551615,"left":{"expression_class":"BOUND_FUNCTION","type":"BOUND_FUNCTION","alias":"","query_location":18446744073709551615,"return_type":{"id":"VARCHAR","type_info":null},"children":[{"expression_class":"BOUND_FUNCTION","type":"BOUND_FUNCTION","alias":"","query_location":18446744073709551615,"return_type":{"id":"STRUCT","type_info":{"type":"STRUCT_TYPE_INFO","alias":"","modifiers":[],"child_types":[{"first":"Name","second":{"id":"VARCHAR","type_info":null}},{"first":"CreationDate","second":{"id":"TIMESTAMP_S","type_info":null}}]}},"children":[{"expression_class":"BOUND_COLUMN_REF","type":"BOUND_COLUMN_REF","alias":"Buckets","query_location":18446744073709551615,"return_type":{"id":"LIST","type_info":{"type":"LIST_TYPE_INFO","alias":"","modifiers":[],"child_type":{"id":"STRUCT","type_info":{"type":"STRUCT_TYPE_INFO","alias":"","modifiers":[],"child_types":[{"first":"Name","second":{"id":"VARCHAR","type_info":null}},{"first":"CreationDate","second":{"id":"TIMESTAMP_S","type_info":null}}]}}}},"binding":{"table_index":0,"column_index":1},"depth":0},{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"BIGINT","type_info":null},"is_null":false,"value":1}}],"name":"array_extract","arguments":[{"id":"LIST","type_info":{"type":"LIST_TYPE_INFO","alias":"","modifiers":[],"child_type":{"id":"STRUCT","type_info":{"type":"STRUCT_TYPE_INFO","alias":"","modifiers":[],"child_types":[{"first":"Name","second":{"id":"VARCHAR","type_info":null}},{"first":"CreationDate","second":{"id":"TIMESTAMP_S","type_info":null}}]}}}},{"id":"BIGINT","type_info":null}],"original_arguments":[],"has_serialize":false,"is_operator":false},{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"Name"}}],"name":"struct_extract","arguments":[{"id":"STRUCT","type_info":{"type":"STRUCT_TYPE_INFO","alias":"","modifiers":[],"child_types":[{"first":"Name","second":{"id":"VARCHAR","type_info":null}},{"first":"CreationDate","second":{"id":"TIMESTAMP_S","type_info":null}}]}},{"id":"VARCHAR","type_info":null}],"original_arguments":[],"has_serialize":false,"is_operator":false},"right":{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"foobar"}}},{"expression_class":"BOUND_COMPARISON","type":"COMPARE_EQUAL","alias":"","query_location":18446744073709551615,"left":{"expression_class":"BOUND_COLUMN_REF","type":"BOUND_COLUMN_REF","alias":"aws_region","query_location":18446744073709551615,"return_type":{"id":"VARCHAR","type_info":null},"binding":{"table_index":0,"column_index":0},"depth":0},"right":{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"us-east-1"}}}],"column_binding_names_by_index":["aws_region","Buckets","Owner","aws_profile_name"]}',
            "struct_extract(array_extract(\"Buckets\", 1), 'Name') = 'foobar' AND \"aws_region\" = 'us-east-1'",
            bucket_type_info,
        ),
        (
            '{"filters":[{"expression_class":"BOUND_COMPARISON","type":"COMPARE_EQUAL","alias":"","query_location":18446744073709551615,"left":{"expression_class":"BOUND_FUNCTION","type":"BOUND_FUNCTION","alias":"","query_location":71,"return_type":{"id":"STRUCT","type_info":{"type":"STRUCT_TYPE_INFO","alias":"","modifiers":[],"child_types":[{"first":"hello","second":{"id":"VARCHAR","type_info":null}}]}},"children":[{"expression_class":"BOUND_FUNCTION","type":"BOUND_FUNCTION","alias":"hello","query_location":18446744073709551615,"return_type":{"id":"VARCHAR","type_info":null},"children":[{"expression_class":"BOUND_FUNCTION","type":"BOUND_FUNCTION","alias":"","query_location":18446744073709551615,"return_type":{"id":"STRUCT","type_info":{"type":"STRUCT_TYPE_INFO","alias":"","modifiers":[],"child_types":[{"first":"Name","second":{"id":"VARCHAR","type_info":null}},{"first":"CreationDate","second":{"id":"TIMESTAMP_S","type_info":null}}]}},"children":[{"expression_class":"BOUND_COLUMN_REF","type":"BOUND_COLUMN_REF","alias":"Buckets","query_location":18446744073709551615,"return_type":{"id":"LIST","type_info":{"type":"LIST_TYPE_INFO","alias":"","modifiers":[],"child_type":{"id":"STRUCT","type_info":{"type":"STRUCT_TYPE_INFO","alias":"","modifiers":[],"child_types":[{"first":"Name","second":{"id":"VARCHAR","type_info":null}},{"first":"CreationDate","second":{"id":"TIMESTAMP_S","type_info":null}}]}}}},"binding":{"table_index":0,"column_index":1},"depth":0},{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"BIGINT","type_info":null},"is_null":false,"value":1}}],"name":"array_extract","arguments":[{"id":"LIST","type_info":{"type":"LIST_TYPE_INFO","alias":"","modifiers":[],"child_type":{"id":"STRUCT","type_info":{"type":"STRUCT_TYPE_INFO","alias":"","modifiers":[],"child_types":[{"first":"Name","second":{"id":"VARCHAR","type_info":null}},{"first":"CreationDate","second":{"id":"TIMESTAMP_S","type_info":null}}]}}}},{"id":"BIGINT","type_info":null}],"original_arguments":[],"has_serialize":false,"is_operator":false},{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"Name"}}],"name":"struct_extract","arguments":[{"id":"STRUCT","type_info":{"type":"STRUCT_TYPE_INFO","alias":"","modifiers":[],"child_types":[{"first":"Name","second":{"id":"VARCHAR","type_info":null}},{"first":"CreationDate","second":{"id":"TIMESTAMP_S","type_info":null}}]}},{"id":"VARCHAR","type_info":null}],"original_arguments":[],"has_serialize":false,"is_operator":false}],"name":"struct_pack","arguments":[],"original_arguments":[],"has_serialize":true,"function_data":{"variable_return_type":{"id":"STRUCT","type_info":{"type":"STRUCT_TYPE_INFO","alias":"","modifiers":[],"child_types":[{"first":"hello","second":{"id":"VARCHAR","type_info":null}}]}}},"is_operator":false},"right":{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"STRUCT","type_info":{"type":"STRUCT_TYPE_INFO","alias":"","modifiers":[],"child_types":[{"first":"hello","second":{"id":"VARCHAR","type_info":null}}]}},"is_null":false,"value":{"children":[{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"foo"}]}}}},{"expression_class":"BOUND_COMPARISON","type":"COMPARE_EQUAL","alias":"","query_location":18446744073709551615,"left":{"expression_class":"BOUND_COLUMN_REF","type":"BOUND_COLUMN_REF","alias":"aws_region","query_location":18446744073709551615,"return_type":{"id":"VARCHAR","type_info":null},"binding":{"table_index":0,"column_index":0},"depth":0},"right":{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"us-east-1"}}}],"column_binding_names_by_index":["aws_region","Buckets","Owner","aws_profile_name"]}',
            "struct_pack(hello := struct_extract(array_extract(\"Buckets\", 1), 'Name')) = {'hello':'foo'} AND \"aws_region\" = 'us-east-1'",
            bucket_type_info,
        ),
        (
            '{"filters":[{"expression_class":"BOUND_COMPARISON","type":"COMPARE_EQUAL","alias":"","query_location":18446744073709551615,"left":{"expression_class":"BOUND_FUNCTION","type":"BOUND_FUNCTION","alias":"","query_location":71,"return_type":{"id":"STRUCT","type_info":{"type":"STRUCT_TYPE_INFO","alias":"","modifiers":[],"child_types":[{"first":"hello","second":{"id":"VARCHAR","type_info":null}},{"first":"d","second":{"id":"DATE","type_info":null}},{"first":"z","second":{"id":"LIST","type_info":{"type":"LIST_TYPE_INFO","alias":"","modifiers":[],"child_type":{"id":"INTEGER","type_info":null}}}},{"first":"c","second":{"id":"LIST","type_info":{"type":"LIST_TYPE_INFO","alias":"","modifiers":[],"child_type":{"id":"VARCHAR","type_info":null}}}}]}},"children":[{"expression_class":"BOUND_FUNCTION","type":"BOUND_FUNCTION","alias":"hello","query_location":18446744073709551615,"return_type":{"id":"VARCHAR","type_info":null},"children":[{"expression_class":"BOUND_FUNCTION","type":"BOUND_FUNCTION","alias":"","query_location":18446744073709551615,"return_type":{"id":"STRUCT","type_info":{"type":"STRUCT_TYPE_INFO","alias":"","modifiers":[],"child_types":[{"first":"Name","second":{"id":"VARCHAR","type_info":null}},{"first":"CreationDate","second":{"id":"TIMESTAMP_S","type_info":null}}]}},"children":[{"expression_class":"BOUND_COLUMN_REF","type":"BOUND_COLUMN_REF","alias":"Buckets","query_location":18446744073709551615,"return_type":{"id":"LIST","type_info":{"type":"LIST_TYPE_INFO","alias":"","modifiers":[],"child_type":{"id":"STRUCT","type_info":{"type":"STRUCT_TYPE_INFO","alias":"","modifiers":[],"child_types":[{"first":"Name","second":{"id":"VARCHAR","type_info":null}},{"first":"CreationDate","second":{"id":"TIMESTAMP_S","type_info":null}}]}}}},"binding":{"table_index":0,"column_index":1},"depth":0},{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"BIGINT","type_info":null},"is_null":false,"value":1}}],"name":"array_extract","arguments":[{"id":"LIST","type_info":{"type":"LIST_TYPE_INFO","alias":"","modifiers":[],"child_type":{"id":"STRUCT","type_info":{"type":"STRUCT_TYPE_INFO","alias":"","modifiers":[],"child_types":[{"first":"Name","second":{"id":"VARCHAR","type_info":null}},{"first":"CreationDate","second":{"id":"TIMESTAMP_S","type_info":null}}]}}}},{"id":"BIGINT","type_info":null}],"original_arguments":[],"has_serialize":false,"is_operator":false},{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"Name"}}],"name":"struct_extract","arguments":[{"id":"STRUCT","type_info":{"type":"STRUCT_TYPE_INFO","alias":"","modifiers":[],"child_types":[{"first":"Name","second":{"id":"VARCHAR","type_info":null}},{"first":"CreationDate","second":{"id":"TIMESTAMP_S","type_info":null}}]}},{"id":"VARCHAR","type_info":null}],"original_arguments":[],"has_serialize":false,"is_operator":false},{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"DATE","type_info":null},"is_null":false,"value":19754}},{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"LIST","type_info":{"type":"LIST_TYPE_INFO","alias":"","modifiers":[],"child_type":{"id":"INTEGER","type_info":null}}},"is_null":false,"value":{"children":[{"type":{"id":"INTEGER","type_info":null},"is_null":false,"value":1},{"type":{"id":"INTEGER","type_info":null},"is_null":false,"value":2},{"type":{"id":"INTEGER","type_info":null},"is_null":false,"value":3}]}}},{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"LIST","type_info":{"type":"LIST_TYPE_INFO","alias":"","modifiers":[],"child_type":{"id":"VARCHAR","type_info":null}}},"is_null":false,"value":{"children":[{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"f"},{"type":{"id":"VARCHAR","type_info":null},"is_null":true},{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"b"}]}}}],"name":"struct_pack","arguments":[],"original_arguments":[],"has_serialize":true,"function_data":{"variable_return_type":{"id":"STRUCT","type_info":{"type":"STRUCT_TYPE_INFO","alias":"","modifiers":[],"child_types":[{"first":"hello","second":{"id":"VARCHAR","type_info":null}},{"first":"d","second":{"id":"DATE","type_info":null}},{"first":"z","second":{"id":"LIST","type_info":{"type":"LIST_TYPE_INFO","alias":"","modifiers":[],"child_type":{"id":"INTEGER","type_info":null}}}},{"first":"c","second":{"id":"LIST","type_info":{"type":"LIST_TYPE_INFO","alias":"","modifiers":[],"child_type":{"id":"VARCHAR","type_info":null}}}}]}}},"is_operator":false},"right":{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"STRUCT","type_info":{"type":"STRUCT_TYPE_INFO","alias":"","modifiers":[],"child_types":[{"first":"hello","second":{"id":"VARCHAR","type_info":null}},{"first":"d","second":{"id":"DATE","type_info":null}},{"first":"z","second":{"id":"LIST","type_info":{"type":"LIST_TYPE_INFO","alias":"","modifiers":[],"child_type":{"id":"INTEGER","type_info":null}}}},{"first":"c","second":{"id":"LIST","type_info":{"type":"LIST_TYPE_INFO","alias":"","modifiers":[],"child_type":{"id":"VARCHAR","type_info":null}}}}]}},"is_null":false,"value":{"children":[{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"foo"},{"type":{"id":"DATE","type_info":null},"is_null":false,"value":3652},{"type":{"id":"LIST","type_info":{"type":"LIST_TYPE_INFO","alias":"","modifiers":[],"child_type":{"id":"INTEGER","type_info":null}}},"is_null":false,"value":{"children":[{"type":{"id":"INTEGER","type_info":null},"is_null":false,"value":4},{"type":{"id":"INTEGER","type_info":null},"is_null":false,"value":5},{"type":{"id":"INTEGER","type_info":null},"is_null":false,"value":6}]}},{"type":{"id":"LIST","type_info":{"type":"LIST_TYPE_INFO","alias":"","modifiers":[],"child_type":{"id":"VARCHAR","type_info":null}}},"is_null":false,"value":{"children":[{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"f"},{"type":{"id":"VARCHAR","type_info":null},"is_null":true},{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"b"}]}}]}}}},{"expression_class":"BOUND_COMPARISON","type":"COMPARE_EQUAL","alias":"","query_location":18446744073709551615,"left":{"expression_class":"BOUND_COLUMN_REF","type":"BOUND_COLUMN_REF","alias":"aws_region","query_location":18446744073709551615,"return_type":{"id":"VARCHAR","type_info":null},"binding":{"table_index":0,"column_index":0},"depth":0},"right":{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"us-east-1"}}}],"column_binding_names_by_index":["aws_region","Buckets","Owner","aws_profile_name"]}',
            "struct_pack(hello := struct_extract(array_extract(\"Buckets\", 1), 'Name'), d := '2024-02-01', z := [1, 2, 3], c := ['f', null, 'b']) = {'hello':'foo','d':'1980-01-01','z':[4, 5, 6],'c':['f', null, 'b']} AND \"aws_region\" = 'us-east-1'",
            bucket_type_info,
        ),
        (
            '{"filters":[{"expression_class":"BOUND_COMPARISON","type":"COMPARE_EQUAL","alias":"","query_location":78,"left":{"expression_class":"BOUND_FUNCTION","type":"BOUND_FUNCTION","alias":"","query_location":71,"return_type":{"id":"LIST","type_info":{"type":"LIST_TYPE_INFO","alias":"","modifiers":[],"child_type":{"id":"STRUCT","type_info":{"type":"STRUCT_TYPE_INFO","alias":"","modifiers":[],"child_types":[{"first":"DisplayName","second":{"id":"VARCHAR","type_info":null}},{"first":"ID","second":{"id":"VARCHAR","type_info":null}}]}}}},"children":[{"expression_class":"BOUND_COLUMN_REF","type":"BOUND_COLUMN_REF","alias":"Owner","query_location":71,"return_type":{"id":"STRUCT","type_info":{"type":"STRUCT_TYPE_INFO","alias":"","modifiers":[],"child_types":[{"first":"DisplayName","second":{"id":"VARCHAR","type_info":null}},{"first":"ID","second":{"id":"VARCHAR","type_info":null}}]}},"binding":{"table_index":0,"column_index":1},"depth":0}],"name":"list_value","arguments":[],"original_arguments":[],"has_serialize":false,"is_operator":false},"right":{"expression_class":"BOUND_FUNCTION","type":"BOUND_FUNCTION","alias":"","query_location":81,"return_type":{"id":"LIST","type_info":{"type":"LIST_TYPE_INFO","alias":"","modifiers":[],"child_type":{"id":"STRUCT","type_info":{"type":"STRUCT_TYPE_INFO","alias":"","modifiers":[],"child_types":[{"first":"DisplayName","second":{"id":"VARCHAR","type_info":null}},{"first":"ID","second":{"id":"VARCHAR","type_info":null}}]}}}},"children":[{"expression_class":"BOUND_COLUMN_REF","type":"BOUND_COLUMN_REF","alias":"Owner","query_location":81,"return_type":{"id":"STRUCT","type_info":{"type":"STRUCT_TYPE_INFO","alias":"","modifiers":[],"child_types":[{"first":"DisplayName","second":{"id":"VARCHAR","type_info":null}},{"first":"ID","second":{"id":"VARCHAR","type_info":null}}]}},"binding":{"table_index":0,"column_index":1},"depth":0}],"name":"list_value","arguments":[],"original_arguments":[],"has_serialize":false,"is_operator":false}},{"expression_class":"BOUND_COMPARISON","type":"COMPARE_EQUAL","alias":"","query_location":18446744073709551615,"left":{"expression_class":"BOUND_COLUMN_REF","type":"BOUND_COLUMN_REF","alias":"aws_region","query_location":18446744073709551615,"return_type":{"id":"VARCHAR","type_info":null},"binding":{"table_index":0,"column_index":0},"depth":0},"right":{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"us-east-1"}}}],"column_binding_names_by_index":["aws_region","Owner","Buckets","aws_profile_name"]}',
            'list_value("Owner") = list_value("Owner") AND "aws_region" = \'us-east-1\'',
            owner_type_info,
        ),
        (
            '{"filters":[{"expression_class":"BOUND_COMPARISON","type":"COMPARE_EQUAL","alias":"","query_location":18446744073709551615,"left":{"expression_class":"BOUND_COLUMN_REF","type":"BOUND_COLUMN_REF","alias":"Owner","query_location":18446744073709551615,"return_type":{"id":"STRUCT","type_info":{"type":"STRUCT_TYPE_INFO","alias":"","modifiers":[],"child_types":[{"first":"DisplayName","second":{"id":"VARCHAR","type_info":null}},{"first":"ID","second":{"id":"VARCHAR","type_info":null}}]}},"binding":{"table_index":0,"column_index":1},"depth":0},"right":{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"STRUCT","type_info":{"type":"STRUCT_TYPE_INFO","alias":"","modifiers":[],"child_types":[{"first":"DisplayName","second":{"id":"VARCHAR","type_info":null}},{"first":"ID","second":{"id":"VARCHAR","type_info":null}}]}},"is_null":false,"value":{"children":[{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"test"},{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"v"}]}}}},{"expression_class":"BOUND_COMPARISON","type":"COMPARE_EQUAL","alias":"","query_location":18446744073709551615,"left":{"expression_class":"BOUND_COLUMN_REF","type":"BOUND_COLUMN_REF","alias":"aws_region","query_location":18446744073709551615,"return_type":{"id":"VARCHAR","type_info":null},"binding":{"table_index":0,"column_index":0},"depth":0},"right":{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"us-east-1"}}}],"column_binding_names_by_index":["aws_region","Owner","Buckets","aws_profile_name"]}',
            "\"Owner\" = {'DisplayName':'test','ID':'v'} AND \"aws_region\" = 'us-east-1'",
            owner_type_info,
        ),
        (
            '{"filters":[{"expression_class":"BOUND_OPERATOR","type":"COMPARE_NOT_IN","alias":"","query_location":76,"return_type":{"id":"BOOLEAN","type_info":null},"children":[{"expression_class":"BOUND_COLUMN_REF","type":"BOUND_COLUMN_REF","alias":"Owner","query_location":70,"return_type":{"id":"STRUCT","type_info":{"type":"STRUCT_TYPE_INFO","alias":"","modifiers":[],"child_types":[{"first":"DisplayName","second":{"id":"VARCHAR","type_info":null}},{"first":"ID","second":{"id":"VARCHAR","type_info":null}}]}},"binding":{"table_index":0,"column_index":1},"depth":0},{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"STRUCT","type_info":{"type":"STRUCT_TYPE_INFO","alias":"","modifiers":[],"child_types":[{"first":"DisplayName","second":{"id":"VARCHAR","type_info":null}},{"first":"ID","second":{"id":"VARCHAR","type_info":null}}]}},"is_null":false,"value":{"children":[{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"test"},{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"v"}]}}},{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"STRUCT","type_info":{"type":"STRUCT_TYPE_INFO","alias":"","modifiers":[],"child_types":[{"first":"DisplayName","second":{"id":"VARCHAR","type_info":null}},{"first":"ID","second":{"id":"VARCHAR","type_info":null}}]}},"is_null":false,"value":{"children":[{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"test2"},{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"v2"}]}}}]},{"expression_class":"BOUND_COMPARISON","type":"COMPARE_EQUAL","alias":"","query_location":18446744073709551615,"left":{"expression_class":"BOUND_COLUMN_REF","type":"BOUND_COLUMN_REF","alias":"aws_region","query_location":18446744073709551615,"return_type":{"id":"VARCHAR","type_info":null},"binding":{"table_index":0,"column_index":0},"depth":0},"right":{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"us-east-1"}}}],"column_binding_names_by_index":["aws_region","Owner","Buckets","aws_profile_name"]}',
            "\"Owner\" NOT IN ({'DisplayName':'test','ID':'v'}, {'DisplayName':'test2','ID':'v2'}) AND \"aws_region\" = 'us-east-1'",
            owner_type_info,
        ),
        (
            '{"filters":[{"expression_class":"BOUND_BETWEEN","type":"COMPARE_BETWEEN","alias":"","query_location":18446744073709551615,"input":{"expression_class":"BOUND_FUNCTION","type":"BOUND_FUNCTION","alias":"","query_location":70,"return_type":{"id":"VARCHAR","type_info":null},"children":[{"expression_class":"BOUND_COLUMN_REF","type":"BOUND_COLUMN_REF","alias":"Owner","query_location":18446744073709551615,"return_type":{"id":"STRUCT","type_info":{"type":"STRUCT_TYPE_INFO","alias":"","modifiers":[],"child_types":[{"first":"DisplayName","second":{"id":"VARCHAR","type_info":null}},{"first":"ID","second":{"id":"VARCHAR","type_info":null}}]}},"binding":{"table_index":0,"column_index":1},"depth":0},{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"DisplayName"}}],"name":"struct_extract","arguments":[{"id":"STRUCT","type_info":{"type":"STRUCT_TYPE_INFO","alias":"","modifiers":[],"child_types":[{"first":"DisplayName","second":{"id":"VARCHAR","type_info":null}},{"first":"ID","second":{"id":"VARCHAR","type_info":null}}]}},{"id":"VARCHAR","type_info":null}],"original_arguments":[],"has_serialize":false,"is_operator":false},"lower":{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"a"}},"upper":{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"z"}},"lower_inclusive":true,"upper_inclusive":true},{"expression_class":"BOUND_COMPARISON","type":"COMPARE_EQUAL","alias":"","query_location":18446744073709551615,"left":{"expression_class":"BOUND_COLUMN_REF","type":"BOUND_COLUMN_REF","alias":"aws_region","query_location":18446744073709551615,"return_type":{"id":"VARCHAR","type_info":null},"binding":{"table_index":0,"column_index":0},"depth":0},"right":{"expression_class":"BOUND_CONSTANT","type":"VALUE_CONSTANT","alias":"","query_location":18446744073709551615,"value":{"type":{"id":"VARCHAR","type_info":null},"is_null":false,"value":"us-east-1"}}}],"column_binding_names_by_index":["aws_region","Owner","Buckets","aws_profile_name"]}',
            "struct_extract(\"Owner\", 'DisplayName') BETWEEN 'a' AND 'z' AND \"aws_region\" = 'us-east-1'",
            owner_type_info,
        ),
    ],
)
def test_duckdb_json_to_sql(
    json_source: str, expected_sql: str, expected_bound_types: dict[str, Any]
) -> None:
    data = json.loads(json_source)
    result = expression.convert_to_sql(
        source=data["filters"], bound_column_names=data["column_binding_names_by_index"]
    )
    assert result[0] == expected_sql
    assert result[1] == expected_bound_types
