# Member2/cleaning_assistant.py

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import warnings
warnings.filterwarnings('ignore')

class CleaningAssistant:
    """
    Intelligent Cleaning Assistant - Member 2
    
    Consumes Member 1's quality_report.json and generates:
    1. Cleaning recommendations
    2. Cleaned dataset
    3. Cleaning report & audit log
    
    Pipeline: quality_report.json → Cleaning → clean_dataset.csv
    """
    
    def __init__(self, quality_report_path: str):
        """
        Initialize with Member 1's quality report.
        
        Args:
            quality_report_path: Path to quality_report.json from Member 1
        """
        print("🔧 Loading quality report from Member 1...")
        with open(quality_report_path, 'r') as f:
            self.quality_report = json.load(f)
        
        self.df = None
        self.cleaned_df = None
        self.cleaning_actions = []
        self.audit_log = []
        self.original_shape = None
        self.user_decisions = []  # Track user decisions
        
        print(f"   ✅ Loaded {len(self.quality_report.get('issues', []))} issues to fix")
    
    def load_data(self, data_path: str) -> pd.DataFrame:
        """
        Load the raw dataset.
        
        Args:
            data_path: Path to CSV or Excel file
            
        Returns:
            pandas DataFrame
        """
        print(f"📂 Loading data from: {data_path}")
        
        if data_path.endswith('.csv'):
            self.df = pd.read_csv(data_path)
        elif data_path.endswith(('.xlsx', '.xls')):
            self.df = pd.read_excel(data_path)
        else:
            raise ValueError(f"Unsupported file format: {data_path}")
        
        self.cleaned_df = self.df.copy()
        self.original_shape = self.df.shape
        
        print(f"   ✅ Loaded {len(self.df)} rows, {len(self.df.columns)} columns")
        return self.df
    
    def generate_recommendations(self) -> List[Dict]:
        """
        Generate cleaning recommendations based on Member 1's quality report.
        
        Returns:
            List of cleaning recommendations
        """
        print("💡 Generating cleaning recommendations...")
        self.cleaning_actions = []
        
        for issue in self.quality_report.get('issues', []):
            recommendation = self._create_recommendation(issue)
            if recommendation:
                self.cleaning_actions.append(recommendation)
                
                # Log to audit
                self.audit_log.append({
                    'issue_type': issue.get('type'),
                    'column': issue.get('column'),
                    'severity': issue.get('severity', 'low'),
                    'recommended_action': recommendation.get('action'),
                    'confidence': recommendation.get('confidence', 0),
                    'status': 'pending_review',  # Changed from 'pending'
                    'timestamp': datetime.now().isoformat(),
                    'explanation': recommendation.get('explanation'),
                    'parameters': recommendation.get('parameters', {})
                })
        
        print(f"   ✅ Generated {len(self.cleaning_actions)} cleaning recommendations")
        return self.cleaning_actions
    
    def _create_recommendation(self, issue: Dict) -> Dict:
        """
        Create a cleaning recommendation for a specific issue.
        """
        issue_type = issue.get('type')
        column = issue.get('column')
        severity = issue.get('severity', 'low')
        
        recommendation = {
            'issue_type': issue_type,
            'column': column,
            'severity': severity,
            'action': None,
            'confidence': 0.0,
            'explanation': '',
            'parameters': {}
        }
        
        # ===== MISSING VALUES =====
        if issue_type == 'missing_values':
            recommendation['action'] = 'impute'
            recommendation['confidence'] = 0.85
            recommendation['explanation'] = f"Column '{column}' has {issue.get('count')} missing values ({issue.get('pct')}%)"
            
            # Determine imputation strategy
            col_profile = self.quality_report.get('column_profiles', {}).get(column, {})
            dtype = col_profile.get('dtype', 'object')
            
            if 'float' in dtype or 'int' in dtype:
                recommendation['parameters'] = {'method': 'median'}
                recommendation['explanation'] += " → Impute with median"
            else:
                recommendation['parameters'] = {'method': 'mode'}
                recommendation['explanation'] += " → Impute with mode"
        
        # ===== DUPLICATE ROWS =====
        elif issue_type == 'duplicate_rows':
            recommendation['action'] = 'drop_duplicates'
            recommendation['confidence'] = 0.95
            recommendation['explanation'] = f"Found {issue.get('count')} duplicate rows ({issue.get('pct')}%) → Dropping duplicates"
            recommendation['parameters'] = {'keep': 'first'}
        
        # ===== DUPLICATE USERS (CRITICAL) =====
        elif issue_type == 'duplicate_users_across_groups':
            recommendation['action'] = 'fix_duplicate_users'
            recommendation['confidence'] = 0.60
            recommendation['explanation'] = "CRITICAL: Users in multiple groups. Fix by keeping most common group."
            recommendation['parameters'] = {'method': 'keep_most_common'}
        
        # ===== INVALID VALUES =====
        elif issue_type == 'invalid_values':
            recommendation['action'] = 'replace_invalid'
            recommendation['confidence'] = 0.75
            invalid_vals = issue.get('invalid_values', [])
            recommendation['explanation'] = f"Found invalid values in '{column}': {invalid_vals[:3]}"
            
            # Try to find replacement from config
            column_rules = self.quality_report.get('config', {}).get('column_rules', {})
            allowed = column_rules.get(column, {}).get('allowed_values', [])
            
            if allowed:
                recommendation['parameters'] = {
                    'invalid_values': invalid_vals,
                    'replace_with': allowed[0]
                }
                recommendation['explanation'] += f" → Replace with '{allowed[0]}'"
            else:
                recommendation['parameters'] = {
                    'invalid_values': invalid_vals,
                    'replace_with': None
                }
                recommendation['explanation'] += " → No replacement found, flagging for review"
                recommendation['confidence'] = 0.5
        
        # ===== OUTLIERS =====
        elif issue_type == 'outliers':
            recommendation['action'] = 'cap_outliers'
            recommendation['confidence'] = 0.70
            bounds = issue.get('bounds', {})
            lower = bounds.get('lower')
            upper = bounds.get('upper')
            
            recommendation['explanation'] = f"Found {issue.get('count')} outliers in '{column}'"
            recommendation['parameters'] = {
                'method': 'winsorize',
                'lower_bound': lower,
                'upper_bound': upper
            }
            if lower and upper:
                recommendation['explanation'] += f" → Capping between {lower:.2f} and {upper:.2f}"
        
        # ===== DATE FORMAT INCONSISTENCY =====
        elif issue_type == 'inconsistent_date_formats':
            recommendation['action'] = 'standardize_date'
            recommendation['confidence'] = 0.90
            formats = issue.get('formats_found', [])
            recommendation['explanation'] = f"Multiple date formats found: {formats} → Standardizing"
            recommendation['parameters'] = {
                'target_format': '%Y-%m-%d',
                'current_formats': formats
            }
        
        # ===== CASE INCONSISTENCY =====
        elif issue_type == 'case_inconsistency':
            recommendation['action'] = 'standardize_case'
            recommendation['confidence'] = 0.85
            recommendation['explanation'] = f"Column '{column}' has inconsistent casing → Converting to lowercase"
            recommendation['parameters'] = {'case': 'lower'}
        
        # ===== WHITESPACE ISSUES =====
        elif issue_type == 'whitespace_issues':
            recommendation['action'] = 'strip_whitespace'
            recommendation['confidence'] = 0.95
            recommendation['explanation'] = f"Found {issue.get('count')} values with whitespace → Stripping"
            recommendation['parameters'] = {'strip': True}
        
        # ===== MIXED TYPES =====
        elif issue_type == 'mixed_types':
            recommendation['action'] = 'convert_type'
            recommendation['confidence'] = 0.60
            recommendation['explanation'] = f"Column '{column}' has mixed types → Converting to numeric"
            recommendation['parameters'] = {'target_type': 'numeric', 'errors': 'coerce'}
        
        # ===== EMPTY COLUMN =====
        elif issue_type == 'empty_column':
            recommendation['action'] = 'drop_column'
            recommendation['confidence'] = 0.95
            recommendation['explanation'] = f"Column '{column}' is completely empty → Dropping"
            recommendation['parameters'] = {'drop': True}
        
        else:
            recommendation['action'] = 'no_action'
            recommendation['confidence'] = 0.0
            recommendation['explanation'] = f"Issue type '{issue_type}' not recognized → Manual review"
        
        return recommendation
    
    def interactive_review(self) -> pd.DataFrame:
        """
        Interactive review of ALL cleaning actions.
        User can approve, reject, or modify each action.
        
        Returns:
            Cleaned DataFrame
        """
        print("\n" + "="*70)
        print("🔍 INTERACTIVE CLEANING REVIEW")
        print("="*70)
        print(f"📋 Total actions to review: {len(self.cleaning_actions)}")
        print("\nYou will review each cleaning action one by one.")
        print("Options:")
        print("  [Y] Yes - Apply this cleaning action")
        print("  [N] No  - Skip this action")
        print("  [M] Modify - Change parameters before applying")
        print("  [Q] Quit - Stop and save current progress")
        print("="*70)
        
        for idx, action in enumerate(self.cleaning_actions, 1):
            print(f"\n{'='*70}")
            print(f"📌 Action {idx}/{len(self.cleaning_actions)}")
            print(f"{'='*70}")
            
            # Display action details
            print(f"📊 Issue Type: {action.get('issue_type')}")
            print(f"📁 Column: {action.get('column', 'N/A')}")
            print(f"⚠️ Severity: {action.get('severity', 'low')}")
            print(f"💡 Action: {action.get('action')}")
            print(f"📝 Explanation: {action.get('explanation')}")
            print(f"🎯 Confidence: {action.get('confidence', 0) * 100:.0f}%")
            print(f"⚙️ Parameters: {action.get('parameters', {})}")
            
            # Show sample data affected
            column = action.get('column')
            if column and column in self.cleaned_df.columns:
                print(f"\n📊 Sample affected data (first 5 rows):")
                sample = self.cleaned_df[column].head(5).tolist()
                for i, val in enumerate(sample, 1):
                    print(f"   Row {i}: {val}")
            
            # Get user decision
            while True:
                choice = input("\nApply this action? (Y/N/M/Q): ").strip().upper()
                
                if choice == 'Y':
                    # Apply the action
                    self._apply_single_action(action)
                    self._update_audit(action, 'approved')
                    self.user_decisions.append({
                        'action': action,
                        'decision': 'approved',
                        'timestamp': datetime.now().isoformat()
                    })
                    print("✅ Action applied!")
                    break
                
                elif choice == 'N':
                    self._update_audit(action, 'rejected')
                    self.user_decisions.append({
                        'action': action,
                        'decision': 'rejected',
                        'timestamp': datetime.now().isoformat()
                    })
                    print("❌ Action skipped!")
                    break
                
                elif choice == 'M':
                    # Modify parameters
                    print(f"\nCurrent parameters: {action.get('parameters', {})}")
                    param_input = input("Enter new parameters (as dict, e.g., {'method': 'mean'}): ")
                    try:
                        if param_input.strip():
                            new_params = eval(param_input)
                            action['parameters'] = new_params
                            print(f"✅ Parameters updated: {new_params}")
                        # Apply with new parameters
                        self._apply_single_action(action)
                        self._update_audit(action, 'approved_modified')
                        self.user_decisions.append({
                            'action': action,
                            'decision': 'approved_modified',
                            'modified_params': action.get('parameters'),
                            'timestamp': datetime.now().isoformat()
                        })
                        print("✅ Action applied with modified parameters!")
                        break
                    except Exception as e:
                        print(f"❌ Invalid parameters: {e}. Try again.")
                
                elif choice == 'Q':
                    print("⏹️ Quitting review. Saving progress...")
                    return self.cleaned_df
                
                else:
                    print("❌ Invalid choice. Please enter Y, N, M, or Q.")
        
        print("\n" + "="*70)
        print("✅ REVIEW COMPLETE")
        print("="*70)
        
        # Summary
        approved = len([d for d in self.user_decisions if d.get('decision') in ['approved', 'approved_modified']])
        rejected = len([d for d in self.user_decisions if d.get('decision') == 'rejected'])
        print(f"✅ Approved: {approved}")
        print(f"❌ Rejected: {rejected}")
        print("="*70)
        
        return self.cleaned_df
    
    def _apply_single_action(self, action: Dict):
        """Apply a single cleaning action."""
        action_type = action.get('action')
        column = action.get('column')
        
        if action_type == 'impute':
            self._impute_missing(column, action.get('parameters', {}))
        elif action_type == 'drop_duplicates':
            self._drop_duplicates(action.get('parameters', {}))
        elif action_type == 'replace_invalid':
            self._replace_invalid(column, action.get('parameters', {}))
        elif action_type == 'cap_outliers':
            self._cap_outliers(column, action.get('parameters', {}))
        elif action_type == 'standardize_date':
            self._standardize_date(column, action.get('parameters', {}))
        elif action_type == 'standardize_case':
            self._standardize_case(column, action.get('parameters', {}))
        elif action_type == 'strip_whitespace':
            self._strip_whitespace(column)
        elif action_type == 'convert_type':
            self._convert_type(column, action.get('parameters', {}))
        elif action_type == 'drop_column':
            self._drop_column(column)
        elif action_type == 'fix_duplicate_users':
            self._fix_duplicate_users()
        elif action_type == 'no_action':
            print(f"   ⚠️ No action taken for: {action.get('explanation')}")
    
    def _fix_duplicate_users(self):
        """Fix duplicate users across groups."""
        if 'user_id' in self.cleaned_df.columns and 'experiment_group' in self.cleaned_df.columns:
            print("   🔧 Fixing duplicate users across groups...")
            
            df_clean = self.cleaned_df[['user_id', 'experiment_group']].copy()
            df_clean['experiment_group'] = df_clean['experiment_group'].astype(str).str.lower().str.strip()
            
            users_in_multiple = df_clean.groupby('user_id')['experiment_group'].nunique()
            users_multiple = users_in_multiple[users_in_multiple > 1].index.tolist()
            
            fixed_count = 0
            for user in users_multiple:
                user_rows = self.cleaned_df[self.cleaned_df['user_id'] == user]
                most_common_group = user_rows['experiment_group'].mode()[0]
                mask = (self.cleaned_df['user_id'] == user) & (self.cleaned_df['experiment_group'] != most_common_group)
                self.cleaned_df = self.cleaned_df[~mask]
                fixed_count += 1
            
            print(f"   ✅ Fixed {fixed_count} users")
    
    def _impute_missing(self, column: str, params: Dict):
        """Impute missing values."""
        method = params.get('method', 'median')
        
        if method == 'median' and pd.api.types.is_numeric_dtype(self.cleaned_df[column]):
            value = self.cleaned_df[column].median()
        elif method == 'mean' and pd.api.types.is_numeric_dtype(self.cleaned_df[column]):
            value = self.cleaned_df[column].mean()
        elif method == 'mode':
            value = self.cleaned_df[column].mode()[0] if len(self.cleaned_df[column].mode()) > 0 else None
        else:
            value = params.get('fallback', 0)
        
        if value is not None:
            self.cleaned_df[column] = self.cleaned_df[column].fillna(value)
    
    def _drop_duplicates(self, params: Dict):
        """Drop duplicate rows."""
        keep = params.get('keep', 'first')
        self.cleaned_df.drop_duplicates(keep=keep, inplace=True)
    
    def _replace_invalid(self, column: str, params: Dict):
        """Replace invalid values."""
        invalid_vals = params.get('invalid_values', [])
        replace_with = params.get('replace_with')
        
        if replace_with is not None:
            self.cleaned_df[column] = self.cleaned_df[column].replace(invalid_vals, replace_with)
    
    def _cap_outliers(self, column: str, params: Dict):
        """Cap outliers using winsorization."""
        lower = params.get('lower_bound')
        upper = params.get('upper_bound')
        
        if lower is not None:
            self.cleaned_df[column] = self.cleaned_df[column].clip(lower=lower)
        if upper is not None:
            self.cleaned_df[column] = self.cleaned_df[column].clip(upper=upper)
    
    def _standardize_date(self, column: str, params: Dict):
        """Standardize date format."""
        self.cleaned_df[column] = pd.to_datetime(self.cleaned_df[column], errors='coerce')
        target_format = params.get('target_format', '%Y-%m-%d')
        self.cleaned_df[column] = self.cleaned_df[column].dt.strftime(target_format)
    
    def _standardize_case(self, column: str, params: Dict):
        """Standardize case."""
        case = params.get('case', 'lower')
        if case == 'lower':
            self.cleaned_df[column] = self.cleaned_df[column].astype(str).str.lower()
        elif case == 'upper':
            self.cleaned_df[column] = self.cleaned_df[column].astype(str).str.upper()
    
    def _strip_whitespace(self, column: str):
        """Strip leading/trailing whitespace."""
        self.cleaned_df[column] = self.cleaned_df[column].astype(str).str.strip()
    
    def _convert_type(self, column: str, params: Dict):
        """Convert column type."""
        target = params.get('target_type', 'numeric')
        if target == 'numeric':
            self.cleaned_df[column] = pd.to_numeric(self.cleaned_df[column], errors='coerce')
    
    def _drop_column(self, column: str):
        """Drop a column."""
        if column in self.cleaned_df.columns:
            self.cleaned_df.drop(columns=[column], inplace=True)
    
    def _update_audit(self, action: Dict, status: str):
        """Update audit log."""
        for log in self.audit_log:
            if (log.get('issue_type') == action.get('issue_type') and 
                log.get('column') == action.get('column')):
                log['status'] = status
                log['applied_at'] = datetime.now().isoformat()
                break
    
    def generate_validation_report(self) -> Dict:
        """
        Compare original vs cleaned dataset.
        
        Returns:
            Validation report
        """
        if self.df is None or self.cleaned_df is None:
            return {'error': 'No data to validate'}
        
        print("📊 Generating validation report...")
        
        original_missing = self.df.isna().sum().sum()
        cleaned_missing = self.cleaned_df.isna().sum().sum()
        
        original_duplicates = self.df.duplicated().sum()
        cleaned_duplicates = self.cleaned_df.duplicated().sum()
        
        report = {
            'original_shape': {
                'rows': self.df.shape[0],
                'columns': self.df.shape[1]
            },
            'cleaned_shape': {
                'rows': self.cleaned_df.shape[0],
                'columns': self.cleaned_df.shape[1]
            },
            'missing_values': {
                'original': int(original_missing),
                'cleaned': int(cleaned_missing),
                'fixed': int(original_missing - cleaned_missing)
            },
            'duplicates': {
                'original': int(original_duplicates),
                'cleaned': int(cleaned_duplicates),
                'removed': int(original_duplicates - cleaned_duplicates)
            },
            'columns_dropped': list(set(self.df.columns) - set(self.cleaned_df.columns)),
            'columns_added': list(set(self.cleaned_df.columns) - set(self.df.columns)),
            'user_decisions': self.user_decisions
        }
        
        return report
    
    def generate_cleaning_report(self) -> Dict:
        """
        Generate complete cleaning report for Member 3.
        
        Returns:
            Complete cleaning report
        """
        print("📝 Generating cleaning report...")
        
        validation = self.generate_validation_report()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'source_quality_report': self.quality_report.get('report_timestamp', 'unknown'),
            'actions_summary': {
                'total_actions': len(self.cleaning_actions),
                'approved': len([a for a in self.audit_log if a.get('status') in ['approved', 'approved_modified']]),
                'rejected': len([a for a in self.audit_log if a.get('status') == 'rejected']),
                'pending': len([a for a in self.audit_log if a.get('status') == 'pending_review'])
            },
            'user_decisions': self.user_decisions,
            'cleaning_actions': self.cleaning_actions,
            'audit_log': self.audit_log,
            'validation': validation,
            'cleaning_status': 'complete' if all(a.get('status') != 'pending_review' for a in self.audit_log) else 'partial'
        }
    
    def save_cleaned_data(self, output_dir: str = 'sample_output/'):
        """Save cleaned dataset."""
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, 'cleaned_data.csv')
        self.cleaned_df.to_csv(output_path, index=False)
        print(f"💾 Cleaned data saved to: {output_path}")
        return output_path
    
    def save_cleaning_report(self, output_dir: str = 'sample_output/'):
        """Save cleaning report as JSON."""
        os.makedirs(output_dir, exist_ok=True)
        
        report = self.generate_cleaning_report()
        
        output_path = os.path.join(output_dir, 'cleaning_report.json')
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"💾 Cleaning report saved to: {output_path}")
        return output_path
    
    def save_audit_log(self, output_dir: str = 'sample_output/'):
        """Save audit log as JSON."""
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, 'audit_log.json')
        with open(output_path, 'w') as f:
            json.dump(self.audit_log, f, indent=2)
        print(f"💾 Audit log saved to: {output_path}")
        return output_path
    
    def run_pipeline(self, data_path: str, output_dir: str = 'sample_output/', 
                     interactive: bool = True):
        """
        Run the complete cleaning pipeline.
        
        Args:
            data_path: Path to raw data
            output_dir: Output directory for cleaned data and reports
            interactive: If True, prompt user for each action
            
        Returns:
            Cleaned DataFrame
        """
        print("="*70)
        print("🧹 Member 2 - Cleaning Pipeline")
        print("="*70)
        
        # Step 1: Load data
        self.load_data(data_path)
        
        # Step 2: Generate recommendations
        self.generate_recommendations()
        
        # Step 3: Interactive review (if enabled)
        if interactive:
            self.interactive_review()
        else:
            # Auto-apply all actions
            print("🤖 Auto-applying all cleaning actions...")
            for action in self.cleaning_actions:
                self._apply_single_action(action)
                self._update_audit(action, 'auto_applied')
        
        # Step 4: Save outputs
        self.save_cleaned_data(output_dir)
        self.save_cleaning_report(output_dir)
        self.save_audit_log(output_dir)
        
        # Print summary
        print("\n" + "="*70)
        print("📊 CLEANING SUMMARY")
        print("="*70)
        print(f"   Original: {self.original_shape[0]} rows, {self.original_shape[1]} cols")
        print(f"   Cleaned:  {self.cleaned_df.shape[0]} rows, {self.cleaned_df.shape[1]} cols")
        
        approved = len([a for a in self.audit_log if a.get('status') in ['approved', 'approved_modified', 'auto_applied']])
        rejected = len([a for a in self.audit_log if a.get('status') == 'rejected'])
        print(f"   ✅ Approved: {approved}")
        print(f"   ❌ Rejected: {rejected}")
        print("="*70)
        
        return self.cleaned_df


