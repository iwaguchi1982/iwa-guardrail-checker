# iwa-guardrail-checker

Preflight checker for survival-oriented bioinformatics datasets, with guardrails for missingness, event sufficiency, and model readiness.

## Overview

`iwa-guardrail-checker` is a lightweight source-available Streamlit app designed to assess whether a clinical dataset is suitable for downstream survival analysis.

Before running Kaplan-Meier curves, Cox proportional hazards models, or related exploratory workflows, this tool helps identify common statistical risks such as:

- too few events
- severe missingness
- zero-event groups
- strong group size imbalance
- weak Cox model readiness

The goal is not to replace analysis, but to prevent unsafe or misleading analysis from starting too early.

## Intended Users

This project is intended for:

- bioinformatics engineers
- translational researchers
- clinical data analysts
- users preparing datasets for survival-oriented workflows

## Current Scope

This repository currently focuses on:

- clinical table upload
- required column mapping
- missingness checks
- event sufficiency checks
- basic Cox readiness heuristics
- overall `OK / CAUTION / DANGER` judgement

## Environment

Tested environment:

- OS: Ubuntu 24.04 / WSL2 Ubuntu
- Python: 3.10+
- Package / environment manager: Pixi

## Installation

Clone this repository:

```bash
git clone https://github.com/iwaguchi1982/iwa-guardrail-checker.git
cd iwa-guardrail-checker
``

Install Pixi if it is not already installed:
```bash
curl -fsSL https://pixi.sh/install.sh | sh
```
Install project dependencies:
```bash
pixi install
```

## Usage
Run the application inside the Pixi environment:
```bash
pixi shell
python -m streamlit run iwa_guardrail_checker.py
```
Alternatively, you can launch it directly without entering the shell:
```bash
pixi run python -m streamlit run iwa_guardrail_checker.py
```
## Planned Checks in v0.1
- required column existence
- duplicate patient IDs
- total sample count
- total event count
- event count by group
- minimum group size
- minimum events per group
- estimated events per parameter
- missingness by column
- complete-case retention estimate

## Output
The app returns:
- overall status: OK, CAUTION, or DANGER
- concise reasons list
- summary tables for survival readiness
- missingness overview

## License

This project is source-available under the [MIT License](LICENSE).

