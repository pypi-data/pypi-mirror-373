import json
import os
import shutil
import tempfile
import urllib.request
from collections.abc import Iterator
from typing import Any

from dotevals.datasets import Dataset


class BFCL(Dataset):
    """Berkeley Function Calling Leaderboard (BFCL) dataset for evaluating function calling capabilities.

    This dataset tests models' ability to correctly call functions with appropriate parameters
    based on user queries. It includes simple, multiple, and parallel function calling scenarios.
    """

    name = "bfcl"
    variants = ["simple", "multiple", "parallel"]
    columns = ["question", "schema", "answer"]

    def __init__(self, variant: str = "simple", **kwargs: object) -> None:
        if variant not in self.variants:
            raise ValueError(
                f"Variant '{variant}' not supported. Choose from: {', '.join(self.variants)}"
            )

        self.variant = variant

        # Create temporary directory for downloads
        self.temp_dir = tempfile.mkdtemp()

        # Download both question and answer files
        base_url = "https://huggingface.co/datasets/gorilla-llm/Berkeley-Function-Calling-Leaderboard/raw/main"
        question_url = f"{base_url}/BFCL_v3_{variant}.json"
        answer_url = f"{base_url}/possible_answer/BFCL_v3_{variant}.json"

        question_path = os.path.join(self.temp_dir, f"questions_{variant}.json")
        answer_path = os.path.join(self.temp_dir, f"answers_{variant}.json")

        try:
            print(f"Downloading BFCL {variant} dataset...")
            urllib.request.urlretrieve(question_url, question_path)
            urllib.request.urlretrieve(answer_url, answer_path)

            # Load and merge data
            self.data = self._load_and_merge_data(question_path, answer_path)
            self.num_rows = len(self.data)

        except Exception as e:
            import shutil

            shutil.rmtree(self.temp_dir)
            raise RuntimeError(f"Failed to download BFCL dataset: {e}") from e

    def __del__(self) -> None:
        """Clean up temporary directory"""
        if hasattr(self, "temp_dir") and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _load_and_merge_data(
        self, question_path: str, answer_path: str
    ) -> list[dict[str, Any]]:
        """Load question and answer files and merge them by ID."""
        # Load questions
        questions = {}
        with open(question_path) as f:
            for line in f:
                item = json.loads(line.strip())
                questions[item["id"]] = item

        # Load answers
        answers = {}
        with open(answer_path) as f:
            for line in f:
                item = json.loads(line.strip())
                answers[item["id"]] = item

        # Merge data
        merged_data = []
        for item_id, question_item in questions.items():
            if item_id in answers:
                merged_data.append(
                    {
                        "id": item_id,
                        "question": question_item["question"],
                        "function": question_item["function"],
                        "ground_truth": answers[item_id]["ground_truth"],
                    }
                )

        return merged_data

    def _sanitize_schema_types(self, obj: Any) -> Any:
        """Recursively sanitize schema 'type' fields for JSON Schema compatibility.
        - 'float' → 'number'
        - 'dict' → 'object'
        - 'tuple' → 'array'
        - 'any' → 'object'
        Also ensures that any object with type 'array' includes an 'items' key (defaulting to {}).
        """
        if isinstance(obj, dict):
            new_obj = {}
            for k, v in obj.items():
                if k == "type":
                    if v == "float":
                        new_obj[k] = "number"
                    elif v == "dict":
                        new_obj[k] = "object"
                    elif v == "tuple":
                        new_obj[k] = "array"
                    elif v == "any":
                        new_obj[k] = "object"
                    else:
                        new_obj[k] = v
                else:
                    new_obj[k] = self._sanitize_schema_types(v)
            # Only add 'items' if type == 'array'
            if new_obj.get("type") == "array" and "items" not in new_obj:
                new_obj["items"] = {}  # type: ignore[assignment]
            return new_obj
        elif isinstance(obj, list):
            return [self._sanitize_schema_types(i) for i in obj]
        else:
            return obj

    def _convert_to_json_schema(
        self, functions: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Convert BFCL function format to valid JSON Schema.

        Returns a list of JSON Schema objects, one for each function.
        """
        if not functions:
            # Return empty list if no functions
            return []

        json_schemas = []

        for func in functions:
            # Create a JSON Schema for each function
            func_schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "function": {
                        "type": "string",
                        "const": func["name"],
                    },
                    "arguments": func.get(
                        "parameters",
                        {"type": "object", "properties": {}, "required": []},
                    ),
                },
                "required": ["function", "arguments"],
                "additionalProperties": False,
                "title": func["name"],
                "description": func.get("description", ""),
            }

            # Recursively sanitize all types in the schema
            func_schema = self._sanitize_schema_types(func_schema)

            json_schemas.append(func_schema)

        return json_schemas

    def _make_hashable(self, obj: Any) -> Any:
        """Recursively convert lists in obj to tuples so they are hashable."""
        if isinstance(obj, list):
            return tuple(self._make_hashable(v) for v in obj)
        elif isinstance(obj, dict):
            return tuple(sorted((k, self._make_hashable(v)) for k, v in obj.items()))
        else:
            return obj

    def _process_ground_truth(
        self, ground_truth: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Process ground truth to convert arrays of alternatives to sets.

        Arrays in BFCL answers can represent multiple valid values for a parameter.
        This method converts them to sets for clearer semantics, except when
        the parameter value itself should be a list (e.g., coordinates).

        Empty strings in arrays indicate the parameter is optional and are removed.

        """
        processed = []

        for func_call in ground_truth:
            processed_call = {}
            for func_name, params in func_call.items():
                processed_params = {}

                for param_name, values in params.items():
                    # Remove empty strings (they indicate optional parameters)
                    non_empty = [v for v in values if v != ""]

                    if not non_empty:
                        # All values were empty strings - skip this parameter
                        continue
                    elif len(non_empty) == 1:
                        # Single valid value - use it directly
                        processed_params[param_name] = non_empty[0]
                    else:
                        # Multiple valid values - use a set
                        # Unless all values are lists (then it's a list parameter with alternatives)
                        if all(isinstance(v, list) for v in non_empty):
                            # This is a list parameter with multiple valid list values
                            # Convert to set of tuples for hashability
                            processed_params[param_name] = {
                                self._make_hashable(v) for v in non_empty
                            }
                        elif all(isinstance(v, dict) for v in non_empty):
                            # This is a parameter with multiple valid dict values
                            # Convert to set of tuples for hashability
                            processed_params[param_name] = {
                                self._make_hashable(v) for v in non_empty
                            }
                        else:
                            # Regular multiple choice parameter
                            processed_params[param_name] = set(non_empty)

                processed_call[func_name] = processed_params
            processed.append(processed_call)

        return processed  # type: ignore[return-value]

    def __iter__(
        self,
    ) -> Iterator[tuple[str, list[dict[str, Any]], list[dict[str, Any]]]]:
        for item in self.data:
            # Extract the user question from the conversation format
            # Questions are in format: [[{"role": "user", "content": "..."}]]
            question_text = ""
            if item["question"] and len(item["question"]) > 0:
                first_turn = item["question"][0]
                if isinstance(first_turn, list) and len(first_turn) > 0:
                    if isinstance(first_turn[0], dict) and "content" in first_turn[0]:
                        question_text = first_turn[0]["content"]

            # Convert function schemas to valid JSON Schema
            schema = self._convert_to_json_schema(item["function"])

            # Process ground truth to use sets for multiple valid values
            answer = self._process_ground_truth(item["ground_truth"])

            yield (question_text, schema, answer)

    def _serialize_value(self, value: object) -> object:
        """Serialize sets to JSON-compatible format."""
        if isinstance(value, set):
            return {"__type__": "set", "data": list(value)}
        elif isinstance(value, tuple):
            return {"__type__": "tuple", "data": list(value)}
        return super()._serialize_value(value)

    def _deserialize_value(self, value: object) -> object:
        """Restore sets from JSON-compatible format."""
        if isinstance(value, dict) and "__type__" in value:
            type_name = value["__type__"]

            if type_name == "set":
                return set(value["data"])
            elif type_name == "tuple":
                return tuple(value["data"])

        return super()._deserialize_value(value)
