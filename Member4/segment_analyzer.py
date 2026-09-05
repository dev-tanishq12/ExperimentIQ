# Member4/segment_analyzer.py
# ============================================================
# EXPERIMENTIQ - MEMBER 4: SEGMENT ANALYSIS MODULE
# ============================================================
# Analyzes experiment performance across user segments
# Dynamically detects dimensions, calculates segment metrics,
# flags sample size risks, and outputs structured findings for
# the Decision Engine and Dashboard.
# ============================================================

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import math
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest
import warnings
warnings.filterwarnings('ignore')


def _safe_float(val, ndigits=4):
    """Safely convert value to float, handling NaN/inf."""
    if val is None or pd.isna(val) or np.isinf(val):
        return None
    return round(float(val), ndigits)


class SegmentAnalyzer:
    """
    Automated and customizable segmentation analyzer for A/B experiments.
    
    Responsibilities:
    1. Dynamically identify categorical and demographic segmentation dimensions.
    2. Compute control vs. treatment metric rates, absolute lift, and relative lift.
    3. Evaluate statistical stability per segment.
    4. Guard against small sample noise with safety thresholds.
    5. Detect potential harmful segments or localized degradation.
    """

    DEFAULT_IGNORE_COLS = {
        'user_id', 'id', 'experiment_group', 'group', 'variant',
        'conversion', 'converted', 'revenue', 'session_duration',
        'date', 'timestamp', 'created_at', 'empty_column'
    }

    def __init__(
        self,
        df: pd.DataFrame,
        group_column: str = 'experiment_group',
        control_name: str = 'control',
        treatment_name: str = 'treatment',
        min_sample_size: int = 30,
        alpha: float = 0.05
    ):
        self.df = df.copy()
        self.group_column = group_column
        self.control_name = control_name
        self.treatment_name = treatment_name
        self.min_sample_size = min_sample_size
        self.alpha = alpha

        # Auto-standardize group names if necessary
        if self.group_column in self.df.columns:
            self.df[self.group_column] = (
                self.df[self.group_column]
                .astype(str)
                .str.strip()
                .str.lower()
            )
            self.control_name = self.control_name.lower().strip()
            self.treatment_name = self.treatment_name.lower().strip()

    def detect_segment_columns(self, max_unique: int = 25) -> List[str]:
        """
        Dynamically discover columns suitable for segmentation.
        Criteria:
        - Not an ID, group assignment, timestamp, or primary metric column.
        - Has between 2 and max_unique distinct values.
        - Has at least some non-null values.
        """
        segment_cols = []
        for col in self.df.columns:
            col_lower = col.lower()
            if col_lower in self.DEFAULT_IGNORE_COLS:
                continue
            if 'id' in col_lower and col_lower != 'device_id':
                continue
            if 'date' in col_lower or 'time' in col_lower:
                continue

            unique_count = self.df[col].nunique(dropna=True)
            if 2 <= unique_count <= max_unique:
                segment_cols.append(col)
            elif col_lower in ['age'] and pd.api.types.is_numeric_dtype(self.df[col]):
                # Add synthetic age_group if age is present
                if 'age_group' not in self.df.columns:
                    self._create_age_groups(col)
                    segment_cols.append('age_group')

        return sorted(list(set(segment_cols)))

    def _create_age_groups(self, col: str = 'age'):
        """Create standard age bracket categories from numeric age."""
        bins = [0, 24, 34, 49, 64, 120]
        labels = ['<25', '25-34', '35-49', '50-64', '65+']
        self.df['age_group'] = pd.cut(
            self.df[col], bins=bins, labels=labels, right=True
        ).astype(str).replace({'nan': 'Unknown'})

    def analyze_dimension(
        self,
        dimension: str,
        metric_col: str = 'conversion',
        metric_type: str = 'proportion'
    ) -> Dict[str, Any]:
        """
        Analyze experiment metrics sliced across a specific segmentation dimension.
        """
        if dimension not in self.df.columns:
            raise ValueError(f"Dimension '{dimension}' not present in dataset.")
        if self.group_column not in self.df.columns:
            raise ValueError(f"Group column '{self.group_column}' not found.")
        if metric_col not in self.df.columns:
            raise ValueError(f"Metric column '{metric_col}' not found.")

        # Clean dimension values: fill NaN with 'Unknown' and strip string whitespace
        sub_df = self.df[[dimension, self.group_column, metric_col]].copy()
        if sub_df[dimension].dtype == 'object' or sub_df[dimension].dtype.name == 'category':
            sub_df[dimension] = sub_df[dimension].fillna('Unknown').astype(str).str.strip()
        else:
            sub_df[dimension] = sub_df[dimension].fillna('Unknown').astype(str)

        # Drop rows where metric is missing
        sub_df = sub_df.dropna(subset=[metric_col])

        # Get unique segment categories
        categories = sorted(sub_df[dimension].unique().tolist())

        segments_data = []
        warnings = []
        harmful_segments = []
        positive_segments = []

        for cat in categories:
            cat_df = sub_df[sub_df[dimension] == cat]
            ctrl_df = cat_df[cat_df[self.group_column] == self.control_name]
            treat_df = cat_df[cat_df[self.group_column] == self.treatment_name]

            n_ctrl = len(ctrl_df)
            n_treat = len(treat_df)
            n_total = n_ctrl + n_treat

            if n_total == 0:
                continue

            is_small = n_total < self.min_sample_size or n_ctrl < 10 or n_treat < 10

            segment_summary = {
                'dimension': dimension,
                'segment': cat,
                'control_n': int(n_ctrl),
                'treatment_n': int(n_treat),
                'total_n': int(n_total),
                'is_small_sample': bool(is_small),
                'control_metric': None,
                'treatment_metric': None,
                'absolute_lift': None,
                'relative_lift_pct': None,
                'p_value': None,
                'is_significant': False,
                'status': 'adequate_sample' if not is_small else 'small_sample_warning'
            }

            if n_ctrl == 0 or n_treat == 0:
                segment_summary['status'] = 'missing_group_data'
                warnings.append(
                    f"Segment '{cat}' in '{dimension}' has missing control or treatment data (Control: {n_ctrl}, Treatment: {n_treat})."
                )
                segments_data.append(segment_summary)
                continue

            if metric_type == 'proportion':
                # Binary / Proportion Metric
                ctrl_success = float(ctrl_df[metric_col].sum())
                treat_success = float(treat_df[metric_col].sum())
                p_ctrl = ctrl_success / n_ctrl if n_ctrl > 0 else 0
                p_treat = treat_success / n_treat if n_treat > 0 else 0

                abs_lift = p_treat - p_ctrl
                rel_lift = ((p_treat - p_ctrl) / p_ctrl * 100) if p_ctrl > 0 else 0.0

                p_val = None
                sig = False
                if not is_small and ctrl_success > 0 and treat_success > 0:
                    try:
                        _, p_val = proportions_ztest(
                            [treat_success, ctrl_success],
                            [n_treat, n_ctrl]
                        )
                        sig = bool(p_val < self.alpha)
                    except Exception:
                        p_val = None

                segment_summary.update({
                    'control_metric': _safe_float(p_ctrl, 4),
                    'treatment_metric': _safe_float(p_treat, 4),
                    'control_pct': _safe_float(p_ctrl * 100, 2),
                    'treatment_pct': _safe_float(p_treat * 100, 2),
                    'absolute_lift': _safe_float(abs_lift, 4),
                    'relative_lift_pct': _safe_float(rel_lift, 2),
                    'p_value': _safe_float(p_val, 6),
                    'is_significant': sig
                })

            else:
                # Continuous Metric (revenue, duration)
                m_ctrl = float(ctrl_df[metric_col].mean())
                m_treat = float(treat_df[metric_col].mean())
                abs_lift = m_treat - m_ctrl
                rel_lift = ((m_treat - m_ctrl) / m_ctrl * 100) if m_ctrl != 0 else 0.0

                p_val = None
                sig = False
                if not is_small:
                    try:
                        _, p_val = stats.ttest_ind(
                            treat_df[metric_col].dropna(),
                            ctrl_df[metric_col].dropna(),
                            equal_var=False
                        )
                        sig = bool(p_val < self.alpha)
                    except Exception:
                        p_val = None

                segment_summary.update({
                    'control_metric': _safe_float(m_ctrl, 2),
                    'treatment_metric': _safe_float(m_treat, 2),
                    'absolute_lift': _safe_float(abs_lift, 2),
                    'relative_lift_pct': _safe_float(rel_lift, 2),
                    'p_value': _safe_float(p_val, 6),
                    'is_significant': sig
                })

            # Check for segment harm vs benefit
            rel_pct = segment_summary.get('relative_lift_pct') or 0.0
            if is_small:
                if rel_pct <= -15.0:
                    warnings.append(
                        f"Potential negative trend in segment '{cat}' ({rel_pct:+.1f}%), but sample size is small (n={n_total}). Avoid hasty conclusions."
                    )
            else:
                if rel_pct <= -5.0 and (segment_summary['is_significant'] or rel_pct <= -15.0):
                    harmful_segments.append({
                        'segment': cat,
                        'lift_pct': rel_pct,
                        'sample_size': n_total,
                        'p_value': segment_summary['p_value']
                    })
                elif rel_pct >= 5.0 and (segment_summary['is_significant'] or rel_pct >= 15.0):
                    positive_segments.append({
                        'segment': cat,
                        'lift_pct': rel_pct,
                        'sample_size': n_total,
                        'p_value': segment_summary['p_value']
                    })

            segments_data.append(segment_summary)

        # Detect Simpson's Paradox or Segment Inversion
        # (e.g., all or majority of segments positive, but overall negative or vice versa)
        return {
            'dimension': dimension,
            'metric': metric_col,
            'metric_type': metric_type,
            'segments': segments_data,
            'total_segments': len(segments_data),
            'harmful_segments': harmful_segments,
            'positive_segments': positive_segments,
            'warnings': warnings,
            'has_harmful_segment': len(harmful_segments) > 0,
            'small_segment_count': sum(1 for s in segments_data if s['is_small_sample'])
        }

    def run_all_segment_analysis(
        self,
        dimensions: Optional[List[str]] = None,
        metric_col: str = 'conversion',
        metric_type: str = 'proportion'
    ) -> Dict[str, Any]:
        """
        Run segmentation analysis across all detected (or specified) dimensions.
        Produces structured summary for the Decision Engine.
        """
        if not dimensions:
            dimensions = self.detect_segment_columns()

        results = {}
        all_harmful_segments = []
        all_warnings = []

        for dim in dimensions:
            try:
                analysis = self.analyze_dimension(
                    dimension=dim,
                    metric_col=metric_col,
                    metric_type=metric_type
                )
                results[dim] = analysis
                if analysis.get('harmful_segments'):
                    for h in analysis['harmful_segments']:
                        all_harmful_segments.append({
                            'dimension': dim,
                            **h
                        })
                all_warnings.extend(analysis.get('warnings', []))
            except Exception as e:
                all_warnings.append(f"Could not analyze dimension '{dim}': {str(e)}")

        has_severe_segment_harm = any(
            h.get('lift_pct', 0) <= -10.0 and h.get('sample_size', 0) >= 100
            for h in all_harmful_segments
        )

        return {
            'dimensions_analyzed': list(results.keys()),
            'dimensions': results,
            'all_harmful_segments': all_harmful_segments,
            'has_harmful_segments': len(all_harmful_segments) > 0,
            'has_severe_segment_harm': has_severe_segment_harm,
            'warnings': all_warnings,
            'summary': {
                'dimensions_count': len(results),
                'harmful_segments_count': len(all_harmful_segments),
                'warnings_count': len(all_warnings)
            }
        }
