"""Tests for GSM8K dataset loader."""

from unittest.mock import MagicMock, patch

import pytest
from dotevals.datasets.registry import registry as _registry

from dotevals_datasets.gsm8k import GSM8K


def test_gsm8k_dataset_attributes():
    """Test GSM8K dataset has correct attributes."""
    assert GSM8K.name == "gsm8k"
    assert GSM8K.splits == ["train", "test"]
    assert GSM8K.columns == ["question", "reasoning", "answer"]


def test_gsm8k_auto_registration():
    """Test GSM8K dataset is automatically registered."""
    assert "gsm8k" in _registry.list_datasets()
    dataset_class = _registry.get_dataset_class("gsm8k")
    assert dataset_class == GSM8K


@patch("datasets.load_dataset")
def test_gsm8k_load_basic(mock_load_dataset):
    """Test basic GSM8K loading functionality."""
    mock_dataset = MagicMock()
    mock_dataset.info.splits = {"test": MagicMock(num_examples=2)}
    mock_dataset.__iter__ = lambda self: iter(
        [
            {"question": "What is 2+2?", "answer": "2+2=4\n#### 4"},
            {"question": "What is 3+3?", "answer": "No answer format"},
        ]
    )
    mock_load_dataset.return_value = mock_dataset

    dataset = GSM8K("test")
    results = list(dataset)

    # Should extract valid answers only
    assert len(results) == 1
    assert results[0] == ("What is 2+2?", "2+2=4", "4")

    # Should call datasets.load_dataset correctly
    mock_load_dataset.assert_called_once_with(
        "openai/gsm8k", "main", split="test", streaming=True
    )


@pytest.mark.parametrize(
    "answer_text,expected_reasoning,expected_answer",
    [
        ("Simple.\n#### 42", "Simple.", "42"),
        ("Negative.\n#### -15", "Negative.", "-15"),
        ("With comma.\n#### 1,234", "With comma.", "1,234"),
        (
            "Multiple lines\nof reasoning\n#### 100",
            "Multiple lines\nof reasoning",
            "100",
        ),
        ("#### 0", "", "0"),  # No reasoning, just answer
        ("No marker", None, None),
    ],
)
@patch("datasets.load_dataset")
def test_gsm8k_answer_extraction(
    mock_load_dataset, answer_text, expected_reasoning, expected_answer
):
    """Test answer extraction regex patterns."""
    mock_dataset = MagicMock()
    mock_dataset.info.splits = {"test": MagicMock(num_examples=1)}
    mock_dataset.__iter__ = lambda self: iter(
        [{"question": "Test", "answer": answer_text}]
    )
    mock_load_dataset.return_value = mock_dataset

    dataset = GSM8K("test")
    results = list(dataset)

    if expected_answer is not None:
        assert len(results) == 1
        assert results[0][1] == expected_reasoning  # reasoning
        assert results[0][2] == expected_answer  # answer
    else:
        assert len(results) == 0


@patch("datasets.load_dataset")
def test_gsm8k_different_splits(mock_load_dataset):
    """Test loading different splits."""
    mock_dataset = MagicMock()
    mock_dataset.info.splits = {
        "train": MagicMock(num_examples=0),
        "test": MagicMock(num_examples=0),
    }
    mock_dataset.__iter__ = lambda self: iter([])
    mock_load_dataset.return_value = mock_dataset

    dataset_train = GSM8K("train")
    list(dataset_train)
    mock_load_dataset.assert_called_with(
        "openai/gsm8k", "main", split="train", streaming=True
    )

    dataset_test = GSM8K("test")
    list(dataset_test)
    mock_load_dataset.assert_called_with(
        "openai/gsm8k", "main", split="test", streaming=True
    )


@patch("datasets.load_dataset", side_effect=ImportError("datasets not available"))
def test_gsm8k_missing_dependency(mock_load_dataset):
    """Test behavior when datasets library is missing."""
    with pytest.raises(ImportError):
        GSM8K("test")