# ===== MAIN - Run the pipeline =====
if __name__ == "__main__":
    import sys
    
    # Paths
    QUALITY_REPORT_PATH = '../Member1/DVIIQ/quality_report.json'  
    RAW_DATA_PATH = '../Member1/DVIIQ/data/raw/messy_experiment_data.csv'  
    OUTPUT_DIR = 'sample_output/'
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Check if files exist
    if not os.path.exists(QUALITY_REPORT_PATH):
        print(f"❌ Error: Quality report not found at {QUALITY_REPORT_PATH}")
        sys.exit(1)
    
    if not os.path.exists(RAW_DATA_PATH):
        print(f"❌ Error: Data file not found at {RAW_DATA_PATH}")
        sys.exit(1)
    
    # Ask user if they want interactive or auto mode
    print("\n" + "="*70)
    print("🧹 Member 2 - Cleaning Assistant")
    print("="*70)
    print("\nChoose cleaning mode:")
    print("  [1] Interactive - Review each action (Recommended)")
    print("  [2] Auto - Apply all actions without review")
    
    mode = input("\nEnter choice (1/2): ").strip()
    interactive = mode != '2'
    
    # Run the cleaning pipeline
    assistant = CleaningAssistant(QUALITY_REPORT_PATH)
    cleaned_df = assistant.run_pipeline(RAW_DATA_PATH, OUTPUT_DIR, interactive=interactive)
    
    # Show sample of cleaned data
    print("\n🔍 Sample of cleaned data (first 5 rows):")
    print(cleaned_df.head())