from __future__ import annotations

import re
from collections.abc import Iterator

from dotevals.datasets import Dataset


class GSM8K(Dataset):
    """GSM8K dataset iterator"""

    name = "gsm8k"
    splits = ["train", "test"]
    columns = ["question", "reasoning", "answer"]

    def __init__(self, split: str, **kwargs: object) -> None:
        # Lazy import to avoid circular import issues
        import datasets as hf_datasets

        # Load streaming dataset and get metadata
        self.dataset = hf_datasets.load_dataset(
            "openai/gsm8k", "main", split=split, streaming=True
        )
        self.num_rows = self.dataset.info.splits[split].num_examples

        # Extract reasoning and answer with a single regex
        self.answer_rx = re.compile(r"^(.*?)####\s*(\-?[0-9\.\,]+)\s*$", re.DOTALL)

    def __iter__(self) -> Iterator[tuple[str, str, str]]:
        for item in self.dataset:
            question = item["question"]
            full_answer = item["answer"]

            match = self.answer_rx.match(full_answer)
            if match:
                reasoning = match.group(1).strip()
                answer = match.group(2).strip()
                # numeric_match handles commas, so no need to remove them
                yield (question, reasoning, answer)
