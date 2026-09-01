import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_messy_experiment_data(n_rows=10000, output_path='data/raw/messy_experiment_data.csv'):
    """
    Generate a deliberately messy experiment dataset with ALL possible issues.
    """
    
    print(f"Generating {n_rows} rows of beautifully messy data...")
    
    # Create base data with issues
    data = {
        # ===== COLUMN 1: user_id =====
        # Issues: duplicates, some missing
        'user_id': [],
        
        # ===== COLUMN 2: experiment_group =====
        # Issues: invalid values, case issues, whitespace
        'experiment_group': [],
        
        # ===== COLUMN 3: conversion =====
        # Issues: missing, invalid values (>1)
        'conversion': [],
        
        # ===== COLUMN 4: revenue =====
        # Issues: outliers, negative, strings with $/commas, missing
        'revenue': [],
        
        # ===== COLUMN 5: date =====
        # Issues: mixed formats (YYYY-MM-DD, MM/DD/YYYY, DD-MM-YYYY)
        'date': [],
        
        # ===== COLUMN 6: device =====
        # Issues: inconsistent categories, case issues
        'device': [],
        
        # ===== COLUMN 7: country =====
        # Issues: inconsistent (US, USA, United States)
        'country': [],
        
        # ===== COLUMN 8: age =====
        # Issues: outliers, missing
        'age': [],
        
        # ===== COLUMN 9: session_duration =====
        # Issues: zero, negative, outliers
        'session_duration': [],
        
        # ===== COLUMN 10: empty_column =====
        # Issues: completely empty
        'empty_column': []
    }
    
    # Track how many rows we've generated for each column
    # Some columns need specific distributions
    
    # 1. Generate user_id (with duplicates)
    # 9000 unique users, 1000 duplicates
    unique_users = [f'user_{i:05d}' for i in range(1, 9001)]
    duplicate_users = [f'user_{i:05d}' for i in range(1, 1001)]  # Duplicates of first 1000
    
    # Shuffle and combine
    all_users = unique_users + duplicate_users
    random.shuffle(all_users)
    # Ensure we have exactly n_rows
    while len(all_users) < n_rows:
        all_users.append(f'user_{random.randint(1, 9000):05d}')
    data['user_id'] = all_users[:n_rows]
    
    # 2. Generate experiment_group (with invalid values)
    groups = []
    # 8500 valid (4500 control, 4000 treatment)
    for i in range(n_rows):
        if i < 4500:
            groups.append('control')
        elif i < 8500:
            groups.append('treatment')
        elif i < 8800:
            groups.append('Control')  # Wrong case
        elif i < 9000:
            groups.append('test')      # Completely invalid
        elif i < 9500:
            groups.append('TRT')       # Another invalid
        else:
            groups.append('treatment ')  # Whitespace issue
    random.shuffle(groups)
    data['experiment_group'] = groups
    
    # 3. Generate conversion (with missing and invalid)
    conversions = []
    for i in range(n_rows):
        if i < 8500:
            conversions.append(random.choice([0, 1]))
        elif i < 9500:
            conversions.append(np.nan)  # Missing
        else:
            conversions.append(2)        # Invalid (should be 0 or 1)
    random.shuffle(conversions)
    data['conversion'] = conversions
    
    # 4. Generate revenue (with ALL issues)
    revenues = []
    for i in range(n_rows):
        if i < 8000:
            # Normal revenue
            revenues.append(round(random.uniform(10, 200), 2))
        elif i < 8100:
            # Outliers (high)
            revenues.append(round(random.uniform(10000, 50000), 2))
        elif i < 8900:
            revenues.append(np.nan)  # Missing
        elif i < 9200:
            # Revenue as string with $
            revenues.append(f"${round(random.uniform(10, 200), 2)}")
        elif i < 9500:
            # Revenue as string with comma
            revenues.append(f"{random.randint(100, 999)},{random.randint(10, 99)}")
        elif i < 9900:
            # Negative revenue (invalid)
            revenues.append(round(random.uniform(-100, -10), 2))
        else:
            # Normal again
            revenues.append(round(random.uniform(10, 200), 2))
    random.shuffle(revenues)
    data['revenue'] = revenues
    
    # 5. Generate date (with mixed formats)
    dates = []
    start_date = datetime(2024, 1, 1)
    for i in range(n_rows):
        random_days = random.randint(0, 365)
        date_obj = start_date + timedelta(days=random_days)
        
        if i < 3000:
            # Format 1: YYYY-MM-DD
            dates.append(date_obj.strftime('%Y-%m-%d'))
        elif i < 6000:
            # Format 2: MM/DD/YYYY
            dates.append(date_obj.strftime('%m/%d/%Y'))
        elif i < 9000:
            # Format 3: DD-MM-YYYY
            dates.append(date_obj.strftime('%d-%m-%Y'))
        else:
            # Format 1 again
            dates.append(date_obj.strftime('%Y-%m-%d'))
    random.shuffle(dates)
    data['date'] = dates
    
    # 6. Generate device (with inconsistent categories)
    devices = []
    device_pool = ['mobile', 'desktop', 'tablet']
    for i in range(n_rows):
        if i < 3000:
            devices.append('mobile')
        elif i < 6000:
            devices.append('desktop')
        elif i < 8000:
            devices.append('tablet')
        elif i < 8500:
            devices.append('Mobile')    # Wrong case
        elif i < 9000:
            devices.append('Desktop')   # Wrong case
        elif i < 9500:
            devices.append('iPhone')    # Too granular
        else:
            devices.append('Android')   # Too granular
    random.shuffle(devices)
    data['device'] = devices
    
    # 7. Generate country (with inconsistent formats)
    countries = []
    country_pool = [
        'US', 'USA', 'United States',  # All mean US
        'UK', 'United Kingdom',         # All mean UK
        'India', 'IN'                   # All mean India
    ]
    for i in range(n_rows):
        if i < 3000:
            countries.append('US')
        elif i < 5000:
            countries.append('USA')
        elif i < 6000:
            countries.append('United States')
        elif i < 7000:
            countries.append('UK')
        elif i < 8000:
            countries.append('United Kingdom')
        elif i < 9000:
            countries.append('India')
        else:
            countries.append('IN')
    random.shuffle(countries)
    data['country'] = countries
    
    # 8. Generate age (with outliers and missing)
    ages = []
    for i in range(n_rows):
        if i < 9000:
            ages.append(random.randint(18, 65))
        elif i < 9050:
            ages.append(random.randint(100, 120))  # Too old
        elif i < 9100:
            ages.append(random.randint(5, 12))      # Too young
        elif i < 9600:
            ages.append(np.nan)                     # Missing
        else:
            ages.append(random.randint(18, 65))     # Normal
    random.shuffle(ages)
    data['age'] = ages
    
    # 9. Generate session_duration (with zeros, negatives, outliers)
    durations = []
    for i in range(n_rows):
        if i < 8500:
            durations.append(random.randint(30, 600))
        elif i < 9300:
            durations.append(0)                      # Zero (invalid)
        elif i < 9900:
            durations.append(random.randint(-100, -10))  # Negative
        else:
            durations.append(random.randint(30, 600))     # Normal
    random.shuffle(durations)
    data['session_duration'] = durations
    
    # 10. Generate empty_column (all nulls)
    data['empty_column'] = [np.nan] * n_rows
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # ===== ADD EXTRA ISSUES =====
    
    # Add exact duplicate rows (100 rows)
    duplicate_rows = df.iloc[:100].copy()
    df = pd.concat([df, duplicate_rows], ignore_index=True)
    
    # Add duplicate user IDs across groups (experiment design violation)
    # Take 50 users from control, put them in treatment too
    control_users = df[df['experiment_group'] == 'control']['user_id'].head(50).values
    treatment_users = df[df['experiment_group'] == 'treatment']['user_id'].head(50).values
    for i, (control_user, treatment_user) in enumerate(zip(control_users, treatment_users)):
        # Replace treatment users with control user IDs (creating duplicates across groups)
        idx = df[df['user_id'] == treatment_user].index
        if len(idx) > 0:
            df.loc[idx[0], 'user_id'] = control_user
    
    # Add leading/trailing whitespace to some values
    whitespace_indices = random.sample(range(len(df)), 200)
    for idx in whitespace_indices:
        if isinstance(df.loc[idx, 'experiment_group'], str):
            df.loc[idx, 'experiment_group'] = ' ' + df.loc[idx, 'experiment_group']
        if isinstance(df.loc[idx, 'device'], str):
            df.loc[idx, 'device'] = df.loc[idx, 'device'] + ' '
    
    # ===== FINAL SHUFFLE =====
    df = df.sample(frac=1).reset_index(drop=True)
    
    # ===== SAVE =====
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save as CSV
    df.to_csv(output_path, index=False)
    
    # Also save as Excel (for testing Excel upload)
    excel_path = output_path.replace('.csv', '.xlsx')
    df.to_excel(excel_path, index=False)
    
    # ===== REPORT WHAT WE CREATED =====
    print(f"\n✅ Dataset generated successfully!")
    print(f"   - CSV: {output_path}")
    print(f"   - Excel: {excel_path}")
    print(f"   - Total rows: {len(df)}")
    print(f"   - Total columns: {len(df.columns)}")
    
    print("\n📊 Column Summary:")
    for col in df.columns:
        nulls = df[col].isna().sum()
        null_pct = nulls / len(df) * 100
        unique = df[col].nunique()
        print(f"   - {col}: {df[col].dtype} | {nulls} nulls ({null_pct:.1f}%) | {unique} unique values")
    
    print("\n🐛 Issues Injected:")
    print("   🔴 CRITICAL:")
    print("      - Duplicate user IDs across experiment groups (experiment design violation)")
    print("      - Invalid group labels (Control, test, TRT)")
    print("   🟡 HIGH:")
    print("      - Missing values in conversion, revenue, age (5-10%)")
    print("      - Invalid conversion values (2s instead of 0/1)")
    print("      - Revenue as strings with $ and commas")
    print("      - Negative revenue values")
    print("   🟠 MEDIUM:")
    print("      - Revenue outliers (>$10,000)")
    print("      - Mixed date formats (YYYY-MM-DD, MM/DD/YYYY, DD-MM-YYYY)")
    print("      - Inconsistent device categories (mobile, Mobile, iPhone)")
    print("      - Inconsistent country formats (US, USA, United States)")
    print("      - Age outliers (>100 or <18)")
    print("      - Session duration with zeros and negatives")
    print("   🟢 LOW:")
    print("      - Leading/trailing whitespace")
    print("      - Case inconsistencies")
    print("      - Empty column (all nulls)")
    print("      - Exact duplicate rows")
    
    # Print sample of issues
    print("\n🔍 Sample Issue Rows:")
    print("\n--- Invalid Groups ---")
    invalid_groups = df[~df['experiment_group'].str.lower().isin(['control', 'treatment'])].head(5)
    if len(invalid_groups) > 0:
        print(invalid_groups[['user_id', 'experiment_group']].to_string(index=False))
    
    print("\n--- Duplicate Users Across Groups ---")
    duplicate_users = df.groupby('user_id')['experiment_group'].nunique()
    duplicate_users = duplicate_users[duplicate_users > 1].head(5)
    if len(duplicate_users) > 0:
        for user_id in duplicate_users.index[:5]:
            groups = df[df['user_id'] == user_id]['experiment_group'].unique()
            print(f"   {user_id}: {', '.join(groups)}")
    
    print("\n--- Mixed Dates ---")
    print(df[['date']].head(10).to_string(index=False))
    
    return df

# Run it!
if __name__ == "__main__":
    df = generate_messy_experiment_data(
        n_rows=10000,
        output_path='data/raw/messy_experiment_data.csv'
    )