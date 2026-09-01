# Member2/test_cleaning.py

import unittest
import pandas as pd
import numpy as np
import json
import os
import shutil
from cleaning_assistant import CleaningAssistant

class TestCleaningAssistant(unittest.TestCase):
    
    def setUp(self):
        """Create test data and quality report."""
        
        # Create test data
        self.test_df = pd.DataFrame({
            'user_id': ['user_001', 'user_002', 'user_003', 'user_004', 'user_005'],
            'experiment_group': ['control', 'test', 'treatment', 'Control', 'treatment'],
            'conversion': [1, np.nan, 2, 0, 1],
            'revenue': [100.50, 200.75, np.nan, 150.25, -50.00],
            'date': ['2024-01-01', '01/15/2024', '2024-02-01', '02/15/2024', '2024-03-01']
        })
        
        # Create quality report (mimicking Member 1)
        self.quality_report = {
            'report_timestamp': '2024-01-15T10:00:00',
            'file_info': {'rows': 5, 'columns': 5},
            'issues': [
                {
                    'column': 'conversion',
                    'type': 'missing_values',
                    'severity': 'high',
                    'count': 1,
                    'pct': 20.0
                },
                {
                    'column': 'experiment_group',
                    'type': 'invalid_values',
                    'severity': 'high',
                    'invalid_values': ['test'],
                    'count': 1
                },
                {
                    'column': 'revenue',
                    'type': 'outliers',
                    'severity': 'medium',
                    'count': 1,
                    'bounds': {'lower': 0, 'upper': 300}
                },
                {
                    'column': 'date',
                    'type': 'inconsistent_date_formats',
                    'severity': 'high',
                    'formats_found': ['%Y-%m-%d', '%m/%d/%Y']
                }
            ],
            'column_profiles': {
                'conversion': {'dtype': 'float64'},
                'revenue': {'dtype': 'float64'},
                'date': {'dtype': 'object'}
            },
            'config': {
                'column_rules': {
                    'experiment_group': {'allowed_values': ['control', 'treatment']}
                }
            }
        }
        
        # Save files
        os.makedirs('test_output', exist_ok=True)
        
        with open('test_output/quality_report.json', 'w') as f:
            json.dump(self.quality_report, f)
        
        self.test_df.to_csv('test_output/test_data.csv', index=False)
    
    def tearDown(self):
        """Clean up."""
        if os.path.exists('test_output'):
            shutil.rmtree('test_output')
    
    def test_init(self):
        """Test initialization."""
        assistant = CleaningAssistant('test_output/quality_report.json')
        self.assertIsNotNone(assistant.quality_report)
        self.assertEqual(len(assistant.quality_report['issues']), 4)
    
    def test_load_data(self):
        """Test loading data."""
        assistant = CleaningAssistant('test_output/quality_report.json')
        df = assistant.load_data('test_output/test_data.csv')
        self.assertEqual(len(df), 5)
        self.assertEqual(len(df.columns), 5)
    
    def test_generate_recommendations(self):
        """Test generating recommendations."""
        assistant = CleaningAssistant('test_output/quality_report.json')
        assistant.load_data('test_output/test_data.csv')
        recommendations = assistant.generate_recommendations()
        
        self.assertTrue(len(recommendations) > 0)
        
        # Check we have recommendations for each issue
        actions = [r['action'] for r in recommendations]
        self.assertIn('impute', actions)  # For missing values
        self.assertIn('replace_invalid', actions)  # For invalid values
        self.assertIn('cap_outliers', actions)  # For outliers
        self.assertIn('standardize_date', actions)  # For date formats
    
    def test_apply_cleaning(self):
        """Test applying cleaning."""
        assistant = CleaningAssistant('test_output/quality_report.json')
        assistant.load_data('test_output/test_data.csv')
        assistant.generate_recommendations()
        cleaned_df = assistant.apply_cleaning()
        
        # Check missing values fixed
        self.assertEqual(cleaned_df['conversion'].isna().sum(), 0)
        
        # Check invalid values fixed
        self.assertNotIn('test', cleaned_df['experiment_group'].values)
        
        # Check outliers capped
        self.assertGreaterEqual(cleaned_df['revenue'].min(), 0)
    
    def test_validation_report(self):
        """Test validation report generation."""
        assistant = CleaningAssistant('test_output/quality_report.json')
        assistant.load_data('test_output/test_data.csv')
        assistant.generate_recommendations()
        assistant.apply_cleaning()
        
        report = assistant.generate_validation_report()
        
        self.assertIn('original_shape', report)
        self.assertIn('cleaned_shape', report)
        self.assertIn('missing_values', report)
        self.assertIn('duplicates', report)
    
    def test_save_outputs(self):
        """Test saving outputs."""
        assistant = CleaningAssistant('test_output/quality_report.json')
        assistant.load_data('test_output/test_data.csv')
        assistant.generate_recommendations()
        assistant.apply_cleaning()
        
        # Save outputs
        assistant.save_cleaned_data('test_output/')
        assistant.save_cleaning_report('test_output/')
        assistant.save_audit_log('test_output/')
        
        # Check files exist
        self.assertTrue(os.path.exists('test_output/cleaned_data.csv'))
        self.assertTrue(os.path.exists('test_output/cleaning_report.json'))
        self.assertTrue(os.path.exists('test_output/audit_log.json'))
    
    def test_full_pipeline(self):
        """Test the complete pipeline."""
        assistant = CleaningAssistant('test_output/quality_report.json')
        cleaned_df = assistant.run_pipeline('test_output/test_data.csv', 'test_output/')
        
        # Check we have a cleaned DataFrame
        self.assertIsNotNone(cleaned_df)
        
        # Check files were created
        self.assertTrue(os.path.exists('test_output/cleaned_data.csv'))
        self.assertTrue(os.path.exists('test_output/cleaning_report.json'))
        self.assertTrue(os.path.exists('test_output/audit_log.json'))


if __name__ == '__main__':
    unittest.main()