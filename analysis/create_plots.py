import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style
plt.style.use('default')
sns.set_palette("husl")

# Load the performance summary
perf_df = pd.read_csv('performance_summary.csv')

# Create visualizations
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# 1. Performance by Model and Approach
pivot_ratings = perf_df.pivot(index='model', columns='approach', values='mean_rating')
sns.heatmap(pivot_ratings, annot=True, cmap='RdYlGn', fmt='.2f', ax=axes[0,0])
axes[0,0].set_title('Mean Performance Rating by Model and Approach')

# 2. Cost vs Performance
for approach in perf_df['approach'].unique():
    approach_data = perf_df[perf_df['approach'] == approach]
    axes[0,1].scatter(approach_data['mean_cost'], approach_data['mean_rating'], 
                     label=approach, s=100, alpha=0.7)
    
    # Add model labels
    for idx, row in approach_data.iterrows():
        axes[0,1].annotate(row['model'][:3], (row['mean_cost'], row['mean_rating']), 
                          xytext=(5, 5), textcoords='offset points', fontsize=8)

axes[0,1].set_xlabel('Mean Cost ($)')
axes[0,1].set_ylabel('Mean Performance Rating')
axes[0,1].set_title('Cost vs Performance Trade-off')
axes[0,1].legend()
axes[0,1].grid(True, alpha=0.3)

# 3. Performance by Approach
approach_means = perf_df.groupby('approach')['mean_rating'].mean().sort_values(ascending=False)
bars = axes[1,0].bar(range(len(approach_means)), approach_means.values)
axes[1,0].set_xticks(range(len(approach_means)))
axes[1,0].set_xticklabels([x.replace('_', ' ').title() for x in approach_means.index])
axes[1,0].set_ylabel('Average Rating')
axes[1,0].set_title('Performance by Approach')
axes[1,0].set_ylim(0, 4)

# Add value labels on bars
for i, v in enumerate(approach_means.values):
    axes[1,0].text(i, v + 0.05, f'{v:.2f}', ha='center', va='bottom')

# 4. Cost Effectiveness
perf_df['cost_effectiveness'] = perf_df['mean_rating'] / perf_df['mean_cost']
top_efficient = perf_df.nlargest(6, 'cost_effectiveness')
bars = axes[1,1].bar(range(len(top_efficient)), top_efficient['cost_effectiveness'])
axes[1,1].set_xticks(range(len(top_efficient)))
axes[1,1].set_xticklabels([f"{row['approach'][:3]}+{row['model'][:3]}" 
                          for idx, row in top_efficient.iterrows()], rotation=45)
axes[1,1].set_ylabel('Cost Effectiveness (Rating/Cost)')
axes[1,1].set_title('Most Cost-Effective Combinations')

plt.tight_layout()
plt.savefig('tutoring_analysis_plots.png', dpi=300, bbox_inches='tight')
plt.show()

# Create a second figure for subject analysis
df = pd.read_csv('TutoringExperiment_evaluation_20250719.csv')
fig2, axes2 = plt.subplots(1, 2, figsize=(15, 6))

# Subject difficulty
subjects = ['Elementary', 'Algebra', 'Trigonometry', 'Geometry', 'Calculus']
subject_ratings = []

for subject in subjects:
    subject_data = df[df['math_level'] == subject]
    ratings = []
    for col in df.columns:
        if '_rating' in col:
            ratings.extend(subject_data[col].dropna().tolist())
    if ratings:
        subject_ratings.append(np.mean(ratings))
    else:
        subject_ratings.append(0)

# Sort by difficulty
subject_difficulty = list(zip(subjects, subject_ratings))
subject_difficulty.sort(key=lambda x: x[1])

subjects_sorted = [x[0] for x in subject_difficulty]
ratings_sorted = [x[1] for x in subject_difficulty]

bars = axes2[0].bar(range(len(subjects_sorted)), ratings_sorted)
axes2[0].set_xticks(range(len(subjects_sorted)))
axes2[0].set_xticklabels(subjects_sorted, rotation=45)
axes2[0].set_ylabel('Average Rating')
axes2[0].set_title('Subject Difficulty (Lower = Harder)')
axes2[0].set_ylim(0, 4)

# Color bars by difficulty
for i, bar in enumerate(bars):
    if ratings_sorted[i] < 2.0:
        bar.set_color('red')
    elif ratings_sorted[i] < 2.5:
        bar.set_color('orange')
    elif ratings_sorted[i] < 3.0:
        bar.set_color('yellow')
    else:
        bar.set_color('green')

# Add value labels
for i, v in enumerate(ratings_sorted):
    axes2[0].text(i, v + 0.05, f'{v:.2f}', ha='center', va='bottom')

# Model comparison
model_means = perf_df.groupby('model')['mean_rating'].mean().sort_values(ascending=False)
bars2 = axes2[1].bar(range(len(model_means)), model_means.values)
axes2[1].set_xticks(range(len(model_means)))
axes2[1].set_xticklabels([x.replace('_', ' ').title() for x in model_means.index])
axes2[1].set_ylabel('Average Rating')
axes2[1].set_title('Model Performance Comparison')
axes2[1].set_ylim(0, 4)

# Add value labels
for i, v in enumerate(model_means.values):
    axes2[1].text(i, v + 0.05, f'{v:.2f}', ha='center', va='bottom')

plt.tight_layout()
plt.savefig('subject_model_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

print("📊 Visualizations saved:")
print("  - tutoring_analysis_plots.png")
print("  - subject_model_analysis.png")
