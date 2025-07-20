#!/usr/bin/env python3
"""Basic test to verify what we have so far."""

import sys
import os
sys.path.append('shared')

print("🧪 Testing Current Framework")
print("=" * 40)

# Test config
try:
    from config import config, MODELS
    print(f"✅ Config loaded: {len(MODELS)} models")
    for key, model in MODELS.items():
        print(f"   • {model.name}")
    
    missing = config.get_missing_keys()
    print(f"Missing API keys: {missing}")
    
except Exception as e:
    print(f"❌ Config error: {e}")

# Check file structure
print(f"\n📁 Directory structure:")
dirs = ['shared', 'zero_shot_tutoring', 'few_shot_tutoring', 'chain_of_thought_tutoring']
for d in dirs:
    exists = os.path.exists(d)
    print(f"   {'✅' if exists else '❌'} {d}")

print(f"\n📂 Files in shared/:")
if os.path.exists('shared'):
    files = os.listdir('shared')
    for f in files:
        if not f.startswith('__'):
            print(f"   • {f}")

print(f"\n🎯 Framework Status:")
print(f"We have the basic structure and configuration.")
print(f"Need to complete the remaining components for full functionality.")
