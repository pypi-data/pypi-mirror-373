from __future__ import annotations

from collections.abc import Iterator

from dotevals.datasets import Dataset


class HumanEval(Dataset):
    """HumanEval dataset iterator"""

    name = "humaneval"
    columns = ["prompt", "canonical_solution", "test", "entry_point"]

    def __init__(self, **kwargs: object) -> None:
        # Lazy import to avoid circular import issues
        import datasets as hf_datasets

        # Load streaming dataset and get metadata
        self.dataset = hf_datasets.load_dataset(
            "openai/openai_humaneval", split="test", streaming=True
        )
        self.num_rows = self.dataset.info.splits["test"].num_examples

    def __iter__(self) -> Iterator[tuple[str, str, str, str]]:
        for item in self.dataset:
            prompt = item["prompt"]
            canonical_solution = item["canonical_solution"]
            test = item["test"]
            entry_point = item["entry_point"]

            yield (prompt, canonical_solution, test, entry_point)
