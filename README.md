# RoleConflictBench

### Concept Figure

![concept_figure](./concept_figure_situation.pdf)

Conceptual illustration of RoleConflictBench. We generate distinct expectations for two competing social roles and synthesize them into a story depicting an individual's role conflict. Our benchmark is designed to evaluate how decisions change depending on the situation.

### Method Overview

![method_figure](./method_figure_pdf.pdf)

RoleConflictBench is built in three stages:

1. **Expectation generation** — for each social role, generate a set of expectations (what that role is obligated to do) and, for each expectation, concrete situations that invoke it at varying levels of obligation/urgency.
2. **Story generation** — pick two roles held by the same person, sample one expectation/situation from each, and synthesize a short first-person story depicting the resulting role conflict.
3. **Evaluation** — present the story to a model (the "evaluatee") as a forced-choice question between the two roles and record its answer, reasoning, and the human value it invokes.

## Repository Structure

```
attribution/                Role taxonomy (role.csv) and helper class for querying roles by domain/gender/status
expectation_generation/      Stage 1: generate per-role expectations & situations
  output/                    Generated expectation/situation data, one JSONL file per role (e.g. F02_father.jsonl)
  run/                       expectation.py (generation logic), main.py (entry point)
story_generation/            Stage 2: combine two roles' expectations into a role-conflict story
  output/                    Generated stories, organized by generator model (e.g. gpt-4.1/)
  run/                       story_generator.py (generation logic), main.py (entry point)
evaluation/                  Stage 3: ask an evaluatee model to resolve the role conflict
  model/                     One .cfg (model name/temperature/api_key index) + client wrapper per supported model
  run/                       evaluatee.py, qa.py (prompts), utils.py, main.py (entry point)
benchmark/question.csv       Final benchmark dataset (role pairs, expectations, situations, generated story, answer key)
main_framework.py            CLI entry point that wires the three stages together
keys.py                      API key lookup by model/provider (fill in your own keys)
run.sh                       Example command for running evaluation
env.yaml                     Conda environment export
```

## Data Location
- Expectation & Situation Seed Data: `/expectation_generation/output/`
- Story & Benchmark Dataset: `/benchmark/question.csv`

### `benchmark/question.csv` columns
`Code1, Role1, Expectation_No1, Expectation1, Obligation1, Situation1, Code2, Role2, Expectation_No2, Expectation2, Obligation2, Situation2, Story, key` — one row per role-conflict story, describing the two competing roles, their triggering expectation/situation/obligation level, the synthesized story, and a unique row key.

### Role taxonomy (`attribution/role.csv`)
65 roles across 5 domains: `family`, `occupation`, `interpersonal`, `religion`, `society`. Each role has a `Code` (e.g. `F02` for father), a `Domain`, and optional `Gender`/`Status` attributes used to control role-pairing (e.g. avoiding gender-mismatched pairs).

## Setup

```bash
conda env create -f env.yaml
```

Fill in your API keys in `keys.py` (OpenAI, OpenRouter, DeepInfra, Anthropic — selected automatically based on model name).

## Usage

All stages are driven through `main_framework.py`:

```bash
# Generate expectations/situations for each role
python main_framework.py --generate_expectation

# Generate role-conflict stories from role + expectation pairs
python main_framework.py --generate_scenario --benchmark_model gpt-4.1

# Evaluate a model's decision on the benchmark
python main_framework.py --evaluate --evaluatee_model gpt-4.1
```

Add `--test` to any command to run on a small subset for a quick sanity check. See `run.sh` for example evaluation commands, and `evaluation/model/*.cfg` for the list of supported evaluatee models (GPT, Claude, Gemini, Qwen, OLMo, gpt-oss, etc.).
