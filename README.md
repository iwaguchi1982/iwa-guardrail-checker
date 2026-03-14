# iwa-guardrail-checker

Preflight checker for survival-oriented bioinformatics datasets, with guardrails for missingness, event sufficiency, and model readiness.

## Overview

`iwa-guardrail-checker` is a lightweight source-available Streamlit app designed to assess whether a clinical dataset is suitable for downstream survival analysis.

Before running Kaplan-Meier curves, Cox proportional hazards models, or related exploratory workflows, this tool helps identify common statistical risks and provides actionable recommendations.

## Key Features

- **🛡️ Comprehensive Guardrails**: Unified `OK / CAUTION / DANGER` status evaluation for your dataset.
- **📁 Smart Upload**: Supports CSV/TSV/TXT files with automatic delimiter detection.
- **🗺️ Automatic Column Mapping**: Intelligent detection of Patient ID, Time, Event, and Group columns based on common naming conventions.
- **📊 Interactive Dashboard**:
    - **Basic Summary**: Event rates, unique patient counts, and duplicate detection.
    - **Group Distribution**: Visual horizontal bar charts for quick sample size assessment.
    - **Covariate Retention**: Estimates row loss for multivariate models (complete-case analysis).
- **💡 Actionable Recommendations**: Dynamic suggestions to remediate detected data quality issues.

## Intended Users

- Bioinformatics engineers
- Translational researchers
- Clinical data analysts
- Users preparing datasets for survival-oriented workflows

## Installation

Clone this repository:

```bash
git clone https://github.com/iwaguchi1982/iwa-guardrail-checker.git
cd iwa-guardrail-checker
```

Install Pixi if it is not already installed:
```bash
curl -fsSL https://pixi.sh/install.sh | sh
```

Install project dependencies:
```bash
pixi install
```

## Usage
Run the application:

```bash
pixi run python -m streamlit run iwa_guardrail_checker.py
```

Alternatively, manually launch it:
```bash
python -m streamlit run iwa_guardrail_checker.py
```

## Checked Rules (v0.1)

- **DANGER**
  - required column missing
  - row count < 5
  - non-positive follow-up time
  - invalid event values (outside 0/1)
  - all events or zero events
  - fewer than 2 valid groups

- **CAUTION**
  - duplicate IDs
  - small group size (< 5)
  - large group size imbalance
  - low total events
  - zero events in specific groups
  - missing covariates (retention check)

## Notes

> 本プロジェクトは探索研究向けの開発中ソフトウェアです。  
> 臨床判断、規制対応用途、診断用途を意図したものではありません。

## License
This project is distributed under the  [Iwa Collections Non-Resale License 1.0](LICENSE).

