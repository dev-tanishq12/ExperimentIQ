# Member4/decision_engine.py
# ============================================================
# EXPERIMENTIQ - MEMBER 4: EXPLAINABLE DECISION ENGINE
# ============================================================
# Transparent, multi-tiered rule hierarchy for A/B experiment
# decision making. Evaluates data quality, SRM, significance,
# effect direction, statistical power, and segment-level risks.
# ============================================================

from typing import Dict, Any, List, Optional
import warnings
warnings.filterwarnings('ignore')


class DecisionEngine:
    """
    Explainable Decision Engine for A/B Testing.
    
    Synthesizes evidence from:
    1. Member 1: Data Quality Profiler (quality score, critical issues)
    2. Member 2: Cleaning Assistant (audit status, applied fixes)
    3. Member 3: Experiment Analyzer (SRM, metrics, p-values, power)
    4. Member 4: Segment Analyzer (localized degradation, segment harm)
    
    Outputs one of 4 standardized decisions:
    - 🚀 LAUNCH
    - ❌ DO NOT LAUNCH
    - ⏳ CONTINUE EXPERIMENT
    - ⚠️ INVESTIGATE DATA
    """

    # Recommendation Constants
    LAUNCH = "LAUNCH"
    DO_NOT_LAUNCH = "DO NOT LAUNCH"
    CONTINUE_EXPERIMENT = "CONTINUE EXPERIMENT"
    INVESTIGATE_DATA = "INVESTIGATE DATA"

    def __init__(
        self,
        min_quality_score: float = 0.65,
        alpha: float = 0.05,
        power_target: float = 0.80,
        primary_metric: str = 'conversion'
    ):
        self.min_quality_score = min_quality_score
        self.alpha = alpha
        self.power_target = power_target
        self.primary_metric = primary_metric

    def evaluate(
        self,
        experiment_results: Dict[str, Any],
        quality_report: Optional[Dict[str, Any]] = None,
        cleaning_report: Optional[Dict[str, Any]] = None,
        segment_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate full experiment evidence and return an explainable decision object.
        """
        evidence: List[str] = []
        warnings_list: List[str] = []

        # ----------------------------------------------------
        # Extract Member 1 & 2 Data Quality context
        # ----------------------------------------------------
        quality_score = 1.0
        has_critical_data_issues = False
        critical_issue_descriptions = []

        if quality_report:
            quality_score = quality_report.get('quality_score', 1.0)
            issues = quality_report.get('issues', [])
            for issue in issues:
                if issue.get('severity') == 'critical':
                    # Check if cleaning resolved it
                    resolved = False
                    if cleaning_report:
                        for action in cleaning_report.get('cleaning_actions', []):
                            if action.get('issue_type') == issue.get('type') and action.get('status') in ['approved', 'auto_applied']:
                                resolved = True
                    if not resolved and issue.get('type') == 'duplicate_users_across_groups':
                        has_critical_data_issues = True
                        critical_issue_descriptions.append(issue.get('description', 'Critical data integrity issue'))

        # ----------------------------------------------------
        # Extract Member 3 Experiment Quality & SRM
        # ----------------------------------------------------
        exp_quality = experiment_results.get('experiment_quality', {})
        srm_info = exp_quality.get('srm', {})
        srm_passed = srm_info.get('passed', True)
        srm_p_value = srm_info.get('p_value', 1.0)

        assignment = exp_quality.get('assignment_balance', {})
        assignment_passed = assignment.get('passed', True)
        multiple_users = assignment.get('users_in_multiple_groups', 0)

        # Extract Metrics & Stats
        metrics = experiment_results.get('metrics', {})
        stats_results = experiment_results.get('statistical_analysis', {})
        power_results = experiment_results.get('power_analysis', {})

        primary_stats = stats_results.get(self.primary_metric, {})
        primary_metrics = metrics.get('conversion_rate', {}) if self.primary_metric == 'conversion' else metrics.get(self.primary_metric, {})

        # P-value and significance
        p_value = primary_stats.get('p_value', 1.0)
        is_significant = primary_stats.get('is_significant', False)
        diff = primary_stats.get('difference', 0.0)

        # Lift
        rel_lift = primary_metrics.get('relative_lift_pct', 0.0) if primary_metrics else 0.0
        abs_lift = primary_metrics.get('absolute_lift', diff) if primary_metrics else diff

        # Power
        primary_power = power_results.get(self.primary_metric, {})
        is_powered = primary_power.get('is_adequately_powered', False)
        n_needed = primary_power.get('sample_size_needed')
        n_current = primary_power.get('current_sample_size') or exp_quality.get('group_counts', {}).get('total', 0)

        # ----------------------------------------------------
        # Extract Member 4 Segment Findings
        # ----------------------------------------------------
        has_severe_segment_harm = False
        harmful_segments = []
        if segment_results:
            has_severe_segment_harm = segment_results.get('has_severe_segment_harm', False)
            harmful_segments = segment_results.get('all_harmful_segments', [])
            for w in segment_results.get('warnings', []):
                warnings_list.append(f"Segment warning: {w}")

        # ----------------------------------------------------
        # EVIDENCE COMPILATION
        # ----------------------------------------------------
        if primary_metrics:
            ctrl_val = primary_metrics.get('control_pct', primary_metrics.get('control', 0.0))
            treat_val = primary_metrics.get('treatment_pct', primary_metrics.get('treatment', 0.0))
            evidence.append(
                f"Primary metric ({self.primary_metric}): Control={ctrl_val}%, Treatment={treat_val}% (Lift: {rel_lift:+.2f}% relative, {abs_lift:+.4f} absolute)"
            )

        if p_value is not None:
            evidence.append(f"Statistical test: p-value = {p_value:.6f} (Alpha threshold = {self.alpha})")

        if srm_info:
            evidence.append(f"Sample Ratio Mismatch (SRM): {'PASSED' if srm_passed else 'FAILED'} (Chi-Square p = {srm_p_value:.5f})")

        if primary_power and not primary_power.get('error'):
            pow_str = "ADEQUATELY POWERED" if is_powered else "UNDERPOWERED"
            needed_str = f"Required: {n_needed:,}" if n_needed else ""
            evidence.append(f"Statistical Power: {pow_str} (Current: {n_current:,} users; {needed_str})")

        # ====================================================
        # DECISION LOGIC EVALUATION
        # ====================================================

        # Tier 1: Data Integrity & Allocation Violations
        if not srm_passed:
            decision = self.INVESTIGATE_DATA
            confidence = 0.95
            reason = (
                f"Severe Sample Ratio Mismatch detected (p={srm_p_value:.5f} < 0.05). "
                "Group allocation is statistically imbalanced, meaning users were not assigned randomly or tracking is dropping events in one group."
            )
            warnings_list.append("Experiment invalid due to SRM failure. Do not trust any conversion or revenue metrics.")

        elif has_critical_data_issues or (not assignment_passed and multiple_users > 0):
            decision = self.INVESTIGATE_DATA
            confidence = 0.92
            reason = (
                f"Experiment design compromised: {multiple_users} users appeared in multiple experiment groups simultaneously. "
                "This creates cross-contamination between control and treatment cohorts."
            )
            warnings_list.append("Users leaked across test and control arms. Run Intelligent Cleaning to isolate cohorts.")

        elif quality_score < self.min_quality_score:
            decision = self.INVESTIGATE_DATA
            confidence = 0.88
            reason = (
                f"Data quality score ({quality_score*100:.1f}%) is below acceptable threshold ({self.min_quality_score*100:.0f}%). "
                "Excessive missing values, formatting anomalies, or corrupted records invalidate statistical inferences."
            )
            warnings_list.append("High defect rate in underlying dataset. Review Data Quality Profiler report.")

        # Tier 2: Significant Negative Treatment Impact
        elif is_significant and (diff < 0 or rel_lift < -1.0):
            decision = self.DO_NOT_LAUNCH
            confidence = 0.94
            reason = (
                f"Treatment demonstrates a statistically significant negative impact on {self.primary_metric} "
                f"({rel_lift:.2f}% relative change, p={p_value:.6f}). Launching would degrade core user experience and metrics."
            )
            warnings_list.append("Treatment underperforms control with strong statistical confidence. Reject the variant.")

        # Tier 3: Severe Segment Harm in Overall Winning Experiment
        elif has_severe_segment_harm and is_significant and diff > 0:
            # Overall is positive, but a major segment is suffering heavy losses
            decision = self.INVESTIGATE_DATA
            confidence = 0.80
            harm_summary = ", ".join([f"{h['dimension']}:{h['segment']} ({h['lift_pct']:+.1f}%)" for h in harmful_segments[:3]])
            reason = (
                f"While overall {self.primary_metric} shows a positive lift, critical segment degradation was detected in: {harm_summary}. "
                "Launching globally risks alienating this key user group. Investigate localized bugs or rollout conditionally."
            )
            warnings_list.append(f"Severe localized drop detected in: {harm_summary}. Consider segment-specific launch.")

        # Tier 4: Clear Statistically Significant Winner
        elif is_significant and diff > 0:
            if is_powered or (n_needed and n_current >= n_needed):
                decision = self.LAUNCH
                confidence = 0.95
                reason = (
                    f"Treatment produces a statistically significant positive improvement in {self.primary_metric} "
                    f"({rel_lift:+.2f}% relative lift, p={p_value:.6f}) with adequate statistical power ({n_current:,} users). "
                    "Data quality and experiment integrity checks passed."
                )
            else:
                # Significant and positive, but slightly underpowered on theoretical sample size
                decision = self.LAUNCH
                confidence = 0.85
                reason = (
                    f"Treatment demonstrates a statistically significant positive improvement ({rel_lift:+.2f}%, p={p_value:.6f}). "
                    "Sample size is close to target. Deployment is supported with ongoing post-launch telemetry."
                )
                warnings_list.append("Statistical power is marginally below 80% target; maintain guardrails during initial rollout.")

        # Tier 5: Inconclusive / Underpowered / Null Result
        else:
            decision = self.CONTINUE_EXPERIMENT
            confidence = 0.86
            if not is_powered and n_needed and n_current < n_needed:
                samples_remaining = max(0, n_needed - n_current)
                reason = (
                    f"Observed effect ({rel_lift:+.2f}%) has not reached statistical significance (p={p_value:.4f} >= {self.alpha}). "
                    f"The test is currently underpowered ({n_current:,} / {n_needed:,} users). "
                    f"Collect approximately {samples_remaining:,} more users before making a final decision."
                )
            else:
                reason = (
                    f"The difference between control and treatment is not statistically distinguishable from random noise (p={p_value:.4f}). "
                    "Continue data collection to detect smaller effect sizes or terminate if test duration window has elapsed."
                )
            warnings_list.append("Do not ship unverified variants based on directional trends alone.")

        return {
            'decision': decision,
            'confidence': round(confidence, 2),
            'confidence_pct': int(confidence * 100),
            'reason': reason,
            'evidence': evidence,
            'warnings': warnings_list,
            'summary': {
                'quality_score_pct': round(quality_score * 100, 1),
                'srm_passed': srm_passed,
                'is_significant': is_significant,
                'p_value': round(p_value, 6) if p_value is not None else None,
                'relative_lift_pct': round(rel_lift, 2),
                'is_powered': is_powered,
                'has_segment_harm': len(harmful_segments) > 0
            }
        }
