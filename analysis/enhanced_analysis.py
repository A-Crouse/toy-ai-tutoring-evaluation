import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load the data
df = pd.read_csv('TutoringExperiment_evaluation_20250719.csv')
performance_df = pd.read_csv('performance_summary.csv')

print(f"Loaded {len(df)} test cases")
print(f"Dataset columns: {list(df.columns)}")

# Extract answer correctness data
models = ['claude_haiku', 'gpt4o_mini', 'phi3_mini']
approaches = ['zero_shot', 'few_shot', 'cot']

correctness_data = []

for approach in approaches:
    for model in models:
        rating_col = f"{approach}_{model}_rating"
        cost_col = f"{approach}_{model}_cost"
        
        if rating_col in df.columns:
            ratings = df[rating_col].dropna()
            costs = df[cost_col].dropna()
            
            # Use rating >= 3 as proxy for good tutoring (answer likely accepted)
            accepted_count = len(ratings[ratings >= 3])
            not_accepted_count = len(ratings[ratings < 3])
            total_responses = len(ratings)
            accuracy_rate = accepted_count / total_responses if total_responses > 0 else 0
            
            correctness_data.append({
                'model': model,
                'approach': approach,
                'accepted_answers': accepted_count,
                'not_accepted_answers': not_accepted_count,
                'total_responses': total_responses,
                'accuracy_rate': accuracy_rate,
                'mean_rating': ratings.mean(),
                'mean_cost': costs.mean() if len(costs) > 0 else 0,
                'n_samples': len(ratings)
            })

correctness_df = pd.DataFrame(correctness_data)

print("\n" + "="*80)
print("ENHANCED TUTORING MODEL EVALUATION SUMMARY")
print("="*80)

print(f"\n📊 ANSWER CORRECTNESS ANALYSIS")
print(f"{'─'*50}")
print(correctness_df[['model', 'approach', 'accuracy_rate', 'mean_rating']].to_string(index=False))

# Create enhanced visualizations
plt.style.use('default')

# 1. Answer Correctness Heatmap
plt.figure(figsize=(10, 6))
pivot_accuracy = correctness_df.pivot(index='model', columns='approach', values='accuracy_rate')
sns.heatmap(pivot_accuracy, annot=True, cmap='RdYlGn', fmt='.2f', 
            cbar_kws={'label': 'Answer Accuracy Rate'})
plt.title('Answer Correctness Rate by Model and Approach')
plt.ylabel('Model')
plt.xlabel('Approach')
plt.tight_layout()
plt.savefig('answer_correctness_heatmap.png', dpi=300, bbox_inches='tight')
plt.show()

# 2. Performance vs Accuracy Comparison
plt.figure(figsize=(12, 8))
approaches_unique = correctness_df['approach'].unique()
colors = {'zero_shot': 'red', 'few_shot': 'blue', 'cot': 'green'}

for approach in approaches_unique:
    approach_data = correctness_df[correctness_df['approach'] == approach]
    plt.scatter(approach_data['accuracy_rate'], approach_data['mean_rating'], 
               c=colors[approach], label=approach, s=100, alpha=0.7)
    
    for idx, row in approach_data.iterrows():
        plt.annotate(row['model'][:3], (row['accuracy_rate'], row['mean_rating']), 
                    xytext=(5, 5), textcoords='offset points', fontsize=9)

plt.xlabel('Answer Accuracy Rate')
plt.ylabel('Mean Performance Rating')
plt.title('Answer Correctness vs Performance Rating')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('accuracy_vs_rating.png', dpi=300, bbox_inches='tight')
plt.show()

# 3. Approach Performance Summary
approach_summary = correctness_df.groupby('approach').agg({
    'accuracy_rate': 'mean',
    'mean_rating': 'mean'
}).round(3)

print(f"\n�� APPROACH PERFORMANCE SUMMARY")
print(f"{'─'*50}")
print(approach_summary)

# Enhanced insights with qualitative observations
print(f"\n🔍 KEY QUALITATIVE INSIGHTS")
print(f"{'─'*50}")
print("1. CoT Prompting Issues:")
print("   • Tends to solve problems FOR students rather than guiding them")
print("   • Lower overall performance compared to few-shot")
print()
print("2. Hallucination Concerns:")
print("   • Zero-shot and few-shot occasionally create non-existent conversation turns")
print("   • May confuse students with fabricated dialogue")
print()
print("3. Few-shot GPT-4o Mini Excellence:")
print("   • Demonstrates optimal balance of brevity, empathy, and accuracy")
print("   • Highest performance rating (3.60) in the evaluation")

# Best performers analysis
print(f"\n🏆 TOP PERFORMERS")
print(f"{'─'*50}")
best_overall = correctness_df.loc[correctness_df['mean_rating'].idxmax()]
best_accuracy = correctness_df.loc[correctness_df['accuracy_rate'].idxmax()]

print(f"Best Overall Rating: {best_overall['approach']} + {best_overall['model']}")
print(f"  Rating: {best_overall['mean_rating']:.2f}, Accuracy: {best_overall['accuracy_rate']:.2f}")
print(f"Best Accuracy: {best_accuracy['approach']} + {best_accuracy['model']}")
print(f"  Accuracy: {best_accuracy['accuracy_rate']:.2f}, Rating: {best_accuracy['mean_rating']:.2f}")

# Cost effectiveness with accuracy
correctness_df['cost_effectiveness'] = correctness_df['mean_rating'] / correctness_df['mean_cost']
best_value = correctness_df.loc[correctness_df['cost_effectiveness'].idxmax()]

print(f"Best Value: {best_value['approach']} + {best_value['model']}")
print(f"  Cost-effectiveness: {best_value['cost_effectiveness']:.0f}, Rating: {best_value['mean_rating']:.2f}")

# Enhanced recommendations
print(f"\n💡 ENHANCED RECOMMENDATIONS")
print(f"{'─'*50}")
print("For Production Deployment:")
print("  1. Primary Choice: Few-shot GPT-4o Mini")
print("     - Best overall balance (Rating: 3.60, Good accuracy)")
print("     - Balanced brevity, empathy, and accuracy")
print("  2. Budget Alternative: Few-shot Phi-3 Mini")
print("     - Excellent cost-effectiveness")
print()
print("Avoid for Production:")
print("  • Chain-of-Thought prompting (tends to over-solve)")
print("  • Zero-shot approaches (inconsistent, hallucination risk)")
print()
print("For Further Development:")
print("  • Improve CoT to guide rather than solve")
print("  • Address hallucination in zero-shot/few-shot")
print("  • Enhance all approaches for Elementary math")

# Save results
correctness_df.to_csv('enhanced_correctness_analysis.csv', index=False)

print(f"\n✅ Enhanced analysis complete!")
print(f"📁 Generated files:")
print(f"  - answer_correctness_heatmap.png")
print(f"  - accuracy_vs_rating.png")
print(f"  - enhanced_correctness_analysis.csv")
