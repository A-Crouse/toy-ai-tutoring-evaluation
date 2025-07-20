import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load the data
df = pd.read_csv('TutoringExperiment_evaluation_20250719.csv')

print("STUDENT ANSWER CORRECTNESS IMPACT ON AI TUTORING PERFORMANCE")
print("="*70)

# Separate cases by student answer correctness
accepted_cases = df[df['expected_result'] == 'Answer Accepted']
not_accepted_cases = df[df['expected_result'] == 'Answer Not Accepted']

print(f"\nDataset Split:")
print(f"Student Correct (Answer Accepted): {len(accepted_cases)} cases")
print(f"Student Incorrect (Answer Not Accepted): {len(not_accepted_cases)} cases")

models = ['claude_haiku', 'gpt4o_mini', 'phi3_mini']
approaches = ['zero_shot', 'few_shot', 'cot']

# Analyze performance by student correctness
results = []

for approach in approaches:
    for model in models:
        rating_col = f"{approach}_{model}_rating"
        
        if rating_col in df.columns:
            # Performance when student was CORRECT
            correct_ratings = accepted_cases[rating_col].dropna()
            correct_mean = correct_ratings.mean() if len(correct_ratings) > 0 else np.nan
            correct_high_quality = len(correct_ratings[correct_ratings >= 3]) / len(correct_ratings) if len(correct_ratings) > 0 else 0
            
            # Performance when student was INCORRECT  
            incorrect_ratings = not_accepted_cases[rating_col].dropna()
            incorrect_mean = incorrect_ratings.mean() if len(incorrect_ratings) > 0 else np.nan
            incorrect_high_quality = len(incorrect_ratings[incorrect_ratings >= 3]) / len(incorrect_ratings) if len(incorrect_ratings) > 0 else 0
            
            # Calculate difference
            rating_diff = correct_mean - incorrect_mean if not np.isnan(correct_mean) and not np.isnan(incorrect_mean) else np.nan
            quality_diff = correct_high_quality - incorrect_high_quality
            
            results.append({
                'model': model,
                'approach': approach,
                'correct_mean_rating': correct_mean,
                'incorrect_mean_rating': incorrect_mean,
                'rating_difference': rating_diff,
                'correct_quality_rate': correct_high_quality,
                'incorrect_quality_rate': incorrect_high_quality,
                'quality_difference': quality_diff,
                'correct_n': len(correct_ratings),
                'incorrect_n': len(incorrect_ratings)
            })

results_df = pd.DataFrame(results)

print(f"\n📊 PERFORMANCE BY STUDENT ANSWER CORRECTNESS")
print(f"{'='*70}")

# Show detailed results
print(f"\nMean Rating Comparison:")
print(f"{'Model':<12} {'Approach':<10} {'Correct':<8} {'Incorrect':<8} {'Difference':<10}")
print(f"{'-'*60}")

for _, row in results_df.iterrows():
    if not np.isnan(row['rating_difference']):
        print(f"{row['model']:<12} {row['approach']:<10} {row['correct_mean_rating']:<8.2f} {row['incorrect_mean_rating']:<8.2f} {row['rating_difference']:<10.2f}")

print(f"\nHigh-Quality Response Rate (≥3.0) Comparison:")
print(f"{'Model':<12} {'Approach':<10} {'Correct':<8} {'Incorrect':<8} {'Difference':<10}")
print(f"{'-'*60}")

for _, row in results_df.iterrows():
    print(f"{row['model']:<12} {row['approach']:<10} {row['correct_quality_rate']:<8.1%} {row['incorrect_quality_rate']:<8.1%} {row['quality_difference']:<10.1%}")

# Statistical analysis
print(f"\n📈 KEY INSIGHTS")
print(f"{'='*50}")

# Overall performance difference
overall_correct = results_df['correct_mean_rating'].mean()
overall_incorrect = results_df['incorrect_mean_rating'].mean()
overall_diff = overall_correct - overall_incorrect

print(f"Overall mean rating when student correct: {overall_correct:.2f}")
print(f"Overall mean rating when student incorrect: {overall_incorrect:.2f}")
print(f"Overall difference: {overall_diff:.2f}")

# Find biggest differences
biggest_positive = results_df.loc[results_df['rating_difference'].idxmax()]
biggest_negative = results_df.loc[results_df['rating_difference'].idxmin()]

print(f"\nBiggest performance boost with correct students:")
print(f"  {biggest_positive['approach']} + {biggest_positive['model']}: +{biggest_positive['rating_difference']:.2f}")

print(f"\nBiggest performance drop with correct students:")
print(f"  {biggest_negative['approach']} + {biggest_negative['model']}: {biggest_negative['rating_difference']:.2f}")

