# Member4/tests/test_segment_analyzer.py
import unittest
import pandas as pd
import numpy as np
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'Member4'))

from segment_analyzer import SegmentAnalyzer


class TestSegmentAnalyzer(unittest.TestCase):

    def setUp(self):
        np.random.seed(42)
        n = 400
        self.df = pd.DataFrame({
            'user_id': [f'user_{i}' for i in range(n)],
            'experiment_group': ['control'] * (n // 2) + ['treatment'] * (n // 2),
            'conversion': np.random.binomial(1, 0.12, n),
            'revenue': np.random.normal(100, 20, n).clip(0),
            'device': np.random.choice(['mobile', 'desktop', 'tablet'], n, p=[0.6, 0.3, 0.1]),
            'country': np.random.choice(['US', 'UK', 'India'], n, p=[0.5, 0.3, 0.2]),
            'age': np.random.randint(18, 70, n)
        })

    def test_detect_segment_columns(self):
        analyzer = SegmentAnalyzer(self.df)
        cols = analyzer.detect_segment_columns()
        self.assertIn('device', cols)
        self.assertIn('country', cols)
        self.assertNotIn('user_id', cols)
        self.assertNotIn('conversion', cols)

    def test_analyze_dimension(self):
        analyzer = SegmentAnalyzer(self.df)
        res = analyzer.analyze_dimension('device', metric_col='conversion', metric_type='proportion')
        self.assertEqual(res['dimension'], 'device')
        self.assertIn('segments', res)
        self.assertTrue(len(res['segments']) >= 3)
        for seg in res['segments']:
            self.assertIn('control_n', seg)
            self.assertIn('treatment_n', seg)
            self.assertIn('absolute_lift', seg)

    def test_small_sample_flagging(self):
        # Add a rare segment with very few samples
        small_df = self.df.copy()
        small_df.loc[:5, 'device'] = 'smart_tv'
        analyzer = SegmentAnalyzer(small_df, min_sample_size=30)
        res = analyzer.analyze_dimension('device')
        tv_seg = next(s for s in res['segments'] if s['segment'] == 'smart_tv')
        self.assertTrue(tv_seg['is_small_sample'])

    def test_missing_dimension_values(self):
        df_missing = self.df.copy()
        df_missing.loc[:10, 'device'] = np.nan
        analyzer = SegmentAnalyzer(df_missing)
        res = analyzer.analyze_dimension('device')
        unknown_seg = next((s for s in res['segments'] if s['segment'] == 'Unknown'), None)
        self.assertIsNotNone(unknown_seg)


if __name__ == '__main__':
    unittest.main()
