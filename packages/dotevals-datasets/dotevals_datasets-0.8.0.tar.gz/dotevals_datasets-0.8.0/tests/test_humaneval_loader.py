"""Tests for HumanEval dataset loader."""

from unittest.mock import MagicMock, patch

import pytest
from dotevals.datasets.registry import registry as _registry

from dotevals_datasets.humaneval import HumanEval


def test_humaneval_dataset_attributes():
    """Test HumanEval dataset has correct attributes."""
    assert HumanEval.name == "humaneval"
    assert HumanEval.columns == ["prompt", "canonical_solution", "test", "entry_point"]


def test_humaneval_auto_registration():
    """Test HumanEval dataset is automatically registered."""
    assert "humaneval" in _registry.list_datasets()
    dataset_class = _registry.get_dataset_class("humaneval")
    assert dataset_class == HumanEval


@patch("datasets.load_dataset")
def test_humaneval_load_basic(mock_load_dataset):
    """Test basic HumanEval loading functionality."""
    mock_dataset = MagicMock()
    mock_dataset.info.splits = {"test": MagicMock(num_examples=2)}
    mock_dataset.__iter__ = lambda self: iter(
        [
            {
                "task_id": "HumanEval/0",
                "prompt": 'def has_close_elements(numbers, threshold):\n    """Check if two numbers are close."""',
                "canonical_solution": "    for i in range(len(numbers)):\n        return True",
                "test": "def check(candidate):\n    assert candidate([1.0, 2.0], 0.5) == True",
                "entry_point": "has_close_elements",
            },
            {
                "task_id": "HumanEval/1",
                "prompt": 'def separate_paren_groups(paren_string):\n    """Separate groups."""',
                "canonical_solution": "    return []",
                "test": "def check(candidate):\n    assert candidate('()') == ['()']",
                "entry_point": "separate_paren_groups",
            },
        ]
    )
    mock_load_dataset.return_value = mock_dataset

    dataset = HumanEval()
    results = list(dataset)

    # Should get all items
    assert len(results) == 2
    assert "has_close_elements" in results[0][0]  # prompt
    assert "for i in range" in results[0][1]  # canonical_solution
    assert "def check" in results[0][2]  # test
    assert results[0][3] == "has_close_elements"  # entry_point

    # Should call datasets.load_dataset correctly
    mock_load_dataset.assert_called_once_with(
        "openai/openai_humaneval", split="test", streaming=True
    )


@patch("datasets.load_dataset", side_effect=ImportError("datasets not available"))
def test_humaneval_missing_dependency(mock_load_dataset):
    """Test behavior when datasets library is missing."""
    with pytest.raises(ImportError):
        HumanEval()
