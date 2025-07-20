#!/usr/bin/env python3
"""
Complete AI tutoring experiment runner - all in one file for reliability.
"""

import requests
import json
import csv
import time
import os
from datetime import datetime
from collections import defaultdict

# OpenRouter configuration
OPENROUTER_API_KEY = "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"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

MODELS = {
    'phi3_mini': {
        'name': 'Phi-3.5-mini',
        'model_id': 'microsoft/phi-3.5-mini-128k-instruct',
        'cost_per_1k_input': 0.0001,
        'cost_per_1k_output': 0.0001
    },
    'claude_haiku': {
        'name': 'Claude 3.5 Haiku',
        'model_id': 'anthropic/claude-3.5-haiku',
        'cost_per_1k_input': 0.0008,
        'cost_per_1k_output': 0.004
    },
    'gpt4o_mini': {
        'name': 'GPT-4o-mini',
        'model_id': 'openai/gpt-4o-mini',
        'cost_per_1k_input': 0.00015,
        'cost_per_1k_output': 0.0006
    }
}

class ExperimentRunner:
    """Complete experiment runner."""
    
    def __init__(self):
        self.results = []
        self.total_cost = 0.0
        
    def make_api_request(self, model_key, prompt):
        """Make request to OpenRouter API."""
        model_config = MODELS[model_key]
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/tutoring-research",
            "X-Title": "AI Tutoring Research"
        }
        
        data = {
            "model": model_config['model_id'],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2000,
            "temperature": 0.0
        }
        
        try:
            response = requests.post(OPENROUTER_URL, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            usage = result.get('usage', {})
            input_tokens = usage.get('prompt_tokens', 0)
            output_tokens = usage.get('completion_tokens', 0)
            
            cost = (input_tokens/1000 * model_config['cost_per_1k_input'] + 
                   output_tokens/1000 * model_config['cost_per_1k_output'])
            
            return {
                'success': True,
                'content': content,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'cost': cost
            }
            
        except Exception as e:
            return {
                'success': False,
                'content': '',
                'error': str(e),
                'cost': 0.0
            }
    
    def format_conversation(self, dialogue_data):
        """Format dialogue into conversation history and student claim."""
        conversation_history = ""
        student_claim = ""
        
        for exchange in dialogue_data.get('full_dialogue', [])[:-1]:
            role = "Student" if exchange['role'] == 'user' else "Tutor"
            conversation_history += f"{role}: {exchange['content']}\n"
        
        if dialogue_data.get('full_dialogue'):
            last_exchange = dialogue_data['full_dialogue'][-1]
            if last_exchange['role'] == 'user':
                student_claim = last_exchange['content']
        
        return conversation_history.strip(), student_claim
    
    def create_zero_shot_prompt(self, conversation_history, student_claim):
        """Create zero-shot prompt."""
        formatted_conversation = conversation_history
        if student_claim:
            formatted_conversation += f"\nStudent: {student_claim}"
        
        return f"""You are an expert math tutor. Based on this conversation, provide your next response to help the student learn.

Conversation:
{formatted_conversation}

Your response as the tutor:"""
    
    def create_few_shot_prompt(self, conversation_history, student_claim):
        """Create few-shot prompt with examples."""
        examples = """### Example 1: Conceptual Error
Tutor: Let's solve: 2 + 3 × 4. What do you get?
Student: I got 20. I added 2 + 3 = 5, then multiplied by 4.
Tutor: I can see your thinking! You're doing operations from left to right, which makes sense. However, there's a special rule called the order of operations. Can you think of what we should do first when we see both addition and multiplication?

### Example 2: Computational Error
Tutor: What's the area of a rectangle with length 6 and width 4?
Student: Area equals length times width, so 6 × 4 = 28.
Tutor: Perfect! You've got the right formula. Let me help you double-check that multiplication. What's 6 × 4? Maybe try thinking of it as 6 groups of 4.

### Example 3: Correct Answer
Tutor: If x + 5 = 12, what is x?
Student: I think x = 7, but I'm not sure I did it right.
Tutor: You absolutely did it right! That's exactly correct. Can you walk me through how you figured that out? I'd love to hear your thinking process."""
        
        formatted_conversation = conversation_history
        if student_claim:
            formatted_conversation += f"\nStudent: {student_claim}"
        
        return f"""You are an expert, Socratic math tutor. Your goal is to help the student understand their mistake without giving them the answer.

Here are examples of good tutoring:

{examples}

Now, based on this conversation, provide your response:

### Current Conversation:
{formatted_conversation}

### Tutor Response:"""
    
    def create_cot_prompt(self, conversation_history, student_claim):
        """Create chain-of-thought prompt."""
        formatted_conversation = conversation_history
        if student_claim:
            formatted_conversation += f"\nStudent: {student_claim}"
        
        return f"""You are an expert, Socratic math tutor. Think step-by-step to analyze the student's claim, then provide a helpful response.

First, in a <scratchpad> block, analyze:
1. What is the original problem?
2. What was the student's claim?
3. Is the claim correct or incorrect?
4. What is the specific error (if any)?
5. What pedagogical strategy should I use?

Then provide your tutor response.

### Current Conversation:
{formatted_conversation}

### Assistant:
<scratchpad>
"""
    
    def parse_cot_response(self, content):
        """Parse CoT response to extract scratchpad and final response."""
        try:
            if '<scratchpad>' in content and '</scratchpad>' in content:
                start = content.find('<scratchpad>') + len('<scratchpad>')
                end = content.find('</scratchpad>')
                scratchpad = content[start:end].strip()
                final_response = content[end + len('</scratchpad>'):].strip()
                return scratchpad, final_response
            else:
                return "", content.strip()
        except:
            return "", content.strip()
    
    def run_single_dialogue(self, dialogue, experiment_type):
        """Run single dialogue through one experiment type."""
        conversation_history, student_claim = self.format_conversation(dialogue)
        
        if experiment_type == 'zero_shot':
            prompt = self.create_zero_shot_prompt(conversation_history, student_claim)
        elif experiment_type == 'few_shot':
            prompt = self.create_few_shot_prompt(conversation_history, student_claim)
        elif experiment_type == 'cot':
            prompt = self.create_cot_prompt(conversation_history, student_claim)
        
        dialogue_results = {
            'test_id': dialogue.get('test_id'),
            'math_level': dialogue.get('math_level'),
            'expected_result': dialogue.get('expected_result'),
            'conversation_history': conversation_history,
            'student_claim': student_claim,
            'experiment': experiment_type
        }
        
        for model_key in MODELS.keys():
            print(f"  �� {MODELS[model_key]['name']}...")
            
            response = self.make_api_request(model_key, prompt)
            
            if response['success']:
                print(f"    ✅ Success (${response['cost']:.4f})")
                self.total_cost += response['cost']
                
                if experiment_type == 'cot':
                    scratchpad, final_response = self.parse_cot_response(response['content'])
                    dialogue_results[f'{experiment_type}_{model_key}_scratchpad'] = scratchpad
                    dialogue_results[f'{experiment_type}_{model_key}_final'] = final_response
                
                dialogue_results[f'{experiment_type}_{model_key}_response'] = response['content']
                dialogue_results[f'{experiment_type}_{model_key}_cost'] = response['cost']
            else:
                print(f"    ❌ Failed: {response.get('error', 'Unknown error')}")
                dialogue_results[f'{experiment_type}_{model_key}_response'] = f"ERROR: {response.get('error')}"
                dialogue_results[f'{experiment_type}_{model_key}_cost'] = 0.0
        
        return dialogue_results
    
    def run_complete_experiment(self):
        """Run all three experiments."""
        print("🚀 COMPLETE AI TUTORING EXPERIMENT")
        print("=" * 50)
        
        # Load sample data
        try:
            with open('../comta_evaluation_sample.json', 'r') as f:
                dialogues = json.load(f)
            print(f"✅ Loaded {len(dialogues)} dialogues")
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return
        
        # Test API
        print("\n🔧 Testing API connectivity...")
        test_response = self.make_api_request('gpt4o_mini', "Hello! Say 'Test successful.'")
        if not test_response['success']:
            print(f"❌ API test failed: {test_response.get('error')}")
            return
        print(f"✅ API working (${test_response['cost']:.4f})")
        
        # Estimate cost
        estimated_cost = len(dialogues) * len(MODELS) * 3 * 0.002
        print(f"📊 Estimated total cost: ~${estimated_cost:.2f}")
        
        proceed = input("\nProceed with full experiment? (y/n): ").lower().strip()
        if proceed != 'y':
            print("Experiment cancelled.")
            return
        
        # Run experiments
        print(f"\n🎬 Starting experiments...")
        
        all_results = {}
        
        for experiment in ['zero_shot', 'few_shot', 'cot']:
            print(f"\n{'='*60}")
            print(f"📝 EXPERIMENT: {experiment.upper().replace('_', '-')}")
            print(f"{'='*60}")
            
            for i, dialogue in enumerate(dialogues, 1):
                print(f"\nDialogue {i}/{len(dialogues)} (ID: {dialogue.get('test_id')})")
                
                result = self.run_single_dialogue(dialogue, experiment)
                
                # Store result
                dialogue_id = str(dialogue.get('test_id'))
                if dialogue_id not in all_results:
                    all_results[dialogue_id] = result
                else:
                    all_results[dialogue_id].update(result)
        
        # Export results
        self.export_results(all_results)
        
        print(f"\n💰 TOTAL COST: ${self.total_cost:.4f}")
        print(f"🎉 EXPERIMENT COMPLETE!")
    
    def export_results(self, results):
        """Export results to CSV."""
        print(f"\n📊 Exporting results...")
        
        filename = f"tutoring_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        if not results:
            print("No results to export")
            return
        
        # Get all fieldnames
        fieldnames = set()
        for result in results.values():
            fieldnames.update(result.keys())
        fieldnames = sorted(list(fieldnames))
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Add evaluation criteria row
            criteria_row = {field: '' for field in fieldnames}
            criteria_row['test_id'] = 'EVALUATION_CRITERIA'
            criteria_row['math_level'] = 'Rate each response 1-5:'
            criteria_row['expected_result'] = '1) Mistake Diagnosis, 2) Teaching Strategy'
            criteria_row['conversation_history'] = '3) Feedback Quality, 4) Clarity'
            criteria_row['student_claim'] = '5) Support & Encouragement'
            writer.writerow(criteria_row)
            
            # Add data
            for result in results.values():
                writer.writerow(result)
        
        print(f"✅ Results exported to {filename}")
        print(f"📋 {len(results)} dialogues exported")
        
        return filename

if __name__ == "__main__":
    runner = ExperimentRunner()
    runner.run_complete_experiment()
