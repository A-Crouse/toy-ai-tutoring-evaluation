import pandas as pd
import numpy as np

# Load the data to analyze actual expected_result column
df = pd.read_csv('TutoringExperiment_evaluation_20250719.csv')

print("ACTUAL ANSWER CORRECTNESS ANALYSIS")
print("="*50)
print(f"Total test cases: {len(df)}")

# Check the expected_result column
if 'expected_result' in df.columns:
    print(f"\nActual Expected Results Distribution:")
    result_counts = df['expected_result'].value_counts()
    print(result_counts)
    
    # Calculate actual acceptance rate
    total_cases = len(df['expected_result'].dropna())
    accepted_cases = (df['expected_result'] == 'Answer Accepted').sum()
    acceptance_rate = accepted_cases / total_cases if total_cases > 0 else 0
    
    print(f"\nOverall Answer Acceptance Rate: {acceptance_rate:.2%}")
    print(f"Accepted: {accepted_cases} cases")
    print(f"Not Accepted: {total_cases - accepted_cases} cases")
    
    # Subject-wise acceptance rates
    print(f"\nAcceptance Rate by Subject:")
    subject_acceptance = df.groupby('math_level')['expected_result'].apply(
        lambda x: (x == 'Answer Accepted').sum() / len(x.dropna()) if len(x.dropna()) > 0 else 0
    ).sort_values(ascending=False)
    
    for subject, rate in subject_acceptance.items():
        subject_total = len(df[df['math_level'] == subject]['expected_result'].dropna())
        print(f"  {subject}: {rate:.1%} ({subject_total} cases)")

else:
    print("Expected_result column not found - using rating-based analysis")

# Show some sample data
print(f"\nSample Data (first 5 rows):")
sample_cols = ['test_id', 'math_level', 'student_claim', 'expected_result']
available_cols = [col for col in sample_cols if col in df.columns]
print(df[available_cols].head())
