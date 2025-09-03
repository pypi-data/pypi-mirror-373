"""Tests for BFCL dataset loader."""

import json
import os
import tempfile
from unittest.mock import patch

import pytest
from dotevals.datasets.registry import registry as _registry

from dotevals_datasets.bfcl import BFCL


def test_bfcl_dataset_attributes():
    """Test BFCL dataset has correct attributes."""
    assert BFCL.name == "bfcl"
    assert BFCL.variants == ["simple", "multiple", "parallel"]
    assert BFCL.columns == ["question", "schema", "answer"]


def test_bfcl_auto_registration():
    """Test BFCL dataset is automatically registered."""
    assert "bfcl" in _registry.list_datasets()
    dataset_class = _registry.get_dataset_class("bfcl")
    assert dataset_class == BFCL


def test_bfcl_invalid_variant():
    """Test BFCL raises error for invalid variant."""
    with pytest.raises(ValueError, match="Variant 'invalid' not supported"):
        BFCL(variant="invalid")


@patch("urllib.request.urlretrieve")
def test_bfcl_download_and_merge(mock_urlretrieve):
    """Test BFCL dataset download and data merging."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create mock question data
        question_data = [
            {
                "id": "simple_0",
                "question": [
                    [{"role": "user", "content": "Calculate the area of a triangle"}]
                ],
                "function": [
                    {"name": "calculate_area", "parameters": {"base": "number"}}
                ],
            },
            {
                "id": "simple_1",
                "question": [[{"role": "user", "content": "Get weather information"}]],
                "function": [{"name": "get_weather", "parameters": {"city": "string"}}],
            },
        ]

        # Create mock answer data
        answer_data = [
            {
                "id": "simple_0",
                "ground_truth": [{"calculate_area": {"base": [10], "height": [5]}}],
            },
            {
                "id": "simple_1",
                "ground_truth": [{"get_weather": {"city": ["New York"]}}],
            },
        ]

        # Mock urlretrieve to create test files
        def mock_urlretrieve_side_effect(url, path):
            if "possible_answer" in url:
                # Write answer file
                with open(path, "w") as f:
                    for item in answer_data:
                        f.write(json.dumps(item) + "\n")
            else:
                # Write question file
                with open(path, "w") as f:
                    for item in question_data:
                        f.write(json.dumps(item) + "\n")

        mock_urlretrieve.side_effect = mock_urlretrieve_side_effect

        # Patch mkdtemp to use our test directory
        with patch("tempfile.mkdtemp", return_value=temp_dir):
            dataset = BFCL(variant="simple")

            # Check dataset attributes
            assert dataset.num_rows == 2
            assert dataset.variant == "simple"

            # Test iteration
            results = list(dataset)
            assert len(results) == 2

            # Check first item
            question, schema, answer = results[0]
            assert question == "Calculate the area of a triangle"
            assert "calculate_area" == schema[0]["properties"]["function"]["const"]
            assert "calculate_area" in answer[0]

            # Check second item
            question, schema, answer = results[1]
            assert question == "Get weather information"
            assert "get_weather" == schema[0]["properties"]["function"]["const"]
            assert "get_weather" in answer[0]


@patch("urllib.request.urlretrieve")
def test_bfcl_different_variants(mock_urlretrieve):
    """Test loading different BFCL variants."""

    def mock_urlretrieve_side_effect(url, path):
        # Create empty but valid JSON files
        with open(path, "w") as f:
            f.write("")

    mock_urlretrieve.side_effect = mock_urlretrieve_side_effect

    for variant in ["simple", "multiple", "parallel"]:
        with patch("tempfile.mkdtemp", return_value=tempfile.mkdtemp()):
            dataset = BFCL(variant=variant)
            assert dataset.variant == variant

            # Verify correct URLs were called
            calls = mock_urlretrieve.call_args_list[-2:]  # Last 2 calls
            question_url = calls[0][0][0]
            answer_url = calls[1][0][0]

            assert f"BFCL_v3_{variant}.json" in question_url
            assert f"possible_answer/BFCL_v3_{variant}.json" in answer_url


@patch("urllib.request.urlretrieve", side_effect=Exception("Download failed"))
def test_bfcl_download_failure(mock_urlretrieve):
    """Test BFCL behavior when download fails."""
    with pytest.raises(RuntimeError, match="Failed to download BFCL dataset"):
        BFCL(variant="simple")


def test_bfcl_cleanup():
    """Test that BFCL cleans up temporary directory."""
    with patch("urllib.request.urlretrieve"):
        # Create valid JSONL files when urlretrieve is called
        def mock_urlretrieve(url, path):
            with open(path, "w") as f:
                # Write valid JSONL format (one JSON object per line)
                if "possible_answer" in url:
                    f.write('{"id": "test_0", "ground_truth": [{"func": {}}]}\n')
                else:
                    f.write(
                        '{"id": "test_0", "question": [[{"role": "user", "content": "test"}]], "function": [{"name": "func"}]}\n'
                    )

        with patch("urllib.request.urlretrieve", side_effect=mock_urlretrieve):
            dataset = BFCL(variant="simple")
            temp_dir = dataset.temp_dir

            # Directory should exist
            assert os.path.exists(temp_dir)

            # Delete the dataset
            del dataset

            # Directory should be cleaned up
            assert not os.path.exists(temp_dir)


@patch("urllib.request.urlretrieve")
def test_bfcl_complex_question_format(mock_urlretrieve):
    """Test BFCL handles complex question formats correctly."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test different question formats
        question_data = [
            {
                "id": "test_0",
                "question": [[{"role": "user", "content": "Normal question"}]],
                "function": [{"name": "func1"}],
            },
            {
                "id": "test_1",
                "question": [[]],  # Empty conversation
                "function": [{"name": "func2"}],
            },
            {
                "id": "test_2",
                "question": [],  # No conversation
                "function": [{"name": "func3"}],
            },
        ]

        answer_data = [
            {"id": "test_0", "ground_truth": [{"func1": {}}]},
            {"id": "test_1", "ground_truth": [{"func2": {}}]},
            {"id": "test_2", "ground_truth": [{"func3": {}}]},
        ]

        def mock_urlretrieve_side_effect(url, path):
            if "possible_answer" in url:
                with open(path, "w") as f:
                    for item in answer_data:
                        f.write(json.dumps(item) + "\n")
            else:
                with open(path, "w") as f:
                    for item in question_data:
                        f.write(json.dumps(item) + "\n")

        mock_urlretrieve.side_effect = mock_urlretrieve_side_effect

        with patch("tempfile.mkdtemp", return_value=temp_dir):
            dataset = BFCL(variant="simple")
            results = list(dataset)

            assert len(results) == 3
            # Check that empty questions are handled gracefully
            assert results[0][0] == "Normal question"
            assert results[1][0] == ""  # Empty conversation
            assert results[2][0] == ""  # No conversation


