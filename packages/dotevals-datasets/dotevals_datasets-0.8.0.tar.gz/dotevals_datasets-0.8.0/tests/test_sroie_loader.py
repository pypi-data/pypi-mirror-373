"""Tests for SROIE dataset loader."""

from unittest.mock import MagicMock, patch

import pytest
from dotevals.datasets.registry import registry as _registry
from PIL import Image

from dotevals_datasets.sroie import SROIE


def test_sroie_dataset_attributes():
    """Test SROIE dataset has correct attributes."""
    assert SROIE.name == "sroie"
    assert SROIE.splits == ["train", "test"]
    assert SROIE.columns == ["images", "address", "company", "date", "total"]


def test_sroie_auto_registration():
    """Test SROIE dataset is automatically registered."""
    assert "sroie" in _registry.list_datasets()
    dataset_class = _registry.get_dataset_class("sroie")
    assert dataset_class == SROIE


@patch("datasets.load_dataset")
def test_sroie_load_basic(mock_load_dataset):
    """Test basic SROIE loading functionality."""
    mock_image = Image.new("RGB", (100, 100), color="white")

    mock_dataset = MagicMock()
    mock_dataset.info.splits = {"test": MagicMock(num_examples=2)}
    mock_dataset.__iter__ = lambda self: iter(
        [
            {
                "images": mock_image,
                "fields": {
                    "ADDRESS": "123 Test Street",
                    "COMPANY": "Test Company",
                    "DATE": "2024-01-01",
                    "TOTAL": "10.50",
                },
            },
            {
                "images": mock_image,
                "fields": {
                    "ADDRESS": "456 Another Ave",
                    "COMPANY": "Another Company",
                    "DATE": "2024-01-02",
                    "TOTAL": "25.75",
                },
            },
        ]
    )
    mock_load_dataset.return_value = mock_dataset

    dataset = SROIE("test")
    results = list(dataset)

    # Should return all items
    assert len(results) == 2

    # Check first item
    image1, address1, company1, date1, total1 = results[0]
    assert isinstance(image1, Image.Image)
    assert image1.size == (100, 100)
    assert address1 == "123 Test Street"
    assert company1 == "Test Company"
    assert date1 == "2024-01-01"
    assert total1 == "10.50"

    # Check second item
    image2, address2, company2, date2, total2 = results[1]
    assert isinstance(image2, Image.Image)
    assert image2.size == (100, 100)
    assert address2 == "456 Another Ave"
    assert company2 == "Another Company"
    assert date2 == "2024-01-02"
    assert total2 == "25.75"

    # Should call datasets.load_dataset correctly
    mock_load_dataset.assert_called_once_with(
        "sizhkhy/SROIE", split="test", streaming=True
    )


@patch("datasets.load_dataset")
def test_sroie_different_splits(mock_load_dataset):
    """Test loading different splits."""
    mock_dataset = MagicMock()
    mock_dataset.info.splits = {
        "train": MagicMock(num_examples=0),
        "test": MagicMock(num_examples=0),
    }
    mock_dataset.__iter__ = lambda self: iter([])
    mock_load_dataset.return_value = mock_dataset

    dataset_train = SROIE("train")
    list(dataset_train)
    mock_load_dataset.assert_called_with("sizhkhy/SROIE", split="train", streaming=True)

    dataset_test = SROIE("test")
    list(dataset_test)
    mock_load_dataset.assert_called_with("sizhkhy/SROIE", split="test", streaming=True)


@patch("datasets.load_dataset", side_effect=ImportError("datasets not available"))
def test_sroie_missing_dependency(mock_load_dataset):
    """Test behavior when datasets library is missing."""
    with pytest.raises(ImportError):
        SROIE("test")
