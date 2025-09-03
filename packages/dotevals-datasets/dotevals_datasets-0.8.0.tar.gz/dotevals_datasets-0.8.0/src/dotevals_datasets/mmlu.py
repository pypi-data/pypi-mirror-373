from __future__ import annotations

from collections.abc import Iterator

from dotevals.datasets import Dataset

# Available subjects in MMLU dataset
AVAILABLE_SUBJECTS = [
    "abstract_algebra",
    "anatomy",
    "astronomy",
    "business_ethics",
    "clinical_knowledge",
    "college_biology",
    "college_chemistry",
    "college_computer_science",
    "college_mathematics",
    "college_medicine",
    "college_physics",
    "computer_security",
    "conceptual_physics",
    "econometrics",
    "electrical_engineering",
    "elementary_mathematics",
    "formal_logic",
    "global_facts",
    "high_school_biology",
    "high_school_chemistry",
    "high_school_computer_science",
    "high_school_european_history",
    "high_school_geography",
    "high_school_government_and_politics",
    "high_school_macroeconomics",
    "high_school_mathematics",
    "high_school_microeconomics",
    "high_school_physics",
    "high_school_psychology",
    "high_school_statistics",
    "high_school_us_history",
    "high_school_world_history",
    "human_aging",
    "human_sexuality",
    "international_law",
    "jurisprudence",
    "logical_fallacies",
    "machine_learning",
    "management",
    "marketing",
    "medical_genetics",
    "miscellaneous",
    "moral_disputes",
    "moral_scenarios",
    "nutrition",
    "philosophy",
    "prehistory",
    "professional_accounting",
    "professional_law",
    "professional_medicine",
    "professional_psychology",
    "public_relations",
    "security_studies",
    "sociology",
    "us_foreign_policy",
    "virology",
    "world_religions",
]


class MMLUSubject:
    """Factory for creating MMLU datasets for specific subjects."""

    def __init__(self, subject: str) -> None:
        if subject not in AVAILABLE_SUBJECTS:
            raise ValueError(
                f"Subject '{subject}' not available. "
                f"Choose from: {', '.join(AVAILABLE_SUBJECTS)}"
            )
        self.subject = subject

    def __call__(self, split: str = "test") -> MMLUSubjectDataset:
        """Create a dataset instance for this subject and split."""
        return MMLUSubjectDataset(self.subject, split)


class MMLUSubjectDataset(Dataset):
    """MMLU dataset for a specific subject."""

    name = "mmlu"
    splits = ["test", "validation", "dev"]
    columns = ["question", "choices", "answer"]

    def __init__(self, subject: str, split: str = "test", **kwargs: object) -> None:
        # Lazy import to avoid circular import issues
        import datasets as hf_datasets

        self.subject = subject
        self.split = split

        # Load dataset for specific subject
        self.dataset = hf_datasets.load_dataset(
            "cais/mmlu", subject, split=split, streaming=True
        )
        self.num_rows = self.dataset.info.splits[split].num_examples

    def __iter__(self) -> Iterator[tuple[str, list[str], int]]:
        for item in self.dataset:
            question = item["question"]
            choices = item["choices"]
            answer = item["answer"]

            yield (question, choices, answer)


class MMLU(Dataset):
    """MMLU dataset iterator for all subjects."""

    name = "mmlu"
    splits = ["test", "validation", "dev"]
    columns = ["question", "subject", "choices", "answer"]

    def __init__(self, split: str = "test", **kwargs: object) -> None:
        # Lazy import to avoid circular import issues
        import datasets as hf_datasets

        self.split = split

        # Load dataset with "all" config (includes all subjects)
        self.dataset = hf_datasets.load_dataset(
            "cais/mmlu", "all", split=split, streaming=True
        )
        self.num_rows = self.dataset.info.splits[split].num_examples

    def __getitem__(self, subject: str) -> MMLUSubject:
        """Get a subject-specific dataset factory."""
        return MMLUSubject(subject)

    def __iter__(self) -> Iterator[tuple[str, str, list[str], int]]:
        for item in self.dataset:
            question = item["question"]
            subject = item["subject"]
            choices = item["choices"]
            answer = item["answer"]

            yield (question, subject, choices, answer)
