"""Integration tests that verify datasets can actually load from remote sources."""

import pytest
from dotevals.datasets.registry import registry as _registry


@pytest.mark.integration
def test_gsm8k_integration():
    """Test GSM8K dataset can load real data from HuggingFace."""
    GSM8K = _registry.get_dataset_class("gsm8k")
    dataset = GSM8K("test")

    # Get first 2 samples
    samples = []
    for i, sample in enumerate(dataset):
        if i >= 2:
            break
        samples.append(sample)

    # Verify we got samples
    assert len(samples) == 2

    # Verify structure
    for sample in samples:
        assert len(sample) == 3  # question, reasoning, answer
        question, reasoning, answer = sample
        assert isinstance(question, str) and len(question) > 0
        assert isinstance(reasoning, str) and len(reasoning) > 0
        assert isinstance(answer, str) and len(answer) > 0


@pytest.mark.integration
def test_humaneval_integration():
    """Test HumanEval dataset can load real data from HuggingFace."""
    HumanEval = _registry.get_dataset_class("humaneval")
    dataset = HumanEval()

    # Get first 2 samples
    samples = []
    for i, sample in enumerate(dataset):
        if i >= 2:
            break
        samples.append(sample)

    # Verify we got samples
    assert len(samples) == 2

    # Verify structure
    for sample in samples:
        assert len(sample) == 4  # prompt, canonical_solution, test, entry_point
        prompt, canonical_solution, test, entry_point = sample
        assert isinstance(prompt, str) and len(prompt) > 0
        assert isinstance(canonical_solution, str) and len(canonical_solution) > 0
        assert isinstance(test, str) and len(test) > 0
        assert isinstance(entry_point, str) and len(entry_point) > 0
        # Verify it's actually code
        assert "def " in prompt
        assert "def check" in test


@pytest.mark.integration
def test_sroie_integration():
    """Test SROIE dataset can load real data from HuggingFace."""
    SROIE = _registry.get_dataset_class("sroie")
    dataset = SROIE("test")

    # Get first 2 samples
    samples = []
    for i, sample in enumerate(dataset):
        if i >= 2:
            break
        samples.append(sample)

    # Verify we got samples
    assert len(samples) == 2

    # Verify structure
    for sample in samples:
        assert len(sample) == 5  # image, address, company, date, total
        image, address, company, date, total = sample
        # Image should be PIL Image
        assert hasattr(image, "size")  # PIL Image has size attribute
        assert isinstance(address, str)
        assert isinstance(company, str)
        assert isinstance(date, str)
        assert isinstance(total, str)


@pytest.mark.integration
def test_bfcl_integration():
    """Test BFCL dataset can load real data from HuggingFace."""
    BFCL = _registry.get_dataset_class("bfcl")
    dataset = BFCL("simple")

    # Get first 2 samples
    samples = []
    for i, sample in enumerate(dataset):
        if i >= 2:
            break
        samples.append(sample)

    # Verify we got samples
    assert len(samples) == 2

    # Verify structure
    for sample in samples:
        assert len(sample) == 3  # question, schema, answer
        question, schema, answer = sample
        assert isinstance(question, str) and len(question) > 0
        assert isinstance(schema, list)
        assert isinstance(answer, list)


@pytest.mark.integration
def test_mmlu_all_subjects_integration():
    """Test MMLU all subjects can load real data from HuggingFace."""
    MMLU = _registry.get_dataset_class("mmlu")
    dataset = MMLU("test")

    # Get first 2 samples
    samples = []
    for i, sample in enumerate(dataset):
        if i >= 2:
            break
        samples.append(sample)

    # Verify we got samples
    assert len(samples) == 2

    # Verify structure
    for sample in samples:
        assert len(sample) == 4  # question, subject, choices, answer
        question, subject, choices, answer = sample
        assert isinstance(question, str) and len(question) > 0
        assert isinstance(subject, str) and len(subject) > 0
        assert isinstance(choices, list) and len(choices) == 4
        assert isinstance(answer, int) and 0 <= answer <= 3
        # Verify all choices are strings
        assert all(isinstance(choice, str) for choice in choices)


@pytest.mark.integration
def test_mmlu_specific_subject_integration():
    """Test MMLU specific subject can load real data from HuggingFace."""
    MMLU = _registry.get_dataset_class("mmlu")
    dataset = MMLU()["college_mathematics"]("test")

    # Get first 2 samples
    samples = []
    for i, sample in enumerate(dataset):
        if i >= 2:
            break
        samples.append(sample)

    # Verify we got samples
    assert len(samples) == 2

    # Verify structure
    for sample in samples:
        assert len(sample) == 3  # question, choices, answer (no subject)
        question, choices, answer = sample
        assert isinstance(question, str) and len(question) > 0
        assert isinstance(choices, list) and len(choices) == 4
        assert isinstance(answer, int) and 0 <= answer <= 3
        # Verify all choices are strings
        assert all(isinstance(choice, str) for choice in choices)
