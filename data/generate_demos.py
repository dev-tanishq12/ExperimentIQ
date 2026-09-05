# data/generate_demos.py
"""
Generates the 4 standardized evaluation scenarios for ExperimentIQ:
Scenario A: Successful Experiment (🚀 LAUNCH)
Scenario B: Inconclusive Experiment (⏳ CONTINUE EXPERIMENT)
Scenario C: Invalid / SRM Failure / Poor Data (⚠️ INVESTIGATE DATA)
Scenario D: Negative Treatment Impact (❌ DO NOT LAUNCH)
"""

import os
import pandas as pd
import numpy as np

np.random.seed(42)
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'demo')
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_scenario_a():
    """Scenario A: Successful experiment -> LAUNCH"""
    n = 4000
    n_ctrl = n // 2
    n_treat = n // 2

    ctrl_conv = np.random.binomial(1, 0.10, n_ctrl)
    treat_conv = np.random.binomial(1, 0.14, n_treat)

    ctrl_rev = np.random.normal(100, 25, n_ctrl) * (ctrl_conv * 1.5 + 0.5)
    treat_rev = np.random.normal(115, 25, n_treat) * (treat_conv * 1.5 + 0.5)

    df_ctrl = pd.DataFrame({
        'user_id': [f'user_{i:05d}' for i in range(1, n_ctrl + 1)],
        'experiment_group': ['control'] * n_ctrl,
        'conversion': ctrl_conv,
        'revenue': np.clip(ctrl_rev, 0, None).round(2),
        'session_duration': np.random.normal(250, 40, n_ctrl).clip(30, 800).round(1),
        'device': np.random.choice(['mobile', 'desktop', 'tablet'], n_ctrl, p=[0.55, 0.35, 0.10]),
        'country': np.random.choice(['US', 'UK', 'India'], n_ctrl, p=[0.50, 0.30, 0.20]),
        'age': np.random.randint(18, 70, n_ctrl)
    })

    df_treat = pd.DataFrame({
        'user_id': [f'user_{i:05d}' for i in range(n_ctrl + 1, n + 1)],
        'experiment_group': ['treatment'] * n_treat,
        'conversion': treat_conv,
        'revenue': np.clip(treat_rev, 0, None).round(2),
        'session_duration': np.random.normal(280, 40, n_treat).clip(30, 800).round(1),
        'device': np.random.choice(['mobile', 'desktop', 'tablet'], n_treat, p=[0.55, 0.35, 0.10]),
        'country': np.random.choice(['US', 'UK', 'India'], n_treat, p=[0.50, 0.30, 0.20]),
        'age': np.random.randint(18, 70, n_treat)
    })

    df = pd.concat([df_ctrl, df_treat]).sample(frac=1.0, random_state=42).reset_index(drop=True)
    out_path = os.path.join(OUTPUT_DIR, 'scenario_a_launch.csv')
    df.to_csv(out_path, index=False)
    print(f"[OK] Generated Scenario A -> {out_path} ({len(df)} rows)")


def generate_scenario_b():
    """Scenario B: Inconclusive / Underpowered -> CONTINUE EXPERIMENT"""
    n = 300
    n_ctrl = n // 2
    n_treat = n // 2

    ctrl_conv = np.random.binomial(1, 0.10, n_ctrl)
    treat_conv = np.random.binomial(1, 0.115, n_treat)

    ctrl_rev = np.random.normal(100, 25, n_ctrl).clip(0)
    treat_rev = np.random.normal(102, 25, n_treat).clip(0)

    df_ctrl = pd.DataFrame({
        'user_id': [f'user_{i:05d}' for i in range(1, n_ctrl + 1)],
        'experiment_group': ['control'] * n_ctrl,
        'conversion': ctrl_conv,
        'revenue': ctrl_rev.round(2),
        'session_duration': np.random.normal(250, 40, n_ctrl).clip(30).round(1),
        'device': np.random.choice(['mobile', 'desktop', 'tablet'], n_ctrl),
        'country': np.random.choice(['US', 'UK', 'India'], n_ctrl),
        'age': np.random.randint(18, 70, n_ctrl)
    })

    df_treat = pd.DataFrame({
        'user_id': [f'user_{i:05d}' for i in range(n_ctrl + 1, n + 1)],
        'experiment_group': ['treatment'] * n_treat,
        'conversion': treat_conv,
        'revenue': treat_rev.round(2),
        'session_duration': np.random.normal(252, 40, n_treat).clip(30).round(1),
        'device': np.random.choice(['mobile', 'desktop', 'tablet'], n_treat),
        'country': np.random.choice(['US', 'UK', 'India'], n_treat),
        'age': np.random.randint(18, 70, n_treat)
    })

    df = pd.concat([df_ctrl, df_treat]).sample(frac=1.0, random_state=42).reset_index(drop=True)
    out_path = os.path.join(OUTPUT_DIR, 'scenario_b_continue.csv')
    df.to_csv(out_path, index=False)
    print(f"[OK] Generated Scenario B -> {out_path} ({len(df)} rows)")


