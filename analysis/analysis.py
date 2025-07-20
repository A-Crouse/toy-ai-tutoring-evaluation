import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load the data
df = pd.read_csv('TutoringExperiment_evaluation_20250719.csv')
print(f"Loaded {len(df)} test cases")
print(f"\nColumns: {list(df.columns)}")

# Extract performance data
models = ['claude_haiku', 'gpt4o_mini', 'phi3_mini']
approaches = ['zero_shot', 'few_shot', 'cot']

performance_data = []

for approach in approaches:
    for model in models:
        rating_col = f"{approach}_{model}_rating"
        cost_col = f"{approach}_{model}_cost"
        
        if rating_col in df.columns and cost_col in df.columns:
            ratings = df[rating_col].dropna()
            costs = df[cost_col].dropna()
            
            if len(ratings) > 0:
                performance_data.append({
                    'model': model,
                    'approach': approach,
                    'mean_rating': ratings.mean(),
                    'median_rating': ratings.median(),
                    'std_rating': ratings.std(),
                    'mean_cost': costs.mean(),
                    'total_cost': costs.sum(),
                    'n_samples': len(ratings)
                })

perf_df = pd.DataFrame(performance_data)

print("\n" + "="*80)
print("TUTORING MODEL EVALUATION SUMMARY")
print("="*80)

print(f"\n📊 DATASET OVERVIEW")
print(f"Total test cases: {len(df)}")
print(f"Subjects: {', '.join(df['math_level'].unique())}")
print(f"Models: {len(perf_df['model'].unique())}")
print(f"Approaches: {len(perf_df['approach'].unique())}")

print(f"\n🏆 PERFORMANCE SUMMARY")
print(perf_df.to_string(index=False))

print(f"\n📈 BEST PERFORMERS")
best = perf_df.nlargest(3, 'mean_rating')[['model', 'approach', 'mean_rating', 'mean_cost']]
for idx, row in best.iterrows():
    print(f"{row['approach']} + {row['model']}: Rating {row['mean_rating']:.2f}, Cost ${row['mean_cost']:.4f}")

print(f"\n💰 COST ANALYSIS")
total_cost = perf_df['total_cost'].sum()
print(f"Total cost: ${total_cost:.4f}")
print(f"Average cost per approach: ${perf_df['mean_cost'].mean():.4f}")

# Cost effectiveness
perf_df['cost_effectiveness'] = perf_df['mean_rating'] / perf_df['mean_cost']
print(f"\n💡 MOST COST-EFFECTIVE")
efficient = perf_df.nlargest(3, 'cost_effectiveness')[['model', 'approach', 'mean_rating', 'mean_cost', 'cost_effectiveness']]
for idx, row in efficient.iterrows():
    print(f"{row['approach']} + {row['model']}: Rating {row['mean_rating']:.2f}, Cost ${row['mean_cost']:.4f}, Effectiveness {row['cost_effectiveness']:.1f}")

print(f"\n📚 SUBJECT ANALYSIS")
subject_perf = []
for subject in df['math_level'].unique():
    subject_data = df[df['math_level'] == subject]
    avg_ratings = []
    for approach in approaches:
        for model in models:
            rating_col = f"{approach}_{model}_rating"
            if rating_col in df.columns:
                ratings = subject_data[rating_col].dropna()
                if len(ratings) > 0:
                    avg_ratings.append(ratings.mean())
    
    if avg_ratings:
        subject_perf.append({
            'subject': subject,
            'avg_rating': np.mean(avg_ratings),
            'n_cases': len(subject_data)
        })

subject_df = pd.DataFrame(subject_perf).sort_values('avg_rating')
print("\nSubject difficulty (lower = harder):")
for idx, row in subject_df.iterrows():
    print(f"{row['subject']}: {row['avg_rating']:.2f} ({row['n_cases']} cases)")

# Save results
perf_df.to_csv('performance_summary.csv', index=False)
print(f"\n✅ Analysis complete! Saved performance_summary.csv")
