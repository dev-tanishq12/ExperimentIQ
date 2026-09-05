# quality_profiler.py

import pandas as pd
import numpy as np
import json
from datetime import datetime
from typing import Dict, Any, Optional
import warnings
warnings.filterwarnings('ignore')

class DataQualityProfiler:
    """Data Quality Profiler - Finds EVERY issue in experiment data."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._get_default_config()
        self.issues = []
        self.profile = {}
        self.df = None
    
    def _get_default_config(self) -> Dict:
        return {
            'column_rules': {
                'user_id': {'required': True, 'type': 'string'},
                'experiment_group': {
                    'required': True,
                    'allowed_values': ['control', 'treatment'],
                    'case_sensitive': False
                },
                'conversion': {
                    'required': True,
                    'min': 0,
                    'max': 1,
                    'allowed_values': [0, 1]
                },
                'revenue': {'required': False, 'min': 0, 'type': 'numeric'},
                'device': {
                    'required': False,
                    'allowed_values': ['mobile', 'desktop', 'tablet'],
                    'case_sensitive': False
                },
                'country': {
                    'required': False,
                    'allowed_values': ['US', 'UK', 'India'],
                    'case_sensitive': False
                },
                'age': {'required': False, 'min': 18, 'max': 100},
                'session_duration': {'required': False, 'min': 1}
            },
            'outlier_method': 'IQR',
            'outlier_threshold': 1.5,
            'zscore_threshold': 3,
            'date_columns': ['date'],
            'date_formats': ['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y'],
            'id_columns': ['user_id']
        }
    
    def load_data(self, filepath: str) -> pd.DataFrame:
        """Load CSV or Excel file."""
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filepath.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(filepath)
        else:
            raise ValueError(f"Unsupported file format: {filepath}")
        
        self.df = df
        return df
    
    def profile_data(self, df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """Complete profiling - find EVERYTHING wrong."""
        if df is not None:
            self.df = df
        
        if self.df is None:
            raise ValueError("No data loaded.")
        
        print("🔍 Profiling data...")
        self.issues = []
        
        self._profile_file_info()
        self._profile_columns()
        self._check_missing_values()
        self._check_duplicate_rows()
        self._check_duplicate_users()
        self._check_invalid_values()
        self._check_outliers()
        self._check_format_inconsistencies()
        self._check_whitespace_issues()
        self._check_mixed_types()
        self._check_empty_columns()
        
        report = {
            'file_info': self.profile.get('file_info', {}),
            'column_profiles': self.profile.get('column_profiles', {}),
            'issues': self.issues,
            'summary': self._generate_summary(),
            'quality_score': self._calculate_quality_score(),
            'report_timestamp': datetime.now().isoformat()
        }
        
        print(f"✅ Found {len(self.issues)} issues")
        return report
    
    def _profile_file_info(self):
        """Basic file information."""
        self.profile['file_info'] = {
            'rows': len(self.df),
            'columns': len(self.df.columns),
            'column_names': self.df.columns.tolist(),
            'memory_usage_mb': round(self.df.memory_usage(deep=True).sum() / (1024*1024), 2)
        }
    
    def _profile_columns(self):
        """Detailed column profiling."""
        self.profile['column_profiles'] = {}
        for col in self.df.columns:
            series = self.df[col]
            profile = {
                'dtype': str(series.dtype),
                'null_count': int(series.isna().sum()),
                'null_pct': float(round(series.isna().sum() / len(series) * 100, 2)),
                'unique_count': int(series.nunique()),
                'unique_pct': float(round(series.nunique() / len(series) * 100, 2)),
                'sample_values': series.dropna().head(5).tolist()
            }
            
            if pd.api.types.is_numeric_dtype(series):
                profile.update({
                    'min': float(series.min()) if not series.isna().all() else None,
                    'max': float(series.max()) if not series.isna().all() else None,
                    'mean': float(series.mean()) if not series.isna().all() else None,
                    'median': float(series.median()) if not series.isna().all() else None,
                    'std': float(series.std()) if not series.isna().all() else None,
                    'q1': float(series.quantile(0.25)) if not series.isna().all() else None,
                    'q3': float(series.quantile(0.75)) if not series.isna().all() else None
                })
            
            if series.dtype == 'object':
                profile['top_values'] = series.value_counts().head(5).to_dict()
            
            self.profile['column_profiles'][col] = profile
    
    def _check_missing_values(self):
        """Find missing values."""
        for col in self.df.columns:
            missing = self.df[col].isna().sum()
            if missing > 0:
                pct = missing / len(self.df) * 100
                severity = 'high' if pct > 10 else 'medium' if pct > 5 else 'low'
                self.issues.append({
                    'column': col,
                    'type': 'missing_values',
                    'severity': severity,
                    'count': int(missing),
                    'pct': float(round(pct, 2)),
                    'description': f"{missing} missing values ({pct:.1f}%)",
                    'suggestion': 'Impute with median/mode or drop rows if >10%'
                })
    
    def _check_duplicate_rows(self):
        """Find exact duplicate rows."""
        duplicates = self.df.duplicated().sum()
        if duplicates > 0:
            pct = duplicates / len(self.df) * 100
            severity = 'high' if pct > 2 else 'medium'
            self.issues.append({
                'type': 'duplicate_rows',
                'severity': severity,
                'count': int(duplicates),
                'pct': float(round(pct, 2)),
                'description': f"{duplicates} exact duplicate rows ({pct:.1f}%)",
                'suggestion': 'Drop duplicate rows'
            })
    
    def _check_duplicate_users(self):
        """Check for same user in multiple groups."""
        if 'user_id' in self.df.columns and 'experiment_group' in self.df.columns:
            # Create a clean copy with standardized groups
            df_clean = self.df[['user_id', 'experiment_group']].copy()
            
            # Convert to string, strip whitespace, lowercase
            df_clean['experiment_group'] = (
                df_clean['experiment_group']
                .astype(str)
                .str.strip()
                .str.lower()
            )
            
            # Count unique groups per user
            users_in_multiple = df_clean.groupby('user_id')['experiment_group'].nunique()
            users_multiple = users_in_multiple[users_in_multiple > 1]
            
            if len(users_multiple) > 0:
                sample_users = users_multiple.head(5).index.tolist()
                self.issues.append({
                    'type': 'duplicate_users_across_groups',
                    'severity': 'critical',
                    'count': int(len(users_multiple)),
                    'sample_users': sample_users,
                    'description': f"{len(users_multiple)} users appear in multiple experiment groups",
                    'suggestion': 'CRITICAL: Experiment design invalid. Users must be in ONLY one group.'
                })
    
    def _check_invalid_values(self):
        """Find values outside allowed ranges/categories."""
        for col, rules in self.config.get('column_rules', {}).items():
            if col not in self.df.columns:
                continue
            
            invalid = []
            
            if 'allowed_values' in rules:
                allowed = rules['allowed_values']
                
                if rules.get('case_sensitive', True):
                    # Case sensitive: exact match required
                    mask = ~self.df[col].isin(allowed)
                else:
                    # Case insensitive: check if lowercase version is valid
                    mask = ~self.df[col].astype(str).str.lower().isin([str(v).lower() for v in allowed])
                
                invalid_rows = self.df[col][mask & self.df[col].notna()]
                if len(invalid_rows) > 0:
                    # Get UNIQUE invalid values (original format)
                    invalid_vals = invalid_rows.unique().tolist()
                    invalid.extend(invalid_vals)
            
            # Check numeric ranges
            if 'min' in rules and pd.api.types.is_numeric_dtype(self.df[col]):
                invalid_vals = self.df[col][self.df[col] < rules['min']].unique().tolist()
                invalid.extend(invalid_vals)
            
            if 'max' in rules and pd.api.types.is_numeric_dtype(self.df[col]):
                invalid_vals = self.df[col][self.df[col] > rules['max']].unique().tolist()
                invalid.extend(invalid_vals)
            
            if invalid:
                unique_invalid = list(set(invalid))
                # Filter out nan values
                unique_invalid = [x for x in unique_invalid if pd.notna(x)]
                if unique_invalid:
                    self.issues.append({
                        'column': col,
                        'type': 'invalid_values',
                        'severity': 'high' if len(unique_invalid) > 3 else 'medium',
                        'invalid_values': unique_invalid[:10],
                        'count': len(unique_invalid),
                        'description': f"Found {len(unique_invalid)} invalid values in column '{col}'",
                        'suggestion': f"Replace invalid values with valid options: {rules.get('allowed_values', [])}"
                    })
    
    def _check_outliers(self):
        """Detect outliers using IQR method with Z-score fallback."""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            series = self.df[col].dropna()
            if len(series) < 10 or series.nunique() <= 2 or col.lower() in ['conversion', 'converted']:
                continue
            
            # Try IQR first
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            if IQR == 0:
                continue
            
            threshold = self.config.get('outlier_threshold', 1.5)
            
            # For small datasets, use more sensitive threshold
            if len(series) < 50:
                threshold = 1.0
            
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            
            outliers_iqr = series[(series < lower_bound) | (series > upper_bound)]
            
            # If IQR didn't find outliers but dataset has extreme values, try Z-score
            if len(outliers_iqr) == 0 and len(series) > 5:
                # Try Z-score method
                z_scores = np.abs((series - series.mean()) / series.std())
                z_threshold = self.config.get('zscore_threshold', 3)
                outliers_zscore = series[z_scores > z_threshold]
                
                if len(outliers_zscore) > 0:
                    outliers = outliers_zscore
                    method = 'Z-score'
                    threshold_used = z_threshold
                    bounds = {'lower': float(series.mean() - z_threshold * series.std()), 
                              'upper': float(series.mean() + z_threshold * series.std())}
                else:
                    outliers = pd.Series()
                    method = 'IQR'
                    threshold_used = threshold
                    bounds = {'lower': float(lower_bound), 'upper': float(upper_bound)}
            else:
                outliers = outliers_iqr
                method = 'IQR'
                threshold_used = threshold
                bounds = {'lower': float(lower_bound), 'upper': float(upper_bound)}
            
            if len(outliers) > 0:
                pct = len(outliers) / len(series) * 100
                self.issues.append({
                    'column': col,
                    'type': 'outliers',
                    'severity': 'high' if pct > 2 else 'medium',
                    'method': method,
                    'threshold': float(threshold_used),
                    'count': int(len(outliers)),
                    'pct': float(round(pct, 2)),
                    'bounds': bounds,
                    'outlier_values': outliers.head(5).tolist(),
                    'description': f"{len(outliers)} outliers detected using {method} ({pct:.1f}%)",
                    'suggestion': 'Investigate outliers. Consider winsorizing or capping.'
                })
    
    def _check_format_inconsistencies(self):
        """Check for mixed date formats and categorical inconsistencies."""
        # Date format inconsistencies
        for col in self.config.get('date_columns', []):
            if col not in self.df.columns:
                continue
            
            formats_found = []
            for fmt in self.config.get('date_formats', []):
                parsed = pd.to_datetime(self.df[col], format=fmt, errors='coerce')
                if parsed.notna().sum() > 0:
                    formats_found.append(fmt)
            
            if len(formats_found) > 1:
                self.issues.append({
                    'column': col,
                    'type': 'inconsistent_date_formats',
                    'severity': 'high',
                    'formats_found': formats_found,
                    'description': f"Multiple date formats detected: {', '.join(formats_found)}",
                    'suggestion': f"Standardize to a single date format (e.g., {formats_found[0]})"
                })
        
        # Category inconsistency (case variations)
        try:
            categorical_cols = self.df.select_dtypes(include=['object', 'string']).columns
        except:
            categorical_cols = self.df.select_dtypes(include=['object']).columns
            
        for col in categorical_cols:
            if col in ['user_id']:
                continue
            
            values = self.df[col].dropna().astype(str)
            if len(values) < 10:
                continue
            
            lower_values = values.str.lower()
            if len(lower_values.unique()) < len(values.unique()):
                self.issues.append({
                    'column': col,
                    'type': 'case_inconsistency',
                    'severity': 'low',
                    'description': f"Column '{col}' has inconsistent casing",
                    'suggestion': 'Standardize to lowercase or title case'
                })
    
    def _check_whitespace_issues(self):
        """Find leading/trailing whitespace."""
        try:
            object_cols = self.df.select_dtypes(include=['object', 'string']).columns
        except:
            object_cols = self.df.select_dtypes(include=['object']).columns
            
        for col in object_cols:
            has_whitespace = self.df[col].astype(str).str.match(r'^\s+|\s+$', na=False)
            count = has_whitespace.sum()
            if count > 0:
                self.issues.append({
                    'column': col,
                    'type': 'whitespace_issues',
                    'severity': 'low',
                    'count': int(count),
                    'description': f"{count} values have leading/trailing whitespace",
                    'suggestion': 'Strip whitespace using .str.strip()'
                })
    
    def _check_mixed_types(self):
        """Check for mixed types in columns."""
        for col in self.df.columns:
            if self.df[col].dtype == 'object':
                numeric = pd.to_numeric(self.df[col], errors='coerce')
                if numeric.notna().sum() > 0 and numeric.isna().sum() > 0:
                    numeric_pct = numeric.notna().sum() / len(self.df) * 100
                    if 20 < numeric_pct < 80:
                        self.issues.append({
                            'column': col,
                            'type': 'mixed_types',
                            'severity': 'medium',
                            'description': f"Column '{col}' has mixed text and numeric values",
                            'suggestion': 'Convert to numeric or extract clean numeric values'
                        })
    
    def _check_empty_columns(self):
        """Find completely empty columns."""
        for col in self.df.columns:
            if self.df[col].isna().all():
                self.issues.append({
                    'column': col,
                    'type': 'empty_column',
                    'severity': 'low',
                    'description': f"Column '{col}' is completely empty",
                    'suggestion': 'Drop this column'
                })
    
    def _generate_summary(self) -> Dict:
        """Generate summary statistics of all issues."""
        summary = {
            'total_issues': len(self.issues),
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'by_type': {}
        }
        
        for issue in self.issues:
            severity = issue.get('severity', 'low')
            summary[severity] = summary.get(severity, 0) + 1
            
            issue_type = issue.get('type', 'unknown')
            summary['by_type'][issue_type] = summary['by_type'].get(issue_type, 0) + 1
        
        return summary
    
    def _calculate_quality_score(self) -> float:
        """Calculate overall quality score (0-1)."""
        score = 1.0
        
        for issue in self.issues:
            severity = issue.get('severity', 'low')
            penalty = {
                'critical': 0.25,
                'high': 0.15,
                'medium': 0.08,
                'low': 0.03
            }.get(severity, 0.03)
            
            # Larger issues get bigger penalties
            count = issue.get('count', 1)
            pct = issue.get('pct', 0)
            
            if count > 0 and 'pct' in issue:
                penalty *= min(1, pct / 10)  # Scale by percentage
            
            score -= penalty
        
        return max(0, min(1, round(score, 3)))
    
    def save_report(self, report: Dict, output_path: str = 'quality_report.json'):
        """Save report as JSON file."""
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"📄 Report saved to: {output_path}")
    
    def print_report_summary(self, report: Dict):
        """Print a human-readable summary."""
        print("\n" + "="*60)
        print("📊 QUALITY REPORT SUMMARY")
        print("="*60)
        
        file_info = report.get('file_info', {})
        print(f"\n📄 File: {file_info.get('rows', 0):,} rows, {file_info.get('columns', 0)} columns")
        print(f"   Memory: {file_info.get('memory_usage_mb', 0)} MB")
        
        summary = report.get('summary', {})
        print(f"\n🐛 Issues Found: {summary.get('total_issues', 0)}")
        print(f"   🔴 Critical: {summary.get('critical', 0)}")
        print(f"   🟡 High: {summary.get('high', 0)}")
        print(f"   🟠 Medium: {summary.get('medium', 0)}")
        print(f"   🟢 Low: {summary.get('low', 0)}")
        
        print(f"\n📈 Quality Score: {report.get('quality_score', 0) * 100:.1f}%")
        
        if report.get('issues'):
            print(f"\n🔍 Top Issues:")
            for issue in report['issues'][:5]:
                severity_icon = {
                    'critical': '🔴',
                    'high': '🟡',
                    'medium': '🟠',
                    'low': '🟢'
                }.get(issue.get('severity', 'low'), '⚪')
                print(f"   {severity_icon} {issue.get('type')}: {issue.get('description')[:60]}...")


# ===== Run on the generated dataset =====
if __name__ == "__main__":
    # Load your messy dataset
    profiler = DataQualityProfiler()
    df = profiler.load_data('data/raw/messy_experiment_data.csv')
    
    # Generate report
    report = profiler.profile_data()
    
    # Save report
    profiler.save_report(report, 'quality_report.json')
    
    # Print summary
    profiler.print_report_summary(report)