def test_bfcl_process_ground_truth_unhashable_list():
    """Test that _process_ground_truth handles nested lists by converting them to hashable tuples."""
    dataset = BFCL.__new__(BFCL)

    ground_truth = [{"func": {"param": [[[1, 2]], [[3, 4]]]}}]
    result = dataset._process_ground_truth(ground_truth)

    expected = [{"func": {"param": {((1, 2),), ((3, 4),)}}}]
    assert result == expected


def test_bfcl_process_ground_truth_dict_in_list():
    """Test that _process_ground_truth handles list of dicts by converting dicts to sorted tuples."""
    dataset = BFCL.__new__(BFCL)
    ground_truth = [{"func": {"param": [{"a": 1, "b": [2, 3]}, {"a": 4, "b": [5, 6]}]}}]
    result = dataset._process_ground_truth(ground_truth)
    expected = [
        {"func": {"param": {(("a", 1), ("b", (2, 3))), (("a", 4), ("b", (5, 6)))}}}
    ]
    assert result == expected


def test_bfcl_schema_float_to_number():
    """Test that 'float' types in function parameters are converted to 'number' in the schema."""

    functions = [
        {
            "name": "add",
            "parameters": {
                "type": "object",
                "properties": {"x": {"type": "float"}, "y": {"type": "float"}},
                "required": ["x", "y"],
            },
            "description": "Add two numbers.",
        }
    ]
    dataset = BFCL.__new__(BFCL)
    schema = dataset._convert_to_json_schema(functions)

    props = schema[0]["properties"]["arguments"]["properties"]
    assert props["x"]["type"] == "number"
    assert props["y"]["type"] == "number"


