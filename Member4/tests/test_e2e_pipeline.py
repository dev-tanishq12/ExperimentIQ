# Member4/tests/test_e2e_pipeline.py
import unittest
import os
import sys

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'Member1', 'DVIIQ'))
sys.path.insert(0, os.path.join(BASE_DIR, 'member2'))
sys.path.insert(0, os.path.join(BASE_DIR, 'Member3'))
sys.path.insert(0, os.path.join(BASE_DIR, 'Member4'))

from pipeline import ExperimentIQPipeline


class TestEndToEndPipeline(unittest.TestCase):

    def setUp(self):
        self.pipeline = ExperimentIQPipeline()
        self.demo_dir = os.path.join(BASE_DIR, 'data', 'demo')

    def test_pipeline_scenario_a_launch(self):
        scenario_a_path = os.path.join(self.demo_dir, 'scenario_a_launch.csv')
        self.assertTrue(os.path.exists(scenario_a_path), "Scenario A file missing")
        output = self.pipeline.run(scenario_a_path)

        # Check structure
        self.assertIn('decision', output)
        self.assertIn('experiment_quality', output)
        self.assertIn('segment_analysis', output)
        self.assertIn('metrics', output)

        # Scenario A should result in LAUNCH
        self.assertEqual(output['decision']['decision'], 'LAUNCH')
        self.assertGreaterEqual(output['decision']['confidence'], 0.80)

    def test_pipeline_scenario_b_continue(self):
        scenario_b_path = os.path.join(self.demo_dir, 'scenario_b_continue.csv')
        self.assertTrue(os.path.exists(scenario_b_path), "Scenario B file missing")
        output = self.pipeline.run(scenario_b_path)
        self.assertEqual(output['decision']['decision'], 'CONTINUE EXPERIMENT')

    def test_pipeline_scenario_c_investigate(self):
        scenario_c_path = os.path.join(self.demo_dir, 'scenario_c_investigate.csv')
        self.assertTrue(os.path.exists(scenario_c_path), "Scenario C file missing")
        output = self.pipeline.run(scenario_c_path)
        self.assertEqual(output['decision']['decision'], 'INVESTIGATE DATA')

    def test_pipeline_scenario_d_do_not_launch(self):
        scenario_d_path = os.path.join(self.demo_dir, 'scenario_d_do_not_launch.csv')
        self.assertTrue(os.path.exists(scenario_d_path), "Scenario D file missing")
        output = self.pipeline.run(scenario_d_path)
        self.assertEqual(output['decision']['decision'], 'DO NOT LAUNCH')


if __name__ == '__main__':
    unittest.main()
