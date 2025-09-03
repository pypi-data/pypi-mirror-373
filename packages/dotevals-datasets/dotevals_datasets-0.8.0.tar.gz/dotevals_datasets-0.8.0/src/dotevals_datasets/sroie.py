import base64
import io
from collections.abc import Iterator

from dotevals.datasets import Dataset
from PIL import Image


class SROIE(Dataset):
    """SROIE dataset for receipt information extraction

    This dataset tests the ability of models to extract key information
    from digitized receipts including company name, address, date, and total amount.
    """

    name = "sroie"
    splits = ["train", "test"]
    columns = ["images", "address", "company", "date", "total"]

    def __init__(self, split: str, **kwargs: object) -> None:
        # Lazy import to avoid circular import issues
        import datasets as hf_datasets

        # Load streaming dataset and get metadata
        self.dataset = hf_datasets.load_dataset(
            "sizhkhy/SROIE", split=split, streaming=True
        )
        self.num_rows = self.dataset.info.splits[split].num_examples

    def __iter__(self) -> Iterator[tuple[Image.Image, str, str, str, str]]:
        for item in self.dataset:
            image = item["images"]
            address = item["fields"]["ADDRESS"]
            company = item["fields"]["COMPANY"]
            date = item["fields"]["DATE"]
            total = item["fields"]["TOTAL"]

            yield (image, address, company, date, total)

    def _serialize_value(self, value: object) -> object:
        """Serialize PIL Images to JSON-compatible format."""
        if isinstance(value, Image.Image):
            buffered = io.BytesIO()
            value.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            return {
                "__type__": "PIL.Image",
                "data": img_base64,
                "mode": value.mode,
                "size": value.size,
            }
        return super()._serialize_value(value)

    def _deserialize_value(self, value: object) -> object:
        """Restore PIL Images from JSON-compatible format."""
        if isinstance(value, dict) and "__type__" in value:
            type_name = value["__type__"]

            if type_name == "PIL.Image":
                img_data = base64.b64decode(value["data"])
                return Image.open(io.BytesIO(img_data))

        return super()._deserialize_value(value)
