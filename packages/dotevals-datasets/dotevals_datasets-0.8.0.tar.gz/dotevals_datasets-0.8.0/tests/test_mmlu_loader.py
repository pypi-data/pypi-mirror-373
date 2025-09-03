"""Tests for MMLU dataset loader."""

from unittest.mock import MagicMock, patch

import pytest
from dotevals.datasets.registry import registry as _registry

from dotevals_datasets.mmlu import AVAILABLE_SUBJECTS, MMLU


def test_mmlu_dataset_attributes():
    """Test MMLU dataset has correct attributes."""
    assert MMLU.name == "mmlu"
    assert MMLU.splits == ["test", "validation", "dev"]
    assert MMLU.columns == ["question", "subject", "choices", "answer"]


def test_mmlu_auto_registration():
    """Test MMLU dataset is automatically registered."""
    assert "mmlu" in _registry.list_datasets()
    dataset_class = _registry.get_dataset_class("mmlu")
    assert dataset_class == MMLU


def test_mmlu_available_subjects():
    """Test that we have the expected number of subjects."""
    assert len(AVAILABLE_SUBJECTS) == 57
    assert "college_mathematics" in AVAILABLE_SUBJECTS
    assert "abstract_algebra" in AVAILABLE_SUBJECTS
    assert "world_religions" in AVAILABLE_SUBJECTS


@patch("datasets.load_dataset")
def test_mmlu_all_subjects_load(mock_load_dataset):
    """Test loading all subjects (mmlu() syntax)."""
    mock_dataset = MagicMock()
    mock_dataset.info.splits = {"test": MagicMock(num_examples=100)}
    mock_dataset.__iter__ = lambda self: iter(
        [
            {
                "question": "What is 2+2?",
                "subject": "elementary_mathematics",
                "choices": ["3", "4", "5", "6"],
                "answer": 1,
            },
            {
                "question": "What is photosynthesis?",
                "subject": "biology",
                "choices": ["A process", "A disease", "A theory", "A law"],
                "answer": 0,
            },
        ]
    )
    mock_load_dataset.return_value = mock_dataset

    # Test mmlu() - all subjects
    dataset = MMLU("test")
    results = list(dataset)

    # Should get all items with subject column
    assert len(results) == 2
    assert len(results[0]) == 4  # question, subject, choices, answer
    assert results[0][0] == "What is 2+2?"  # question
    assert results[0][1] == "elementary_mathematics"  # subject
    assert results[0][2] == ["3", "4", "5", "6"]  # choices
    assert results[0][3] == 1  # answer

    # Should call datasets.load_dataset with "all" config
    mock_load_dataset.assert_called_once_with(
        "cais/mmlu", "all", split="test", streaming=True
    )


@patch("datasets.load_dataset")
def test_mmlu_specific_subject_load(mock_load_dataset):
    """Test loading specific subject (mmlu[subject]() syntax)."""
    mock_dataset = MagicMock()
    mock_dataset.info.splits = {"test": MagicMock(num_examples=50)}
    mock_dataset.__iter__ = lambda self: iter(
        [
            {
                "question": "What is calculus?",
                "subject": "college_mathematics",  # This gets filtered out
                "choices": ["Math branch", "Physics", "Chemistry", "Biology"],
                "answer": 0,
            }
        ]
    )
    mock_load_dataset.return_value = mock_dataset

    # Test mmlu["college_mathematics"]() - specific subject
    # Don't create MMLU() instance to avoid extra mock calls
    from dotevals_datasets.mmlu import MMLUSubject

    subject_factory = MMLUSubject("college_mathematics")
    dataset = subject_factory("test")
    results = list(dataset)

    # Should get items without subject column
    assert len(results) == 1
    assert len(results[0]) == 3  # question, choices, answer (no subject)
    assert results[0][0] == "What is calculus?"  # question
    assert results[0][1] == [
        "Math branch",
        "Physics",
        "Chemistry",
        "Biology",
    ]  # choices
    assert results[0][2] == 0  # answer

    # Should call datasets.load_dataset with specific subject
    mock_load_dataset.assert_called_once_with(
        "cais/mmlu", "college_mathematics", split="test", streaming=True
    )


def test_mmlu_subject_validation():
    """Test that invalid subjects raise errors."""
    mmlu = MMLU()

    with pytest.raises(ValueError, match="Subject 'invalid_subject' not available"):
        mmlu["invalid_subject"]


def test_mmlu_subject_factory_attributes():
    """Test MMLUSubject factory has correct behavior."""
    mmlu = MMLU()
    subject_factory = mmlu["college_mathematics"]

    # Test default split
    dataset_default = subject_factory()
    assert dataset_default.subject == "college_mathematics"
    assert dataset_default.split == "test"

    # Test explicit split
    dataset_val = subject_factory("validation")
    assert dataset_val.subject == "college_mathematics"
    assert dataset_val.split == "validation"


@patch("datasets.load_dataset")
def test_mmlu_different_splits(mock_load_dataset):
    """Test loading different splits."""
    # Setup mock for validation split
    mock_dataset_val = MagicMock()
    mock_dataset_val.info.splits = {"validation": MagicMock(num_examples=10)}
    mock_dataset_val.__iter__ = lambda self: iter([])

    # Setup mock for dev split
    mock_dataset_dev = MagicMock()
    mock_dataset_dev.info.splits = {"dev": MagicMock(num_examples=5)}
    mock_dataset_dev.__iter__ = lambda self: iter([])

    # Configure mock to return different datasets based on calls
    mock_load_dataset.side_effect = [mock_dataset_val, mock_dataset_dev]

    # Test validation split for all subjects
    dataset_all = MMLU("validation")
    list(dataset_all)

    # Test dev split for specific subject
    from dotevals_datasets.mmlu import MMLUSubject

    subject_factory = MMLUSubject("college_physics")
    dataset_subject = subject_factory("dev")
    list(dataset_subject)

    # Check that the correct calls were made
    assert mock_load_dataset.call_count == 2
    mock_load_dataset.assert_any_call(
        "cais/mmlu", "all", split="validation", streaming=True
    )
    mock_load_dataset.assert_any_call(
        "cais/mmlu", "college_physics", split="dev", streaming=True
    )


@patch("datasets.load_dataset", side_effect=ImportError("datasets not available"))
def test_mmlu_missing_dependency(mock_load_dataset):
    """Test behavior when datasets library is missing."""
    with pytest.raises(ImportError):
        MMLU("test")

    # Also test for subject-specific
    from dotevals_datasets.mmlu import MMLUSubject

    subject_factory = MMLUSubject("college_mathematics")
    with pytest.raises(ImportError):
        subject_factory("test")


def test_mmlu_subject_dataset_attributes():
    """Test MMLUSubjectDataset has correct attributes."""
    from dotevals_datasets.mmlu import MMLUSubjectDataset

    # We can't easily test without mocking, but we can check class attributes
    assert MMLUSubjectDataset.name == "mmlu"
    assert MMLUSubjectDataset.splits == ["test", "validation", "dev"]
    assert MMLUSubjectDataset.columns == ["question", "choices", "answer"]
