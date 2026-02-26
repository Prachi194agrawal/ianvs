#!/usr/bin/env python3
"""
Analyze OracleRouter cache to determine edge vs cloud routing
"""
import json
from pathlib import Path

CACHE_FILE = Path("/home/prachi/ianvs/workspace-gpqa/benchmarkingjob/query-routing/cache.json")

with open(CACHE_FILE, 'r') as f:
    cache_data = json.load(f)

print("="*60)
print("Analyzing OracleRouter Cache (Last Run)")
print("="*60)

# Get the last config with groq (126 samples)
for idx, config_data in enumerate(cache_data, 1):
    config = config_data.get('config', {})
    results = config_data.get('result', [])
    
    if len(results) != 126:
        continue
    
    print(f"\nConfig {idx}: {len(results)} samples")
    print(f"Model: {config.get('model', 'Unknown')}")
    print(f"Backend: {config.get('backend', 'Unknown')}")
    
    # Analyze each result to determine if it's edge or cloud
    # In OracleRouter cache, we need to check if responses came from local model or API
    
    edge_count = 0
    cloud_count = 0
    edge_tokens_prompt = 0
    edge_tokens_completion = 0
    cloud_tokens_prompt = 0
    cloud_tokens_completion = 0
    
    for r in results:
        response = r.get('response', {})
        usage = response.get('usage', {})
        perf = response.get('perf', {})
        
        # Check indicators: Cloud responses typically have different performance characteristics
        # If it has very low latency and high throughput, likely edge
        # If it has API-style metrics, likely cloud
        
        throughput = perf.get('throughput', 0)
        ttft = perf.get('time_to_first_token', 0)
        
        # Heuristic: Edge models (local) have higher throughput (>50 tok/s)
        # Cloud APIs have lower but consistent throughput
        is_edge = throughput > 60  # tokens per second
        
        prompt_tok = usage.get('prompt_tokens', 0)
        completion_tok = usage.get('completion_tokens', 0)
        
        if is_edge:
            edge_count += 1
            edge_tokens_prompt += prompt_tok
            edge_tokens_completion += completion_tok
        else:
            cloud_count += 1
            cloud_tokens_prompt += prompt_tok
            cloud_tokens_completion += completion_tok
    
    total = edge_count + cloud_count
    edge_ratio = (edge_count / total * 100) if total > 0 else 0
    
    print(f"\nRouting Analysis:")
    print(f"  Edge queries: {edge_count} ({edge_ratio:.1f}%)")
    print(f"  Cloud queries: {cloud_count} ({100-edge_ratio:.1f}%)")
    print(f"\nToken Usage:")
    print(f"  Edge: {edge_tokens_prompt:,} prompt + {edge_tokens_completion:,} completion")
    print(f"  Cloud: {cloud_tokens_prompt:,} prompt + {cloud_tokens_completion:,} completion")
    
    # Check accuracy per routing decision
    edge_correct = sum(1 for r in results if r.get('prediction') == r.get('gold') and 
                      r.get('response', {}).get('perf', {}).get('throughput', 0) > 60)
    cloud_correct = sum(1 for r in results if r.get('prediction') == r.get('gold') and 
                       r.get('response', {}).get('perf', {}).get('throughput', 0) <= 60)
    
    edge_acc = (edge_correct / edge_count * 100) if edge_count > 0 else 0
    cloud_acc = (cloud_correct / cloud_count * 100) if cloud_count > 0 else 0
    
    print(f"\nAccuracy by Routing:")
    print(f"  Edge accuracy: {edge_acc:.1f}%")
    print(f"  Cloud accuracy: {cloud_acc:.1f}%")
    print(f"  Overall accuracy: {(edge_correct + cloud_correct)/total*100:.1f}%")

print("\n" + "="*60)
