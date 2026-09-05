# Member4/tests/test_decision_engine.py
import unittest
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'Member4'))

from decision_engine import DecisionEngine


class TestDecisionEngine(unittest.TestCase):

    def setUp(self):
        self.engine = DecisionEngine(min_quality_score=0.65, alpha=0.05, power_target=0.80)

    def test_scenario_1_launch(self):
        """Scenario 1: Valid + Significant Positive Effect + Adequately Powered -> LAUNCH"""
        exp_results = {
            'experiment_quality': {
                'srm': {'passed': True, 'p_value': 0.85},
                'assignment_balance': {'passed': True, 'users_in_multiple_groups': 0}
            },
            'metrics': {
                'conversion_rate': {
                    'control': 0.10,
                    'treatment': 0.14,
                    'absolute_lift': 0.04,
                    'relative_lift_pct': 40.0
                }
            },
            'statistical_analysis': {
                'conversion': {
                    'p_value': 0.001,
                    'is_significant': True,
                    'difference': 0.04
                }
            },
            'power_analysis': {
                'conversion': {
                    'is_adequately_powered': True,
                    'sample_size_needed': 3000,
                    'current_sample_size': 4000
                }
            }
        }
        res = self.engine.evaluate(exp_results)
        self.assertEqual(res['decision'], DecisionEngine.LAUNCH)
        self.assertIn("statistically significant positive improvement", res['reason'])

    def test_scenario_2_do_not_launch(self):
        """Scenario 2: Valid + Significant Negative Effect -> DO NOT LAUNCH"""
        exp_results = {
            'experiment_quality': {
                'srm': {'passed': True, 'p_value': 0.72},
                'assignment_balance': {'passed': True, 'users_in_multiple_groups': 0}
            },
            'metrics': {
                'conversion_rate': {
                    'control': 0.12,
                    'treatment': 0.08,
                    'absolute_lift': -0.04,
                    'relative_lift_pct': -33.33
                }
            },
            'statistical_analysis': {
                'conversion': {
                    'p_value': 0.002,
                    'is_significant': True,
                    'difference': -0.04
                }
            },
            'power_analysis': {
                'conversion': {
                    'is_adequately_powered': True,
                    'current_sample_size': 4000
                }
            }
        }
        res = self.engine.evaluate(exp_results)
        self.assertEqual(res['decision'], DecisionEngine.DO_NOT_LAUNCH)
        self.assertIn("negative impact", res['reason'].lower())

    def test_scenario_3_continue_experiment(self):
        """Scenario 3: Valid + Inconclusive / Underpowered -> CONTINUE EXPERIMENT"""
        exp_results = {
            'experiment_quality': {
                'srm': {'passed': True, 'p_value': 0.90},
                'assignment_balance': {'passed': True, 'users_in_multiple_groups': 0}
            },
            'metrics': {
                'conversion_rate': {
                    'control': 0.10,
                    'treatment': 0.11,
                    'absolute_lift': 0.01,
                    'relative_lift_pct': 10.0
                }
            },
            'statistical_analysis': {
                'conversion': {
                    'p_value': 0.45,
                    'is_significant': False,
                    'difference': 0.01
                }
            },
            'power_analysis': {
                'conversion': {
                    'is_adequately_powered': False,
                    'sample_size_needed': 3200,
                    'current_sample_size': 400
                }
            }
        }
        res = self.engine.evaluate(exp_results)
        self.assertEqual(res['decision'], DecisionEngine.CONTINUE_EXPERIMENT)

    def test_scenario_4_poor_data_quality(self):
        """Scenario 4: Poor data quality (< 0.65) -> INVESTIGATE DATA"""
        exp_results = {
            'experiment_quality': {
                'srm': {'passed': True, 'p_value': 0.88},
                'assignment_balance': {'passed': True, 'users_in_multiple_groups': 0}
            },
            'metrics': {
                'conversion_rate': {'control': 0.10, 'treatment': 0.15, 'relative_lift_pct': 50.0}
            },
            'statistical_analysis': {
                'conversion': {'p_value': 0.01, 'is_significant': True, 'difference': 0.05}
            },
            'power_analysis': {
                'conversion': {'is_adequately_powered': True, 'current_sample_size': 5000}
            }
        }
        quality_report = {'quality_score': 0.45, 'issues': []}
        res = self.engine.evaluate(exp_results, quality_report=quality_report)
        self.assertEqual(res['decision'], DecisionEngine.INVESTIGATE_DATA)
        self.assertIn("quality score", res['reason'].lower())

    def test_scenario_5_srm_failure(self):
        """Scenario 5: SRM failure -> INVESTIGATE DATA"""
        exp_results = {
            'experiment_quality': {
                'srm': {'passed': False, 'p_value': 0.00002},
                'assignment_balance': {'passed': True, 'users_in_multiple_groups': 0}
            },
            'metrics': {
                'conversion_rate': {'control': 0.10, 'treatment': 0.15, 'relative_lift_pct': 50.0}
            },
            'statistical_analysis': {
                'conversion': {'p_value': 0.01, 'is_significant': True, 'difference': 0.05}
            }
        }
        res = self.engine.evaluate(exp_results)
        self.assertEqual(res['decision'], DecisionEngine.INVESTIGATE_DATA)
        self.assertIn("sample ratio mismatch", res['reason'].lower())

    def test_scenario_6_severe_segment_harm(self):
        """Scenario 6: Overall positive but large credible segment suffering harm -> INVESTIGATE DATA with warning"""
        exp_results = {
            'experiment_quality': {
                'srm': {'passed': True, 'p_value': 0.85},
                'assignment_balance': {'passed': True, 'users_in_multiple_groups': 0}
            },
            'metrics': {
                'conversion_rate': {'control': 0.10, 'treatment': 0.13, 'relative_lift_pct': 30.0}
            },
            'statistical_analysis': {
                'conversion': {'p_value': 0.02, 'is_significant': True, 'difference': 0.03}
            },
            'power_analysis': {
                'conversion': {'is_adequately_powered': True, 'current_sample_size': 4000}
            }
        }
        segment_results = {
            'has_severe_segment_harm': True,
            'all_harmful_segments': [
                {'dimension': 'device', 'segment': 'mobile', 'lift_pct': -25.0, 'sample_size': 1200}
            ],
            'warnings': ["Mobile users experience -25% drop"]
        }
        res = self.engine.evaluate(exp_results, segment_results=segment_results)
        self.assertEqual(res['decision'], DecisionEngine.INVESTIGATE_DATA)
        self.assertIn("segment degradation", res['reason'].lower())


if __name__ == '__main__':
    unittest.main()
