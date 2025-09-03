# doteval-datasets

Standard datasets for [dotevals](https://github.com/dottxt-ai/dotevals) LLM evaluations.

## Installation

```bash
pip install dotevals-datasets
```

## Usage

Once installed, the datasets are automatically available in doteval:

```python
from dotevals import foreach

@foreach.bfcl("simple")
def eval_bfcl(question: str, schema: list, answer: list):
    # Your evaluation logic here
    pass

@foreach.gsm8k("test")
def eval_gsm8k(question: str, reasoning: str, answer: str):
    # Your evaluation logic here
    pass

@foreach.humaneval()
def eval_humaneval(prompt: str, canonical_solution: str, test: str, entry_point: str):
    # Your evaluation logic here
    pass

@foreach.mmlu("test")
def eval_mmlu_all(question: str, subject: str, choices: list, answer: int):
    # Your evaluation logic here
    pass

@foreach.mmlu["college_mathematics"]("test")
def eval_mmlu_math(question: str, choices: list, answer: int):
    # Your evaluation logic here
    pass

@foreach.sroie("test")
def eval_sroie(image: Image, entities: dict):
    # Your evaluation logic here
    pass
```

## Available Datasets

- **BFCL** (Berkeley Function Calling Leaderboard): Tests function calling capabilities
  - Variants: `simple`, `multiple`, `parallel`
  - Columns: `question`, `schema`, `answer`

- **GSM8K**: Grade school math word problems
  - Splits: `train`, `test`
  - Columns: `question`, `reasoning`, `answer`

- **HumanEval**: Hand-written programming problems for code generation evaluation
  - Columns: `prompt`, `canonical_solution`, `test`, `entry_point`

- **MMLU**: Massive Multitask Language Understanding across 57 academic subjects
  - All subjects: `mmlu("test")` - Columns: `question`, `subject`, `choices`, `answer`
  - Specific subject: `mmlu["college_mathematics"]("test")` - Columns: `question`, `choices`, `answer`
  - Splits: `test`, `validation`, `dev`

- **SROIE**: Scanned receipts OCR and information extraction
  - Splits: `train`, `test`
  - Columns: `image`, `address`, `company`, `date`
