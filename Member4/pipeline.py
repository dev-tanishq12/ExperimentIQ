# Member4/pipeline.py
# ============================================================
# EXPERIMENTIQ - MEMBER 4: END-TO-END PIPELINE ORCHESTRATOR
# ============================================================
# Unifies Member 1 (Quality Profiler), Member 2 (Cleaning Assistant),
# Member 3 (Experiment Analyzer), and Member 4 (Segment Analyzer &
# Decision Engine) into one coherent, robust execution pipeline.
# ============================================================

import os
import sys
from pathlib import Path

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union

# Ensure all member packages are on the import path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / 'Member1' / 'DVIIQ'))
sys.path.insert(0, str(BASE_DIR / 'member2'))
sys.path.insert(0, str(BASE_DIR / 'Member3'))
sys.path.insert(0, str(BASE_DIR / 'Member4'))

# Module imports
from quality_profiler import DataQualityProfiler
from cleaning_assistant import CleaningAssistant
from experiment_analyzer import ExperimentAnalyzer
from segment_analyzer import SegmentAnalyzer
from decision_engine import DecisionEngine


class ExperimentIQPipeline:
    """
    Unified 10-step ExperimentIQ Pipeline.
    
    1. Data Upload / Input
    2. Data Quality Profiling (Member 1)
    3. Intelligent Cleaning Assistant (Member 2)
    4. Clean & Validate Data
    5. Experiment Quality Check (Member 3)
    6. Metric Engine (Member 3)
    7. Statistical Analysis (Member 3)
    8. Power & Sample Analysis (Member 3)
    9. Segment Analysis (Member 4)
    10. Explainable Decision Engine (Member 4)
    """

    def __init__(
        self,
        group_column: str = 'experiment_group',
        user_column: str = 'user_id',
        control_group: str = 'control',
        treatment_group: str = 'treatment',
        conversion_col: str = 'conversion',
        revenue_col: str = 'revenue',
        duration_col: str = 'session_duration',
        alpha: float = 0.05,
        power_target: float = 0.80,
        min_segment_sample: int = 30
    ):
        self.config = {
            'group_column': group_column,
            'user_column': user_column,
            'control_group': control_group,
            'treatment_group': treatment_group,
            'conversion_col': conversion_col,
            'revenue_col': revenue_col,
            'duration_col': duration_col,
            'alpha': alpha,
            'power_target': power_target,
            'min_segment_sample': min_segment_sample
        }

    def load_dataset(self, data_input: Union[str, pd.DataFrame]) -> pd.DataFrame:
        """Load data from filepath or return copy of DataFrame."""
        if isinstance(data_input, pd.DataFrame):
            return data_input.copy()
        
        path_str = str(data_input)
        if path_str.endswith('.csv'):
            return pd.read_csv(path_str)
        elif path_str.endswith(('.xlsx', '.xls')):
            return pd.read_excel(path_str)
        else:
            raise ValueError(f"Unsupported file type: {path_str}")

    def run(
        self,
        data_input: Union[str, pd.DataFrame],
        auto_clean: bool = True,
        segment_dimensions: Optional[List[str]] = None,
        custom_clean_decisions: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Execute the complete ExperimentIQ pipeline end-to-end.
        """
        # Step 1: Ingest Data
        raw_df = self.load_dataset(data_input)
        original_shape = raw_df.shape

        # Step 2: Member 1 Data Quality Profiling
        profiler = DataQualityProfiler()
        profiler.df = raw_df.copy()
        quality_report = profiler.profile_data(raw_df)

        # Step 3 & 4: Member 2 Intelligent Cleaning Assistant
        # Create a temporary or virtual quality report structure for CleaningAssistant
        cleaner = CleaningAssistant.__new__(CleaningAssistant)
        cleaner.quality_report = quality_report
        cleaner.df = raw_df.copy()
        cleaner.cleaned_df = raw_df.copy()
        cleaner.cleaning_actions = []
        cleaner.audit_log = []
        cleaner.original_shape = original_shape
        cleaner.user_decisions = []

        # Generate recommendations
        cleaning_actions = cleaner.generate_recommendations()

        if custom_clean_decisions:
            # Apply custom user approvals/rejections from UI
            for dec in custom_clean_decisions:
                action = dec.get('action')
                status = dec.get('decision', 'approved')
                if status in ['approved', 'approved_modified']:
                    cleaner._apply_single_action(action)
                    cleaner._update_audit(action, status)
                else:
                    cleaner._update_audit(action, 'rejected')
                cleaner.user_decisions.append(dec)
        elif auto_clean:
            # Auto-apply all recommendations
            for action in cleaning_actions:
                cleaner._apply_single_action(action)
                cleaner._update_audit(action, 'auto_applied')

        cleaned_df = cleaner.cleaned_df
        validation_report = cleaner.generate_validation_report()
        cleaning_report = cleaner.generate_cleaning_report()

        # Step 5, 6, 7, 8: Member 3 Experiment Analyzer
        analyzer = ExperimentAnalyzer.__new__(ExperimentAnalyzer)
        analyzer.df = cleaned_df.copy()
        analyzer.cleaning_report = cleaning_report
        analyzer.quality_results = {}
        analyzer.metric_results = {}
        analyzer.statistical_results = {}
        analyzer.power_results = {}
        analyzer.config = {
            'alpha': self.config['alpha'],
            'beta': round(1 - self.config['power_target'], 2),
            'power_target': self.config['power_target'],
            'group_column': self.config['group_column'],
            'user_column': self.config['user_column'],
            'control_group': self.config['control_group'],
            'treatment_group': self.config['treatment_group'],
            'metrics': {
                'conversion': {'type': 'proportion', 'column': self.config['conversion_col']},
                'revenue': {'type': 'continuous', 'column': self.config['revenue_col']},
                'session_duration': {'type': 'continuous', 'column': self.config['duration_col']}
            }
        }
        analyzer._detect_columns()

        exp_quality = analyzer.check_experiment_quality()
        metrics = analyzer.calculate_metrics()
        stats_analysis = analyzer.perform_statistical_analysis()
        power_analysis = analyzer.calculate_power_analysis()
        experiment_report = analyzer.generate_report()

        # Step 9: Member 4 Segment Analysis
        seg_analyzer = SegmentAnalyzer(
            df=cleaned_df,
            group_column=analyzer.config['group_column'],
            control_name=analyzer.config['control_group'],
            treatment_name=analyzer.config['treatment_group'],
            min_sample_size=self.config['min_segment_sample'],
            alpha=self.config['alpha']
        )
        available_segments = seg_analyzer.detect_segment_columns()
        segment_results = seg_analyzer.run_all_segment_analysis(
            dimensions=segment_dimensions or available_segments,
            metric_col=self.config['conversion_col'] if self.config['conversion_col'] in cleaned_df.columns else 'conversion'
        )

        # Step 10: Member 4 Explainable Decision Engine
        engine = DecisionEngine(
            min_quality_score=0.65,
            alpha=self.config['alpha'],
            power_target=self.config['power_target'],
            primary_metric='conversion' if 'conversion' in cleaned_df.columns else list(metrics.keys())[0] if metrics else 'conversion'
        )
        decision_report = engine.evaluate(
            experiment_results=experiment_report,
            quality_report=quality_report,
            cleaning_report=cleaning_report,
            segment_results=segment_results
        )

        # Combine into complete system output
        full_pipeline_output = {
            'metadata': {
                'original_rows': original_shape[0],
                'original_cols': original_shape[1],
                'cleaned_rows': cleaned_df.shape[0],
                'cleaned_cols': cleaned_df.shape[1],
                'columns': list(cleaned_df.columns)
            },
            'quality_report': quality_report,
            'cleaning_report': cleaning_report,
            'validation_report': validation_report,
            'experiment_quality': exp_quality,
            'metrics': metrics,
            'statistical_analysis': stats_analysis,
            'power_analysis': power_analysis,
            'available_segments': available_segments,
            'segment_analysis': segment_results,
            'decision': decision_report
        }

        return full_pipeline_output
