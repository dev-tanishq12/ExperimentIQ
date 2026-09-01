# Member3/experiment_analyzer.py
# ============================================================
# EXPERIMENTIQ - MEMBER 3: EXPERIMENT ANALYSIS ENGINE
# ============================================================
# Consumes: cleaned_data.csv from Member 2
# Produces: experiment_report.json for Member 4
# ============================================================

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import norm, ttest_ind, chi2_contingency
from statsmodels.stats.proportion import proportions_ztest
from statsmodels.stats.power import TTestIndPower, GofChisquarePower
import json
import os

def _json_default(obj):
    """Convert NumPy values to native Python values for JSON output."""
    if isinstance(obj, np.generic):
        return obj.item()
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


class ExperimentAnalyzer:
    """
    Experiment Analysis Engine - Member 3
    
    Pipeline: cleaned_data.csv → Experiment Analysis → results for Member 4
    """
    
    def __init__(self, cleaned_data_path: str, cleaning_report_path: Optional[str] = None):
        """
        Initialize with Member 2's cleaned data.
        """
        print("=" * 70)
        print("🔬 ExperimentIQ - Member 3: Experiment Analysis Engine")
        print("=" * 70)
        
        print("\n📂 Loading cleaned data from Member 2...")
        self.df = pd.read_csv(cleaned_data_path)
        
        if cleaning_report_path and os.path.exists(cleaning_report_path):
            with open(cleaning_report_path, 'r') as f:
                self.cleaning_report = json.load(f)
            print(f"   ✅ Loaded cleaning report")
        else:
            self.cleaning_report = None
        
        print(f"   ✅ Loaded {len(self.df)} rows, {len(self.df.columns)} columns")
        
        # Storage for results
        self.quality_results = {}
        self.metric_results = {}
        self.statistical_results = {}
        self.power_results = {}
        
        # Configuration
        self.config = {
            'alpha': 0.05,
            'beta': 0.20,
            'power_target': 0.80,
            'group_column': 'experiment_group',
            'user_column': 'user_id',
            'control_group': 'control',
            'treatment_group': 'treatment',
            'metrics': {
                'conversion': {'type': 'proportion', 'column': 'conversion'},
                'revenue': {'type': 'continuous', 'column': 'revenue'},
                'session_duration': {'type': 'continuous', 'column': 'session_duration'}
            }
        }
        
        # Auto-detect columns if needed
        self._detect_columns()
    
    def _detect_columns(self):
        """Auto-detect important columns if not found."""
        # Try to find group column
        if self.config['group_column'] not in self.df.columns:
            for col in self.df.columns:
                if 'group' in col.lower() or 'variant' in col.lower():
                    self.config['group_column'] = col
                    break
        
        # Try to find user column
        if self.config['user_column'] not in self.df.columns:
            for col in self.df.columns:
                if 'user' in col.lower() or 'id' in col.lower():
                    self.config['user_column'] = col
                    break
    
    def check_experiment_quality(self) -> Dict:
        """
        Step 5: Check experiment validity.
        - Sample Ratio Mismatch (SRM)
        - Assignment balance
        """
        print("\n" + "=" * 70)
        print("🔍 Step 5: Experiment Quality Checks")
        print("=" * 70)
        
        group_col = self.config['group_column']
        
        # Get group counts
        group_counts = self.df[group_col].value_counts()
        total = len(self.df)
        
        control_count = group_counts.get('control', group_counts.iloc[0] if len(group_counts) > 0 else 0)
        treatment_count = group_counts.get('treatment', group_counts.iloc[1] if len(group_counts) > 1 else 0)
        
        # SRM Test (Chi-square)
        expected_control = total / 2
        expected_treatment = total / 2
        
        observed = [control_count, treatment_count]
        expected = [expected_control, expected_treatment]
        
        chi2, p_value = stats.chisquare(observed, expected)
        is_srm = bool(p_value < 0.05)
        
        # Assignment balance check
        user_col = self.config['user_column']
        unique_users = self.df[user_col].nunique() if user_col in self.df.columns else total
        users_multiple = 0
        
        if user_col in self.df.columns:
            users_in_multiple = self.df.groupby(user_col)[group_col].nunique()
            users_multiple = users_in_multiple[users_in_multiple > 1].sum()
        
        results = {
            'group_counts': {
                'control': int(control_count),
                'treatment': int(treatment_count),
                'total': int(total),
                'control_pct': round(control_count / total * 100, 2),
                'treatment_pct': round(treatment_count / total * 100, 2)
            },
            'srm': {
                'chi2_statistic': round(chi2, 4),
                'p_value': round(p_value, 6),
                'is_significant': is_srm,
                'passed': not is_srm,
                'interpretation': '⚠️ SRM DETECTED' if is_srm else '✅ Balanced allocation'
            },
            'assignment_balance': {
                'unique_users': int(unique_users),
                'users_in_multiple_groups': int(users_multiple),
                'passed': users_multiple == 0
            },
            'quality_status': '✅ PASS' if not is_srm and users_multiple == 0 else '⚠️ ISSUES DETECTED'
        }
        
        self.quality_results = results
        
        print(f"   Control group:   {int(control_count):,} users ({control_count/total*100:.1f}%)")
        print(f"   Treatment group: {int(treatment_count):,} users ({treatment_count/total*100:.1f}%)")
        print(f"   SRM test:        {'PASS — groups are balanced' if not is_srm else 'FAIL — possible sample ratio mismatch'}")
        print(f"   SRM p-value:     {float(p_value):.6f}")
        print(f"   Assignment:      {'PASS — users stay in one group' if users_multiple == 0 else f'CHECK — {int(users_multiple):,} users appear in multiple groups'}")
        
        return results
    
    def calculate_metrics(self) -> Dict:
        """
        Step 6: Calculate experiment metrics.
        """
        print("\n" + "=" * 70)
        print("📊 Step 6: Metric Engine")
        print("=" * 70)
        
        group_col = self.config['group_column']
        control_df = self.df[self.df[group_col] == 'control']
        treatment_df = self.df[self.df[group_col] == 'treatment']
        
        metrics = {}
        
        # 1. Conversion Rate
        if 'conversion' in self.df.columns:
            conv_control = control_df['conversion'].mean()
            conv_treatment = treatment_df['conversion'].mean()
            conv_lift = ((conv_treatment - conv_control) / conv_control * 100) if conv_control > 0 else 0
            
            metrics['conversion_rate'] = {
                'control': round(float(conv_control), 4),
                'treatment': round(float(conv_treatment), 4),
                'control_pct': round(float(conv_control * 100), 2),
                'treatment_pct': round(float(conv_treatment * 100), 2),
                'absolute_lift': round(float(conv_treatment - conv_control), 4),
                'relative_lift_pct': round(float(conv_lift), 2),
                'control_conversions': int(control_df['conversion'].sum()),
                'treatment_conversions': int(treatment_df['conversion'].sum())
            }
            print(f"   Conversion: {conv_control*100:.2f}% → {conv_treatment*100:.2f}%")
            print(f"      Absolute change: {float((conv_treatment - conv_control) * 100):+.2f} percentage points")
            print(f"      Relative lift:   {float(conv_lift):+.1f}%")
        
        # 2. Revenue Per User
        if 'revenue' in self.df.columns:
            rev_control = control_df['revenue'].mean()
            rev_treatment = treatment_df['revenue'].mean()
            rev_lift = ((rev_treatment - rev_control) / rev_control * 100) if rev_control > 0 else 0
            
            metrics['revenue_per_user'] = {
                'control': round(float(rev_control), 2),
                'treatment': round(float(rev_treatment), 2),
                'absolute_lift': round(float(rev_treatment - rev_control), 2),
                'relative_lift_pct': round(float(rev_lift), 2)
            }
            print(f"   Revenue/user: ${rev_control:.2f} → ${rev_treatment:.2f}")
            print(f"      Change:        ${float(rev_treatment - rev_control):+.2f} per user")
            print(f"      Relative lift: {float(rev_lift):+.1f}%")
        
        # 3. Session Duration
        if 'session_duration' in self.df.columns:
            dur_control = control_df['session_duration'].mean()
            dur_treatment = treatment_df['session_duration'].mean()
            dur_lift = ((dur_treatment - dur_control) / dur_control * 100) if dur_control > 0 else 0
            
            metrics['session_duration'] = {
                'control': round(float(dur_control), 2),
                'treatment': round(float(dur_treatment), 2),
                'absolute_lift': round(float(dur_treatment - dur_control), 2),
                'relative_lift_pct': round(float(dur_lift), 2)
            }
            print(f"   Session duration: {dur_control:.1f}s → {dur_treatment:.1f}s")
            print(f"      Change:        {float(dur_treatment - dur_control):+.1f} seconds")
            print(f"      Relative lift: {float(dur_lift):+.1f}%")
        
        self.metric_results = metrics
        return metrics
    
    def perform_statistical_analysis(self) -> Dict:
        """
        Step 7: Statistical analysis.
        - Hypothesis tests
        - P-values
        - Confidence intervals
        - Effect sizes
        """
        print("\n" + "=" * 70)
        print("📈 Step 7: Statistical Analysis")
        print("=" * 70)
        
        group_col = self.config['group_column']
        alpha = self.config['alpha']
        
        control_df = self.df[self.df[group_col] == 'control']
        treatment_df = self.df[self.df[group_col] == 'treatment']
        
        results = {}
        
        # 1. Conversion Test (Proportion Z-test)
        if 'conversion' in self.df.columns:
            n1 = len(control_df)
            n2 = len(treatment_df)
            x1 = control_df['conversion'].sum()
            x2 = treatment_df['conversion'].sum()
            
            try:
                z_stat, p_value = proportions_ztest([x1, x2], [n1, n2])
                p1 = x1 / n1
                p2 = x2 / n2
                
                # Confidence interval
                se = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
                z_critical = norm.ppf(1 - alpha / 2)
                ci_lower = (p2 - p1) - z_critical * se
                ci_upper = (p2 - p1) + z_critical * se
                
                # Effect size (Cohen's h)
                import math
                h = 2 * math.asin(np.sqrt(p2)) - 2 * math.asin(np.sqrt(p1))
                
                results['conversion'] = {
                    'test_type': 'Proportion Z-Test',
                    'control_rate': round(float(p1), 4),
                    'treatment_rate': round(float(p2), 4),
                    'difference': round(float(p2 - p1), 4),
                    'z_statistic': round(float(z_stat), 4),
                    'p_value': round(float(p_value), 6),
                    'is_significant': bool(p_value < alpha),
                    'confidence_interval': {
                        'lower': round(float(ci_lower), 4),
                        'upper': round(float(ci_upper), 4),
                        'level': '95%'
                    },
                    'effect_size': {
                        'cohens_h': round(float(h), 4),
                        'interpretation': self._interpret_effect_size(h)
                    }
                }
                print(f"   Conversion: p={float(p_value):.6f} — {'SIGNIFICANT' if p_value < alpha else 'NOT SIGNIFICANT'}")
                print(f"      Meaning: {'Evidence supports a real difference.' if p_value < alpha else 'The observed difference could be random variation.'}")
            except Exception as e:
                results['conversion'] = {'error': str(e)}
        
        # 2. Revenue Test (Welch's t-test)
        if 'revenue' in self.df.columns:
            rev_control = control_df['revenue'].dropna()
            rev_treatment = treatment_df['revenue'].dropna()
            
            if len(rev_control) > 0 and len(rev_treatment) > 0:
                try:
                    t_stat, p_value = ttest_ind(rev_treatment, rev_control, equal_var=False)
                    
                    # Effect size (Cohen's d)
                    pooled_std = np.sqrt((rev_control.std()**2 + rev_treatment.std()**2) / 2)
                    cohens_d = (rev_treatment.mean() - rev_control.mean()) / pooled_std if pooled_std > 0 else 0
                    
                    # Confidence interval
                    from scipy.stats import t
                    se = np.sqrt(rev_control.var()/len(rev_control) + rev_treatment.var()/len(rev_treatment))
                    df = len(rev_control) + len(rev_treatment) - 2
                    t_critical = t.ppf(1 - alpha/2, df)
                    ci_lower = (rev_treatment.mean() - rev_control.mean()) - t_critical * se
                    ci_upper = (rev_treatment.mean() - rev_control.mean()) + t_critical * se
                    
                    results['revenue'] = {
                        'test_type': "Welch's t-test",
                        'control_mean': round(float(rev_control.mean()), 2),
                        'treatment_mean': round(float(rev_treatment.mean()), 2),
                        'difference': round(float(rev_treatment.mean() - rev_control.mean()), 2),
                        't_statistic': round(float(t_stat), 4),
                        'p_value': round(float(p_value), 6),
                        'is_significant': bool(p_value < alpha),
                        'confidence_interval': {
                            'lower': round(float(ci_lower), 2),
                            'upper': round(float(ci_upper), 2),
                            'level': '95%'
                        },
                        'effect_size': {
                            'cohens_d': round(float(cohens_d), 4),
                            'interpretation': self._interpret_cohens_d(cohens_d)
                        }
                    }
                    print(f"   Revenue: p={float(p_value):.6f} — {'SIGNIFICANT' if p_value < alpha else 'NOT SIGNIFICANT'}")
                    print(f"      Meaning: {'Evidence supports a real difference.' if p_value < alpha else 'The observed difference could be random variation.'}")
                except Exception as e:
                    results['revenue'] = {'error': str(e)}
        
        # 3. Session Duration Test
        if 'session_duration' in self.df.columns:
            dur_control = control_df['session_duration'].dropna()
            dur_treatment = treatment_df['session_duration'].dropna()
            
            if len(dur_control) > 0 and len(dur_treatment) > 0:
                try:
                    t_stat, p_value = ttest_ind(dur_treatment, dur_control, equal_var=False)
                    
                    pooled_std = np.sqrt((dur_control.std()**2 + dur_treatment.std()**2) / 2)
                    cohens_d = (dur_treatment.mean() - dur_control.mean()) / pooled_std if pooled_std > 0 else 0
                    
                    results['session_duration'] = {
                        'test_type': "Welch's t-test",
                        'control_mean': round(float(dur_control.mean()), 2),
                        'treatment_mean': round(float(dur_treatment.mean()), 2),
                        'difference': round(float(dur_treatment.mean() - dur_control.mean()), 2),
                        't_statistic': round(float(t_stat), 4),
                        'p_value': round(float(p_value), 6),
                        'is_significant': bool(p_value < alpha),
                        'effect_size': {
                            'cohens_d': round(float(cohens_d), 4),
                            'interpretation': self._interpret_cohens_d(cohens_d)
                        }
                    }
                    print(f"   Session duration: p={float(p_value):.6f} — {'SIGNIFICANT' if p_value < alpha else 'NOT SIGNIFICANT'}")
                    print(f"      Meaning: {'Evidence supports a real difference.' if p_value < alpha else 'The observed difference could be random variation.'}")
                except Exception as e:
                    results['session_duration'] = {'error': str(e)}
        
        self.statistical_results = results
        return results
    
    def _interpret_effect_size(self, h: float) -> str:
        """Interpret Cohen's h."""
        abs_h = abs(h)
        if abs_h < 0.2:
            return "Small effect"
        elif abs_h < 0.5:
            return "Medium effect"
        elif abs_h < 0.8:
            return "Large effect"
        else:
            return "Very large effect"
    
    def _interpret_cohens_d(self, d: float) -> str:
        """Interpret Cohen's d."""
        abs_d = abs(d)
        if abs_d < 0.2:
            return "Very small effect"
        elif abs_d < 0.5:
            return "Small effect"
        elif abs_d < 0.8:
            return "Medium effect"
        else:
            return "Large effect"
    
    def calculate_power_analysis(self) -> Dict:
        """
        Step 8: Power & Sample Analysis.
        """
        print("\n" + "=" * 70)
        print("⚡ Step 8: Power & Sample Analysis")
        print("=" * 70)
        
        alpha = self.config['alpha']
        power_target = self.config['power_target']
        
        results = {
            'power_target': power_target,
            'alpha': alpha,
            'beta': round(1 - power_target, 2)
        }
        
        # Conversion power
        if 'conversion' in self.df.columns:
            p1 = self.df[self.df[self.config['group_column']] == 'control']['conversion'].mean()
            p2 = self.df[self.df[self.config['group_column']] == 'treatment']['conversion'].mean()
            
            n_current = len(self.df)
            
            # Effect size for proportion
            import math
            h = 2 * math.asin(np.sqrt(p2)) - 2 * math.asin(np.sqrt(p1))
            
            try:
                power_analysis = GofChisquarePower()
                n_needed = power_analysis.solve_power(effect_size=h, power=power_target, alpha=alpha)
                
                results['conversion'] = {
                    'control_rate': round(float(p1), 4),
                    'treatment_rate': round(float(p2), 4),
                    'absolute_difference': round(float(p2 - p1), 4),
                    'relative_lift_pct': round(float(((p2 - p1) / p1 * 100) if p1 > 0 else 0), 2),
                    'sample_size_needed': int(n_needed * 2),
                    'current_sample_size': n_current,
                    'is_adequately_powered': bool(n_current >= n_needed * 2),
                    'interpretation': '✅ Adequately powered' if n_current >= n_needed * 2 else f'⚠️ Need {int(n_needed*2):,} samples (have {n_current:,})'
                }
                status = 'POWERED' if n_current >= n_needed * 2 else 'UNDERPOWERED'
                print(f"   Conversion: {status}")
                print(f"      Required sample: {int(n_needed*2):,} total users")
                print(f"      Current sample:  {int(n_current):,} users")
            except Exception as e:
                results['conversion'] = {'error': str(e)}
        
        # Revenue power
        if 'revenue' in self.df.columns:
            rev_control = self.df[self.df[self.config['group_column']] == 'control']['revenue'].dropna()
            rev_treatment = self.df[self.df[self.config['group_column']] == 'treatment']['revenue'].dropna()
            
            if len(rev_control) > 0 and len(rev_treatment) > 0:
                try:
                    pooled_std = np.sqrt((rev_control.std()**2 + rev_treatment.std()**2) / 2)
                    effect_size = (rev_treatment.mean() - rev_control.mean()) / pooled_std if pooled_std > 0 else 0
                    
                    power_analysis = TTestIndPower()
                    n_needed = power_analysis.solve_power(effect_size=effect_size, power=power_target, alpha=alpha)
                    
                    results['revenue'] = {
                        'effect_size': round(float(effect_size), 4),
                        'sample_size_needed': int(n_needed * 2),
                        'current_sample_size': len(self.df),
                        'is_adequately_powered': bool(len(self.df) >= n_needed * 2),
                        'interpretation': '✅ Adequately powered' if len(self.df) >= n_needed * 2 else f'⚠️ Need {int(n_needed*2):,} samples (have {len(self.df):,})'
                    }
                    status = 'POWERED' if len(self.df) >= n_needed * 2 else 'UNDERPOWERED'
                    print(f"   Revenue: {status}")
                    print(f"      Required sample: {int(n_needed*2):,} total users")
                    print(f"      Current sample:  {len(self.df):,} users")
                except Exception as e:
                    results['revenue'] = {'error': str(e)}
        
        self.power_results = results
        return results
    
    def generate_report(self) -> Dict:
        """
        Generate complete experiment report for Member 4.
        """
        print("\n📝 Generating experiment report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'source': {
                'cleaned_data': 'from Member 2',
                'cleaning_report': 'from Member 2' if self.cleaning_report else 'Not available'
            },
            'config': self.config,
            'experiment_quality': self.quality_results,
            'metrics': self.metric_results,
            'statistical_analysis': self.statistical_results,
            'power_analysis': self.power_results,
            'summary': self._generate_summary()
        }
        
        return report
    
    def _generate_summary(self) -> Dict:
        """Generate executive summary."""
        summary = {
            'quality_status': self.quality_results.get('quality_status', 'Unknown'),
            'significant_metrics': [],
            'recommendation': 'Continue Experiment'
        }
        
        # Find significant metrics
        for metric, data in self.statistical_results.items():
            if isinstance(data, dict) and data.get('is_significant', False):
                summary['significant_metrics'].append(metric)
        
        # Generate recommendation
        quality_ok = self.quality_results.get('quality_status') == '✅ PASS'
        has_significant = len(summary['significant_metrics']) > 0
        
        if not quality_ok:
            summary['recommendation'] = '🔴 INVESTIGATE DATA - Experiment quality issues detected'
        elif has_significant:
            summary['recommendation'] = '🟢 LAUNCH - Statistically significant results found'
        else:
            summary['recommendation'] = '🟡 CONTINUE EXPERIMENT - No significant results yet'
        
        return summary
    
    def save_report(self, output_dir: str = 'sample_output/') -> str:
        """Save report as JSON."""
        os.makedirs(output_dir, exist_ok=True)
        report = self.generate_report()
        path = os.path.join(output_dir, 'experiment_report.json')
        with open(path, 'w') as f:
            json.dump(report, f, indent=2, default=_json_default)
        print(f"💾 Report saved to: {path}")
        return path
    
    def save_summary(self, output_dir: str = 'sample_output/') -> str:
        """Save summary as CSV."""
        os.makedirs(output_dir, exist_ok=True)
        
        summary_data = []
        for metric, data in self.metric_results.items():
            summary_data.append({
                'Metric': metric,
                'Control': data.get('control', 0),
                'Treatment': data.get('treatment', 0),
                'Lift_%': data.get('relative_lift_pct', 0),
                'Significant': 'Yes' if self.statistical_results.get(metric, {}).get('is_significant', False) else 'No',
                'P_Value': self.statistical_results.get(metric, {}).get('p_value', 1)
            })
        
        df_summary = pd.DataFrame(summary_data)
        path = os.path.join(output_dir, 'experiment_summary.csv')
        df_summary.to_csv(path, index=False)
        print(f"💾 Summary saved to: {path}")
        return path
    
    def run_pipeline(self, output_dir: str = 'sample_output/') -> Dict:
        """
        Run the complete analysis pipeline.
        """
        print("\n" + "=" * 70)
        print("🚀 RUNNING COMPLETE PIPELINE")
        print("=" * 70)
        
        self.check_experiment_quality()
        self.calculate_metrics()
        self.perform_statistical_analysis()
        self.calculate_power_analysis()
        self.save_report(output_dir)
        self.save_summary(output_dir)
        
        # Print final recommendation
        summary = self._generate_summary()
        print("\n" + "=" * 70)
        print("📌 FINAL RECOMMENDATION")
        print("=" * 70)
        print(f"   {summary['recommendation']}")
        print("=" * 70)
        
        summary = self._generate_summary()
        print("\n" + "=" * 70)
        print("📌 FINAL EXPERIMENT INTERPRETATION")
        print("=" * 70)
        print(f"   Experiment quality: {summary['quality_status']}")
        print(f"   Significant metrics: {', '.join(summary['significant_metrics']) if summary['significant_metrics'] else 'None'}")
        print(f"   Recommendation: {summary['recommendation']}")
        print("\n   In plain English:")
        if summary['quality_status'] == '✅ PASS':
            print("   • The experiment passed the basic quality checks.")
        else:
            print("   • Investigate the experiment setup before trusting the results.")
        if self.statistical_results.get('conversion', {}).get('is_significant') is False:
            print("   • Conversion shows a difference, but it is NOT statistically significant.")
        elif self.statistical_results.get('conversion', {}).get('is_significant') is True:
            print("   • Conversion shows a statistically significant difference.")
        if self.statistical_results.get('revenue', {}).get('is_significant') is True:
            print("   • Revenue shows a statistically significant difference.")
        if self.statistical_results.get('session_duration', {}).get('is_significant') is True:
            print("   • Session duration shows a statistically significant difference.")
        if self.power_results.get('conversion', {}).get('is_adequately_powered') is False:
            print("   • Conversion is underpowered; more users are needed for the target power.")
        elif self.power_results.get('conversion', {}).get('is_adequately_powered') is True:
            print("   • Conversion has adequate sample size for the calculated target.")
        print("=" * 70)

        return self.generate_report()


# ============================================================
# MAIN - Run the pipeline
# ============================================================
if __name__ == "__main__":
    import sys
    
    # Paths (adjust based on your structure)
    CLEANED_DATA_PATH = '../Member2/sample_output/cleaned_data.csv'
    CLEANING_REPORT_PATH = '../Member2/sample_output/cleaning_report.json'
    OUTPUT_DIR = 'sample_output/'
    
    # Check if cleaned data exists
    if not os.path.exists(CLEANED_DATA_PATH):
        print(f"❌ Error: Cleaned data not found at {CLEANED_DATA_PATH}")
        print("   Please run Member 2 first to generate cleaned_data.csv")
        sys.exit(1)
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Run the pipeline
    analyzer = ExperimentAnalyzer(CLEANED_DATA_PATH, CLEANING_REPORT_PATH)
    report = analyzer.run_pipeline(OUTPUT_DIR)
    
    print("\n✅ Member 3 complete! Results ready for Member 4.")