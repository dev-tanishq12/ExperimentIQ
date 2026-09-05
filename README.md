# ExperimentIQ — Intelligent Experimentation & Decision Platform

> An end-to-end A/B testing and experimentation quality system that automatically profiles data quality, assists with data cleaning, validates experiment allocation, computes primary and guardrail metrics, performs hypothesis and power analysis, breaks down user segments, and renders transparent, explainable launch decisions.

---

## Table of Contents
- [1. Overview](#1-overview)
- [2. Problem Statement](#2-problem-statement)
- [3. Proposed Solution](#3-proposed-solution)
- [4. System Architecture](#4-system-architecture)
- [5. The 10-Step Pipeline](#5-the-10-step-pipeline)
- [6. Technologies Used](#6-technologies-used)
- [7. Installation & Setup](#7-installation--setup)
- [8. How to Run the Application](#8-how-to-run-the-application)
- [9. Input Dataset Format](#9-input-dataset-format)
- [10. Module Descriptions](#10-module-descriptions)
- [11. Decision Logic & Rule Hierarchy](#11-decision-logic--rule-hierarchy)
- [12. Example Output & Demo Scenarios](#12-example-output--demo-scenarios)
- [13. Team & Module Ownership](#13-team--module-ownership)
- [14. Future Improvements](#14-future-improvements)

---

## 1. Overview
**ExperimentIQ** bridges the gap between raw experiment data and confident product decisions. Rather than relying on disconnected scripts or black-box statistical tools, ExperimentIQ orchestrates data quality profiling, automated cleaning, sample ratio mismatch (SRM) checks, hypothesis testing, power analysis, multidimensional segmentation, and an explainable decision engine into a unified, interactive platform.

---

## 2. Problem Statement
Running online A/B experiments in production often suffers from critical, silent failures:
1. **Corrupted Data & Dirty Tracking**: Missing events, duplicate entries, outliers, and incorrect formats skew statistical calculations.
2. **Experiment Validity Violations**: Sample Ratio Mismatch (SRM) and users assigned to multiple groups simultaneously compromise experiment integrity.
3. **Misleading Statistical Significance**: Teams celebrate $p < 0.05$ without verifying effect direction, statistical power, or sample size adequacy.
4. **Hidden Segment Harm**: An overall positive experiment may mask severe drops in specific user segments (e.g., mobile users or specific regions).
5. **Lack of Explainability**: Stakeholders receive arbitrary launch/no-launch calls without understanding the underlying evidence.

---

## 3. Proposed Solution
ExperimentIQ solves these challenges through a unified 10-step pipeline and a deterministic, multi-tiered decision engine. It evaluates whether an experiment is valid, powered, effective, and safe before rendering one of four standardized recommendations:
- 🚀 **`LAUNCH`**
- ❌ **`DO NOT LAUNCH`**
- ⏳ **`CONTINUE EXPERIMENT`**
- ⚠️ **`INVESTIGATE DATA`**

Each decision is accompanied by a confidence percentage, primary rationale, itemized statistical evidence, and prioritized risk warnings.

---

## 4. System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                          ExperimentIQ System                           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
       ┌────────────────────────────┼────────────────────────────┐
       ▼                            ▼                            ▼
┌──────────────┐             ┌──────────────┐             ┌──────────────┐
│   Member 1   │             │   Member 2   │             │   Member 3   │
│ Data Quality │             │  Intelligent │             │  Experiment  │
│   Profiler   │             │   Cleaner    │             │   Analyzer   │
└──────┬───────┘             └──────┬───────┘             └──────┬───────┘
       │                            │                            │
       └────────────────────────────┼────────────────────────────┘
                                    │
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │                        Member 4                         │
       │  ┌───────────────────────┐   ┌───────────────────────┐  │
       │  │    Segment Analyzer   │   │    Decision Engine    │  │
       │  └───────────────────────┘   └───────────────────────┘  │
       │  ┌───────────────────────┐   ┌───────────────────────┐  │
       │  │   Pipeline Adapter    │   │  Flask / REST Server  │  │
       │  └───────────────────────┘   └───────────────────────┘  │
       │  ┌───────────────────────────────────────────────────┐  │
       │  │              Modern React Dashboard               │  │
       │  └───────────────────────────────────────────────────┘  │
       └─────────────────────────────────────────────────────────┘
```

---

## 5. The 10-Step Pipeline

1. **Data Upload**: Accepts CSV or Excel files, validating schema and column mappings.
2. **Data Quality Profiling**: Scans for missingness, exact duplicate rows, cross-cohort user leakage, schema violations, date format inconsistencies, casing anomalies, and whitespace issues.
3. **Intelligent Cleaning Assistant**: Formulates cleaning actions with confidence scores (median/mode imputation, deduplication, winsorization, case normalization).
4. **Clean & Validate Data**: Produces a cleaned dataset and generates an audit log comparing pre- and post-cleaning states.
5. **Experiment Quality Check**: Executes Chi-Square Goodness-of-Fit tests to detect Sample Ratio Mismatch (SRM) and verifies single-group cohort allocation.
6. **Metric Engine**: Calculates baseline conversion rates, revenue per user, session duration, absolute lift, and relative percentage lift.
7. **Statistical Analysis**: Selects appropriate parametric tests (Two-Proportion $Z$-test, Welch's $t$-test), two-tailed $p$-values, 95% Confidence Intervals, and Cohen's $h$ / $d$ effect sizes.
8. **Power & Sample Analysis**: Calculates statistical power achieved, minimum required sample size, and sample size deficit.
9. **Segment Analysis**: Automatically detects demographic dimensions (`device`, `country`, `age_group`), computes segment-specific lift, and flags localized degradation or small sample sizes ($n < 30$).
10. **Explainable Decision Engine**: Synthesizes evidence across all previous stages to return a clear launch recommendation with supporting rationale and risk guardrails.

---

## 6. Technologies Used

### Backend & Core Analytics
- **Python 3.9+** (Tested on 3.11)
- **pandas** (>= 2.0.0): Data processing, manipulation, and transformations
- **numpy** (>= 1.23.0): Fast vector operations and numerical calculations
- **scipy** (>= 1.9.0): Statistical tests ($\chi^2$ goodness-of-fit, Welch's $t$-test, normal distributions)
- **statsmodels** (>= 0.14.0): Proportions $Z$-tests and statistical power solving (`GofChisquarePower`, `TTestIndPower`)
- **Flask & Flask-CORS**: Lightweight REST API server
- **openpyxl**: Excel dataset support

### Frontend Dashboard
- **React 18**: Component-based UI
- **Vite 5**: Fast frontend tooling and bundler
- **Recharts**: Interactive SVG charts (bar charts, lift comparisons)
- **Lucide React**: Modern iconography
- **Vanilla CSS (Design Tokens)**: Custom glassmorphism, responsive grid, and accessible color palettes

---

## 7. Installation & Setup

### Prerequisites
- Python 3.9 or higher
- Node.js (v18 or higher) & npm

### 1. Clone the Repository
```bash
git clone https://github.com/dev-tanishq12/ExperimentIQ.git
cd ExperimentIQ
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
pip install flask-cors statsmodels
```

### 3. Install Frontend Dependencies & Build Bundle
```bash
cd frontend
npm install
npm run build
cd ..
```

---

## 8. How to Run the Application

### Option A: Run Full Web Application (Unified Server)
The Flask server directly serves the React application and the REST API on port `5000`:
```bash
python server.py
```
Open your browser to: **`http://localhost:5000`**

### Option B: Run in Developer Mode (Hot-Reload)
Run the backend and frontend development servers concurrently:

**Terminal 1 (Backend API):**
```bash
python server.py
```

**Terminal 2 (React Vite Dev Server):**
```bash
cd frontend
npm run dev
```
Open your browser to: **`http://localhost:3000`**

### Option C: Run Unit & Integration Tests
Run the entire 41-test suite across all four members:
```bash
# On Linux / macOS:
PYTHONPATH="Member1/DVIIQ:member2:Member3:Member4" python -m unittest discover Member4/tests

# On Windows PowerShell:
$env:PYTHONPATH="Member1/DVIIQ;member2;Member3;Member4"; $env:PYTHONIOENCODING="utf-8"; python -m unittest discover Member4/tests
```

---

## 9. Input Dataset Format

ExperimentIQ accepts CSV and Excel files. While column names are configurable in the UI, standard columns include:

| Column Name | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `user_id` | String / Int | Unique identifier for the user | Yes |
| `experiment_group` | String | Variant assignment: `'control'` or `'treatment'` | Yes |
| `conversion` | Integer | Binary conversion event (`1` or `0`) | Recommended |
| `revenue` | Float | Continuous revenue generated per user | Optional |
| `session_duration`| Float | Continuous session duration in seconds | Optional |
| `device` | String | Segmentation feature (e.g. `'mobile'`, `'desktop'`) | Optional |
| `country` | String | Segmentation feature (e.g. `'US'`, `'UK'`, `'India'`) | Optional |
| `age` | Integer | User age (automatically binned into age brackets) | Optional |

---

## 10. Module Descriptions

### Member 1: Data Quality Profiler (`Member1/DVIIQ/quality_profiler.py`)
- Profiles dataset dimensions, dtypes, null ratios, and statistical distributions.
- Detects missing values, duplicates, outliers, formatting flaws, and critical user assignment leaks.
- Computes overall `quality_score` (0.0 to 1.0).

### Member 2: Intelligent Cleaning Assistant (`member2/cleaning_assistant.py`)
- Analyzes Member 1's issues and recommends remediation actions with confidence scores.
- Imputes missing data, resolves duplicate user assignments, trims strings, and standardizes formats.
- Generates a validation audit log tracking row and column shape deltas.

### Member 3: Experiment Analyzer (`Member3/experiment_analyzer.py`)
- Performs $\chi^2$ Sample Ratio Mismatch (SRM) checks.
- Computes metrics (Conversion, Revenue, Duration), absolute lift, and relative lift.
- Runs Two-Proportion $Z$-tests and Welch's $t$-tests with 95% Confidence Intervals.
- Computes power analysis and required sample sizes.

### Member 4: Segment Analyzer & Decision Engine (`Member4/`)
- **`segment_analyzer.py`**: Dynamically discovers segmentation columns, calculates metrics per cohort, flags small samples ($n < 30$), and identifies localized degradation.
- **`decision_engine.py`**: Implements the explainable 4-tier decision tree.
- **`pipeline.py`**: Orchestrates all 10 stages in-memory or from file paths.
- **`frontend/`**: Interactive React web dashboard.

---

## 11. Decision Logic & Rule Hierarchy

```
                                  [Start Evaluation]
                                          │
                        ┌─────────────────┴─────────────────┐
                        ▼                                   ▼
             [Data Quality Defect?]                 [SRM Test Fails?]
             (Quality Score < 0.65)                (Chi-Square p < 0.05)
                        │                                   │
                        └─────────────────┬─────────────────┘
                                          │ YES
                                          ▼
                                ⚠️ INVESTIGATE DATA
                                          │ NO
                                          ▼
                        [Significant Negative Impact?]
                        (p < 0.05 AND Diff < 0)
                                          │ YES
                                          ▼
                                 ❌ DO NOT LAUNCH
                                          │ NO
                                          ▼
                        [Severe Segment Harm in Winner?]
                        (Credible cohort drop >= 10%)
                                          │ YES
                                          ▼
                                ⚠️ INVESTIGATE DATA
                                          │ NO
                                          ▼
                        [Significant Positive AND Powered?]
                        (p < 0.05, Diff > 0, Power >= 80%)
                                          │ YES
                                          ▼
                                     🚀 LAUNCH
                                          │ NO
                                          ▼
                                ⏳ CONTINUE EXPERIMENT
```

---

## 12. Example Output & Demo Scenarios

ExperimentIQ includes four pre-configured demo datasets (`data/demo/`):

1. **Scenario A — Winning Treatment (`scenario_a_launch.csv`)**:
   - Split: 2,000 Control vs. 2,000 Treatment (Balanced)
   - Metric: Conversion 9.85% $\to$ 13.25% (+34.5% relative lift, $p = 0.0007$)
   - Power: Adequately powered (Target: 1,380 users, Current: 4,000)
   - Decision: 🚀 **`LAUNCH`** (Confidence: 95%)

2. **Scenario B — Underpowered Experiment (`scenario_b_continue.csv`)**:
   - Split: 150 Control vs. 150 Treatment
   - Metric: Conversion 8.00% $\to$ 10.00% (+25.0% lift, $p = 0.545$)
   - Power: Underpowered (Needs 3,204 users, Current: 300)
   - Decision: ⏳ **`CONTINUE EXPERIMENT`** (Confidence: 86%)

3. **Scenario C — Severe SRM & Leakage (`scenario_c_investigate.csv`)**:
   - Split: 2,200 Control vs. 699 Treatment (Severe SRM, $p < 0.00001$)
   - Leakage: 101 duplicate users assigned across both groups
   - Decision: ⚠️ **`INVESTIGATE DATA`** (Confidence: 95%)

4. **Scenario D — Harmful Treatment (`scenario_d_do_not_launch.csv`)**:
   - Split: 2,000 Control vs. 2,000 Treatment
   - Metric: Conversion 12.10% $\to$ 8.40% (-30.6% relative drop, $p = 0.0001$)
   - Decision: ❌ **`DO NOT LAUNCH`** (Confidence: 94%)

---

## 13. Team & Module Ownership

| Team Member | Module Assigned | Primary Deliverables |
| :--- | :--- | :--- |
| **Member 1** | Data Quality Profiler | Schema rules, profiling, anomaly detection, quality score |
| **Member 2** | Cleaning Assistant | Action recommendations, auto-cleaning, validation reporting |
| **Member 3** | Experiment Analysis Engine | SRM tests, metrics calculation, hypothesis testing, power analysis |
| **Member 4** | Integration & Decisions | Segment analysis, explainable decision engine, React UI, testing |

---

## 14. Future Improvements
- **Bayesian A/B Testing**: Support probability of being best and expected loss modeling.
- **Multiple Comparison Corrections**: Implement Benjamini-Hochberg FDR adjustments when analyzing dozens of segments concurrently.
- **Automated Alerts / Webhooks**: Integration with Slack and Discord for real-time experiment alerts.
- **Sequential Testing**: Support early stopping rules (e.g. mSPRT) without alpha inflation.
