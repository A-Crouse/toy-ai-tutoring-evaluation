#!/usr/bin/env python3
"""
Quick test of OpenRouter with your API key and models.
"""

import requests
import json
import os

# Your OpenRouter configuration
OPENROUTER_API_KEY = 'REDACTED'
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Your selected models
MODELS = {
    'phi3_mini': {
        'name': 'Phi-3.5-mini',
        'model_id': 'microsoft/phi-3.5-mini-128k-instruct'
    },
    'claude_haiku': {
        'name': 'Claude 3.5 Haiku', 
        'model_id': 'anthropic/claude-3.5-haiku'
    },
    'gpt4o_mini': {
        'name': 'GPT-4o-mini',
        'model_id': 'openai/gpt-4o-mini'
    }
}

def test_openrouter_model(model_key, model_config):
    """Test a single model through OpenRouter."""
    print(f"\n🧪 Testing {model_config['name']}...")
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/tutoring-research",
        "X-Title": "AI Tutoring Research"
    }
    
    data = {
        "model": model_config['model_id'],
        "messages": [{"role": "user", "content": "Hello! Please respond with 'Connection successful for tutoring research.'"}],
        "max_tokens": 50,
        "temperature": 0.0
    }
    
    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # Get usage info
        usage = result.get('usage', {})
        input_tokens = usage.get('prompt_tokens', 0)
        output_tokens = usage.get('completion_tokens', 0)
        
        print(f"✅ {model_config['name']}: SUCCESS")
        print(f"   Response: {content[:50]}...")
        print(f"   Tokens: {input_tokens} in, {output_tokens} out")
        
        return True
        
    except Exception as e:
        print(f"❌ {model_config['name']}: FAILED")
        print(f"   Error: {str(e)}")
        return False

def main():
    """Test all three models."""
    print("🚀 OPENROUTER MODEL TEST")
    print("=" * 50)
    print("Testing your selected fast models for tutoring research...")
    
    results = {}
    
    for model_key, model_config in MODELS.items():
        results[model_key] = test_openrouter_model(model_key, model_config)
    
    # Summary
    print(f"\n📊 TEST RESULTS")
    print("=" * 30)
    successful = sum(results.values())
    total = len(results)
    
    for model_key, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {MODELS[model_key]['name']}")
    
    print(f"\nSuccess Rate: {successful}/{total} models working")
    
    if successful == total:
        print(f"\n🎉 ALL MODELS WORKING!")
        print(f"Ready to run your AI tutoring experiments!")
    elif successful > 0:
        print(f"\n⚠️  {successful} models working, {total-successful} failed")
        print(f"You can proceed with working models")
    else:
        print(f"\n❌ No models working. Check API key or try again")

if __name__ == "__main__":
    main()