def test_bfcl_schema_array_items_added_if_missing():
    """Test that 'array' (tuple) types without 'items' get 'items': {} added in the schema."""
    dataset = BFCL.__new__(BFCL)
    # Single 'array' type (from 'tuple')
    functions = [
        {
            "name": "array_func",
            "parameters": {
                "type": "object",
                "properties": {"values": {"type": "tuple"}},  # No 'items' key
                "required": ["values"],
            },
        }
    ]
    schema = dataset._convert_to_json_schema(functions)
    props = schema[0]["properties"]["arguments"]["properties"]
    assert props["values"]["type"] == "array"
    assert "items" in props["values"]
    assert props["values"]["items"] == {}

    # 'array' in a type list
    functions_union = [
        {
            "name": "union_array_func",
            "parameters": {
                "type": "object",
                "properties": {
                    "values": {
                        "type": ["string", "array"],
                        "description": "Union type with array",
                    }
                },
                "required": ["values"],
            },
        }
    ]
    schema_union = dataset._convert_to_json_schema(functions_union)
    props_union = schema_union[0]["properties"]["arguments"]["properties"]
    assert props_union["values"]["type"] == ["string", "array"]
    assert props_union["values"]["description"] == "Union type with array"

    # type list with pre-existing items (should keep items for type list)
    functions_with_items = [
        {
            "name": "preexisting_items",
            "parameters": {
                "type": "object",
                "properties": {
                    "values": {
                        "type": ["string", "array"],
                        "items": {"type": "number"},
                        "description": "Should keep items for type list",
                    }
                },
                "required": ["values"],
            },
        }
    ]
    schema_with_items = dataset._convert_to_json_schema(functions_with_items)
    props_with_items = schema_with_items[0]["properties"]["arguments"]["properties"]
    assert props_with_items["values"]["type"] == ["string", "array"]
    assert props_with_items["values"]["items"] == {"type": "number"}
    assert (
        props_with_items["values"]["description"] == "Should keep items for type list"
    )


def test_bfcl_schema_type_sanitization():
    """Test that 'dict', 'tuple', 'float', and 'any' types are sanitized in function schemas, including nested and combined cases."""
    dataset = BFCL.__new__(BFCL)

    # dict → object (including nested)
    functions_dict = [
        {
            "name": "store",
            "parameters": {
                "type": "dict",
                "properties": {
                    "meta": {"type": "dict"},
                    "info": {"type": "string"},
                },
                "required": ["meta", "info"],
            },
        }
    ]
    schema = dataset._convert_to_json_schema(functions_dict)
    args = schema[0]["properties"]["arguments"]
    assert args["type"] == "object"
    assert args["properties"]["meta"]["type"] == "object"
    assert args["properties"]["info"]["type"] == "string"

    # tuple → array (including nested)
    functions_tuple = [
        {
            "name": "coords",
            "parameters": {
                "type": "object",
                "properties": {
                    "coord1": {"type": "tuple", "items": {"type": "number"}},
                    "coord2": {"type": "tuple", "items": {"type": "number"}},
                },
                "required": ["coord1", "coord2"],
            },
        }
    ]
    schema = dataset._convert_to_json_schema(functions_tuple)
    props = schema[0]["properties"]["arguments"]["properties"]
    assert props["coord1"]["type"] == "array"
    assert props["coord2"]["type"] == "array"
    assert props["coord1"]["items"]["type"] == "number"

    # any → object
    functions_any = [
        {
            "name": "process",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {"type": "any"},
                },
                "required": ["data"],
            },
        }
    ]
    schema = dataset._convert_to_json_schema(functions_any)
    props = schema[0]["properties"]["arguments"]["properties"]
    assert props["data"]["type"] == "object"

    # Combined: dict, tuple, float, any
    functions_combined = [
        {
            "name": "complex",
            "parameters": {
                "type": "dict",
                "properties": {
                    "location": {"type": "tuple", "items": {"type": "float"}},
                    "meta": {"type": "dict", "properties": {"flag": {"type": "any"}}},
                },
                "required": ["location", "meta"],
            },
        }
    ]
    schema = dataset._convert_to_json_schema(functions_combined)
    args = schema[0]["properties"]["arguments"]
    assert args["type"] == "object"
    assert args["properties"]["location"]["type"] == "array"
    assert args["properties"]["location"]["items"]["type"] == "number"
    assert args["properties"]["meta"]["type"] == "object"
    assert args["properties"]["meta"]["properties"]["flag"]["type"] == "object"