def generate_scenario_c():
    """Scenario C: Severe SRM and User Leaks -> INVESTIGATE DATA"""
    # 2200 control vs 800 treatment (extreme SRM)
    n_ctrl = 2200
    n_treat = 800

    ctrl_conv = np.random.binomial(1, 0.12, n_ctrl)
    treat_conv = np.random.binomial(1, 0.15, n_treat)

    df_ctrl = pd.DataFrame({
        'user_id': [f'user_{i:05d}' for i in range(1, n_ctrl + 1)],
        'experiment_group': ['control'] * n_ctrl,
        'conversion': ctrl_conv,
        'revenue': np.random.normal(100, 30, n_ctrl).clip(0).round(2),
        'session_duration': np.random.normal(240, 40, n_ctrl).clip(30).round(1),
        'device': np.random.choice(['mobile', 'desktop'], n_ctrl),
        'country': np.random.choice(['US', 'UK'], n_ctrl),
        'age': np.random.randint(18, 70, n_ctrl)
    })

    df_treat = pd.DataFrame({
        'user_id': [f'user_{i:05d}' for i in range(n_ctrl - 100, n_ctrl + n_treat - 100)], # 100 duplicate users!
        'experiment_group': ['treatment'] * n_treat,
        'conversion': treat_conv,
        'revenue': np.random.normal(110, 30, n_treat).clip(0).round(2),
        'session_duration': np.random.normal(260, 40, n_treat).clip(30).round(1),
        'device': np.random.choice(['mobile', 'desktop'], n_treat),
        'country': np.random.choice(['US', 'UK'], n_treat),
        'age': np.random.randint(18, 70, n_treat)
    })

    df = pd.concat([df_ctrl, df_treat]).sample(frac=1.0, random_state=42).reset_index(drop=True)
    out_path = os.path.join(OUTPUT_DIR, 'scenario_c_investigate.csv')
    df.to_csv(out_path, index=False)
    print(f"[OK] Generated Scenario C -> {out_path} ({len(df)} rows)")


def generate_scenario_d():
    """Scenario D: Negative Treatment -> DO NOT LAUNCH"""
    n = 4000
    n_ctrl = n // 2
    n_treat = n // 2

    # Statistically significant drop
    ctrl_conv = np.random.binomial(1, 0.12, n_ctrl)
    treat_conv = np.random.binomial(1, 0.08, n_treat)

    ctrl_rev = np.random.normal(110, 25, n_ctrl).clip(0)
    treat_rev = np.random.normal(85, 25, n_treat).clip(0)

    df_ctrl = pd.DataFrame({
        'user_id': [f'user_{i:05d}' for i in range(1, n_ctrl + 1)],
        'experiment_group': ['control'] * n_ctrl,
        'conversion': ctrl_conv,
        'revenue': ctrl_rev.round(2),
        'session_duration': np.random.normal(300, 40, n_ctrl).clip(30).round(1),
        'device': np.random.choice(['mobile', 'desktop', 'tablet'], n_ctrl),
        'country': np.random.choice(['US', 'UK', 'India'], n_ctrl),
        'age': np.random.randint(18, 70, n_ctrl)
    })

    df_treat = pd.DataFrame({
        'user_id': [f'user_{i:05d}' for i in range(n_ctrl + 1, n + 1)],
        'experiment_group': ['treatment'] * n_treat,
        'conversion': treat_conv,
        'revenue': treat_rev.round(2),
        'session_duration': np.random.normal(240, 40, n_treat).clip(30).round(1),
        'device': np.random.choice(['mobile', 'desktop', 'tablet'], n_treat),
        'country': np.random.choice(['US', 'UK', 'India'], n_treat),
        'age': np.random.randint(18, 70, n_treat)
    })

    df = pd.concat([df_ctrl, df_treat]).sample(frac=1.0, random_state=42).reset_index(drop=True)
    out_path = os.path.join(OUTPUT_DIR, 'scenario_d_do_not_launch.csv')
    df.to_csv(out_path, index=False)
    print(f"[OK] Generated Scenario D -> {out_path} ({len(df)} rows)")


if __name__ == '__main__':
    generate_scenario_a()
    generate_scenario_b()
    generate_scenario_c()
    generate_scenario_d()