# Approach-level analysis
approach_analysis = results_df.groupby('approach').agg({
    'correct_mean_rating': 'mean',
    'incorrect_mean_rating': 'mean',
    'rating_difference': 'mean',
    'correct_quality_rate': 'mean',
    'incorrect_quality_rate': 'mean',
    'quality_difference': 'mean'
}).round(3)

print(f"\n🔍 APPROACH-LEVEL ANALYSIS")
print(f"{'='*50}")
print(approach_analysis)

# Model-level analysis
model_analysis = results_df.groupby('model').agg({
    'correct_mean_rating': 'mean',
    'incorrect_mean_rating': 'mean', 
    'rating_difference': 'mean',
    'correct_quality_rate': 'mean',
    'incorrect_quality_rate': 'mean',
    'quality_difference': 'mean'
}).round(3)

print(f"\n🤖 MODEL-LEVEL ANALYSIS")
print(f"{'='*50}")
print(model_analysis)

# Create visualization
plt.figure(figsize=(15, 10))

# Plot 1: Rating differences
plt.subplot(2, 2, 1)
valid_results = results_df.dropna(subset=['rating_difference'])
colors = {'zero_shot': 'red', 'few_shot': 'blue', 'cot': 'green'}
for approach in valid_results['approach'].unique():
    approach_data = valid_results[valid_results['approach'] == approach]
    plt.scatter(approach_data['correct_mean_rating'], approach_data['incorrect_mean_rating'], 
               c=colors[approach], label=approach, s=100, alpha=0.7)

plt.plot([0, 5], [0, 5], 'k--', alpha=0.5, label='Equal Performance')
plt.xlabel('Rating when Student Correct')
plt.ylabel('Rating when Student Incorrect')
plt.title('AI Performance: Correct vs Incorrect Student Answers')
plt.legend()
plt.grid(True, alpha=0.3)

# Plot 2: Quality rate differences
plt.subplot(2, 2, 2)
for approach in results_df['approach'].unique():
    approach_data = results_df[results_df['approach'] == approach]
    plt.scatter(approach_data['correct_quality_rate'], approach_data['incorrect_quality_rate'], 
               c=colors[approach], label=approach, s=100, alpha=0.7)

plt.plot([0, 1], [0, 1], 'k--', alpha=0.5, label='Equal Performance')
plt.xlabel('Quality Rate when Student Correct')
plt.ylabel('Quality Rate when Student Incorrect')
plt.title('Quality Rates: Correct vs Incorrect Student Answers')
plt.legend()
plt.grid(True, alpha=0.3)

# Plot 3: Difference by approach
plt.subplot(2, 2, 3)
approach_means = results_df.groupby('approach')['rating_difference'].mean()
bars = plt.bar(range(len(approach_means)), approach_means.values)
plt.xticks(range(len(approach_means)), [x.replace('_', ' ').title() for x in approach_means.index])
plt.ylabel('Mean Rating Difference\n(Correct - Incorrect)')
plt.title('Performance Difference by Approach')
plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)

# Color bars based on performance
for i, bar in enumerate(bars):
    if approach_means.values[i] > 0.2:
        bar.set_color('green')
    elif approach_means.values[i] < -0.2:
        bar.set_color('red')
    else:
        bar.set_color('orange')

# Plot 4: Difference by model
plt.subplot(2, 2, 4)
model_means = results_df.groupby('model')['rating_difference'].mean()
bars = plt.bar(range(len(model_means)), model_means.values)
plt.xticks(range(len(model_means)), [x.replace('_', ' ').title() for x in model_means.index], rotation=45)
plt.ylabel('Mean Rating Difference\n(Correct - Incorrect)')
plt.title('Performance Difference by Model')
plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)

# Color bars
for i, bar in enumerate(bars):
    if model_means.values[i] > 0.2:
        bar.set_color('green')
    elif model_means.values[i] < -0.2:
        bar.set_color('red')
    else:
        bar.set_color('orange')

plt.tight_layout()
plt.savefig('student_correctness_impact_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# Save detailed results
results_df.to_csv('student_correctness_impact_results.csv', index=False)

print(f"\n💡 CONCLUSIONS")
print(f"{'='*50}")
if overall_diff > 0.1:
    print(f"✅ AI tutors perform BETTER when students give correct answers (+{overall_diff:.2f})")
elif overall_diff < -0.1:
    print(f"⚠️ AI tutors perform WORSE when students give correct answers ({overall_diff:.2f})")
else:
    print(f"➡️ AI tutor performance is SIMILAR regardless of student correctness ({overall_diff:.2f})")

print(f"\nThis analysis reveals whether AI tutoring quality depends on")
print(f"the initial correctness of student responses.")

print(f"\n📁 Generated files:")
print(f"  - student_correctness_impact_analysis.png")
print(f"  - student_correctness_impact_results.csv")
