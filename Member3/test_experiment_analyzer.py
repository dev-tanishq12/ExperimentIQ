# Member3/test_experiment_analyzer.py
# ============================================================
# Unit tests for Member 3 - Experiment Analysis Engine
# ============================================================

import unittest
import pandas as pd
import numpy as np
import json
import os
import shutil
from experiment_analyzer import ExperimentAnalyzer


class TestExperimentAnalyzer(unittest.TestCase):
    
    def setUp(self):
        """Create test data."""
        np.random.seed(42)
        
        n = 1000
        control = pd.DataFrame({
            'user_id': [f'user_{i}' for i in range(n//2)],
            'experiment_group': ['control'] * (n//2),
            'conversion': np.random.binomial(1, 0.10, n//2),
            'revenue': np.random.normal(100, 30, n//2).clip(0),
            'session_duration': np.random.normal(300, 60, n//2).clip(0)
        })
        
        treatment = pd.DataFrame({
            'user_id': [f'user_{i}' for i in range(n//2, n)],
            'experiment_group': ['treatment'] * (n//2),
            'conversion': np.random.binomial(1, 0.13, n//2),
            'revenue': np.random.normal(110, 30, n//2).clip(0),
            'session_duration': np.random.normal(310, 60, n//2).clip(0)
        })
        
        self.df = pd.concat([control, treatment]).sample(frac=1).reset_index(drop=True)
        
        os.makedirs('test_output', exist_ok=True)
        self.df.to_csv('test_output/cleaned_data.csv', index=False)
        
        cleaning_report = {
            'timestamp': '2024-01-15T10:00:00',
            'actions_summary': {'total_actions': 5, 'approved': 5, 'rejected': 0}
        }
        with open('test_output/cleaning_report.json', 'w') as f:
            json.dump(cleaning_report, f)
    
    def tearDown(self):
        if os.path.exists('test_output'):
            shutil.rmtree('test_output')
    
    def test_init(self):
        """Test initialization."""
        analyzer = ExperimentAnalyzer('test_output/cleaned_data.csv')
        self.assertIsNotNone(analyzer.df)
        self.assertEqual(len(analyzer.df), 1000)
    
    def test_experiment_quality(self):
        """Test quality checks."""
        analyzer = ExperimentAnalyzer('test_output/cleaned_data.csv')
        results = analyzer.check_experiment_quality()
        self.assertIn('group_counts', results)
        self.assertIn('srm', results)
    
    def test_metrics(self):
        """Test metric calculations."""
        analyzer = ExperimentAnalyzer('test_output/cleaned_data.csv')
        results = analyzer.calculate_metrics()
        self.assertIn('conversion_rate', results)
        self.assertIn('revenue_per_user', results)
    
    def test_statistical_analysis(self):
        """Test statistical analysis."""
        analyzer = ExperimentAnalyzer('test_output/cleaned_data.csv')
        analyzer.calculate_metrics()
        results = analyzer.perform_statistical_analysis()
        self.assertIn('conversion', results)
        self.assertIn('revenue', results)
    
    def test_power_analysis(self):
        """Test power analysis."""
        analyzer = ExperimentAnalyzer('test_output/cleaned_data.csv')
        analyzer.calculate_metrics()
        results = analyzer.calculate_power_analysis()
        self.assertIn('power_target', results)
        self.assertIn('conversion', results)
    
    def test_full_pipeline(self):
        """Test full pipeline."""
        analyzer = ExperimentAnalyzer('test_output/cleaned_data.csv')
        report = analyzer.run_pipeline('test_output/')
        self.assertIn('summary', report)
        self.assertIn('recommendation', report['summary'])


if __name__ == '__main__':
    unittest.main()