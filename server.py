# server.py
# ============================================================
# EXPERIMENTIQ - BACKEND API SERVER
# ============================================================
# Serves the full ExperimentIQ pipeline to the React frontend.
# Provides endpoints for uploading datasets, running pre-built
# demo scenarios, updating cleaning actions, and segment queries.
# ============================================================

import os
import sys
import io
import json
from pathlib import Path

# Add project root and member paths
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / 'Member1' / 'DVIIQ'))
sys.path.insert(0, str(BASE_DIR / 'member2'))
sys.path.insert(0, str(BASE_DIR / 'Member3'))
sys.path.insert(0, str(BASE_DIR / 'Member4'))

try:
    from flask import Flask, request, jsonify, send_from_directory
    from flask_cors import CORS
except ImportError:
    print("\n❌ Error: 'flask' or 'flask-cors' is not installed in your active Python interpreter.")
    print("👉 Run: python -m pip install flask flask-cors")
    print("   or:  pip install -r requirements.txt\n")
    sys.exit(1)

import pandas as pd
import numpy as np

from pipeline import ExperimentIQPipeline

app = Flask(__name__, static_folder='frontend/dist', static_url_path='')
CORS(app)


def to_serializable(obj):
    """Recursively convert NumPy and Pandas objects to native JSON-serializable types."""
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return [to_serializable(x) for x in obj]
    elif isinstance(obj, pd.Series):
        return [to_serializable(x) for x in obj.tolist()]
    elif isinstance(obj, dict):
        return {str(k): to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [to_serializable(x) for x in obj]
    return obj


DEMO_DIR = BASE_DIR / 'data' / 'demo'
RAW_DATA_PATH = BASE_DIR / 'Member1' / 'DVIIQ' / 'data' / 'raw' / 'messy_experiment_data.csv'

DEMO_SCENARIOS = {
    'scenario_a': {
        'id': 'scenario_a',
        'title': 'Scenario A: Winning Treatment',
        'expected_decision': 'LAUNCH',
        'badge': '🚀 LAUNCH',
        'description': 'Balanced 50/50 split, statistically significant conversion uplift (+40% relative, p < 0.001) with adequate power.',
        'path': DEMO_DIR / 'scenario_a_launch.csv'
    },
    'scenario_b': {
        'id': 'scenario_b',
        'title': 'Scenario B: Underpowered / Inconclusive',
        'expected_decision': 'CONTINUE EXPERIMENT',
        'badge': '⏳ CONTINUE',
        'description': 'Small sample size (n=300), modest lift not reaching significance (p=0.45). More data needed.',
        'path': DEMO_DIR / 'scenario_b_continue.csv'
    },
    'scenario_c': {
        'id': 'scenario_c',
        'title': 'Scenario C: Severe SRM & Cohort Leakage',
        'expected_decision': 'INVESTIGATE DATA',
        'badge': '⚠️ INVESTIGATE',
        'description': 'Sample Ratio Mismatch (2200 vs 800) and users appearing in both groups. Data cannot be trusted.',
        'path': DEMO_DIR / 'scenario_c_investigate.csv'
    },
    'scenario_d': {
        'id': 'scenario_d',
        'title': 'Scenario D: Harmful Variant',
        'expected_decision': 'DO NOT LAUNCH',
        'badge': '❌ DO NOT LAUNCH',
        'description': 'Statistically significant drop in conversion (-33% relative, p < 0.001). Variant is harmful.',
        'path': DEMO_DIR / 'scenario_d_do_not_launch.csv'
    },
    'messy_raw': {
        'id': 'messy_raw',
        'title': 'Original Messy Dataset',
        'expected_decision': 'CLEAN & EVALUATE',
        'badge': '🧹 MESSY DATA',
        'description': '10,100 rows containing duplicates, missing values, outliers, invalid formats, and whitespace errors.',
        'path': RAW_DATA_PATH
    }
}


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'online', 'system': 'ExperimentIQ', 'version': '2.0.0'})


@app.route('/api/demos', methods=['GET'])
def get_demos():
    """Return available pre-configured test scenarios."""
    demos_list = []
    for k, v in DEMO_SCENARIOS.items():
        exists = v['path'].exists()
        demos_list.append({
            'id': v['id'],
            'title': v['title'],
            'expected_decision': v['expected_decision'],
            'badge': v['badge'],
            'description': v['description'],
            'available': exists
        })
    return jsonify({'demos': demos_list})


@app.route('/api/run-demo', methods=['POST'])
def run_demo():
    """Execute the pipeline on a chosen demo scenario."""
    try:
        data = request.get_json() or {}
        demo_id = data.get('demo_id', 'scenario_a')

        if demo_id not in DEMO_SCENARIOS:
            return jsonify({'error': f"Unknown demo scenario '{demo_id}'"}), 400

        scenario = DEMO_SCENARIOS[demo_id]
        if not scenario['path'].exists():
            return jsonify({'error': f"Dataset for {demo_id} not found at {scenario['path']}"}), 404

        pipeline = ExperimentIQPipeline(
            alpha=data.get('alpha', 0.05),
            power_target=data.get('power_target', 0.80),
            min_segment_sample=data.get('min_segment_sample', 30)
        )

        results = pipeline.run(str(scenario['path']), auto_clean=True)
        results['scenario_info'] = {
            'id': scenario['id'],
            'title': scenario['title'],
            'description': scenario['description'],
            'expected_decision': scenario['expected_decision']
        }

        return jsonify(to_serializable(results))

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload', methods=['POST'])
def upload_and_run():
    """Ingest user-uploaded CSV or Excel file and execute the pipeline."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        filename = file.filename
        if not filename:
            return jsonify({'error': 'Empty filename'}), 400

        if filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        else:
            return jsonify({'error': 'Unsupported format. Please upload CSV or Excel.'}), 400

        group_col = request.form.get('group_column', 'experiment_group')
        user_col = request.form.get('user_column', 'user_id')
        conv_col = request.form.get('conversion_col', 'conversion')

        pipeline = ExperimentIQPipeline(
            group_column=group_col,
            user_column=user_col,
            conversion_col=conv_col,
            alpha=float(request.form.get('alpha', 0.05)),
            power_target=float(request.form.get('power_target', 0.80)),
            min_segment_sample=int(request.form.get('min_segment_sample', 30))
        )

        results = pipeline.run(df, auto_clean=True)
        results['scenario_info'] = {
            'id': 'custom_upload',
            'title': f'Uploaded: {filename}',
            'description': f'{len(df):,} uploaded rows across {len(df.columns)} columns.'
        }

        return jsonify(to_serializable(results))

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# Serve static React bundle if built
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    if path != "" and (Path(app.static_folder) / path).exists():
        return send_from_directory(app.static_folder, path)
    elif (Path(app.static_folder) / 'index.html').exists():
        return send_from_directory(app.static_folder, 'index.html')
    else:
        return jsonify({'message': 'ExperimentIQ API server running. React frontend is served on its dev port or build frontend/dist.'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 ExperimentIQ API Server listening on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
