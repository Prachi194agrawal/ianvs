#!/usr/bin/env python3
"""
Generate benchmark results CSV from existing cache.json
This bypasses the full benchmark run and directly creates results.
"""
import json
import csv
from datetime import datetime
from pathlib import Path

# Paths
CACHE_FILE = Path("/home/prachi/ianvs/workspace-gpqa/benchmarkingjob/query-routing/cache.json")
OUTPUT_DIR = Path("/home/prachi/ianvs/workspace-gpqa/benchmarkingjob/rank")
OUTPUT_FILE = OUTPUT_DIR / "all_rank_from_cache.csv"

def calculate_metrics_from_cache():
    """Load cache and calculate metrics"""
    print(f"Loading cache from: {CACHE_FILE}")
    
    with open(CACHE_FILE, 'r') as f:
        cache_data = json.load(f)
    
    print(f"Found {len(cache_data)} configurations in cache")
    
    results = []
    
    for idx, config_data in enumerate(cache_data, 1):
        config = config_data.get('config', {})
        test_results = config_data.get('result', [])
        
        if not test_results:
            continue
            
        # Calculate metrics
        total_samples = len(test_results)
        correct = sum(1 for r in test_results if r.get('prediction') == r.get('gold'))
        accuracy = (correct / total_samples * 100) if total_samples > 0 else 0
        
        # Determine if this is edge or cloud based on model/backend
        model_name = config.get('model', '')
        backend = config.get('backend', '')
        api_provider = config.get('api_provider', '')
        
        is_cloud = ('api' in backend.lower() or api_provider or 
                   'gpt' in model_name.lower() or 'llama-3' in model_name.lower())
        
        # Token counts - assign to edge or cloud
        prompt_tokens = sum(r.get('response', {}).get('usage', {}).get('prompt_tokens', 0) for r in test_results)
        completion_tokens = sum(r.get('response', {}).get('usage', {}).get('completion_tokens', 0) for r in test_results)
        
        if is_cloud:
            cloud_prompt_tokens = prompt_tokens
            cloud_completion_tokens = completion_tokens
            edge_prompt_tokens = 0
            edge_completion_tokens = 0
            edge_ratio = 0.0
        else:
            cloud_prompt_tokens = 0
            cloud_completion_tokens = 0
            edge_prompt_tokens = prompt_tokens
            edge_completion_tokens = completion_tokens
            edge_ratio = 100.0
        
        # Performance metrics
        ttft_list = [r.get('response', {}).get('perf', {}).get('time_to_first_token', 0) for r in test_results]
        throughput_list = [r.get('response', {}).get('perf', {}).get('throughput', 0) for r in test_results]
        latency_list = [r.get('response', {}).get('perf', {}).get('internal_token_latency', 0) for r in test_results]
        
        avg_ttft = sum(ttft_list) / len(ttft_list) if ttft_list else 0
        avg_throughput = sum(throughput_list) / len(throughput_list) if throughput_list else 0
        avg_latency = sum(latency_list) / len(latency_list) if latency_list else 0
        
        result = {
            'rank': idx,
            'algorithm': 'query-routing',
            'accuracy': round(accuracy, 2),
            'edge_ratio': edge_ratio,
            'ttft': round(avg_ttft, 3),
            'throughput': round(avg_throughput, 2),
            'latency': round(avg_latency, 3),
            'cloud_prompt_tokens': cloud_prompt_tokens,
            'cloud_completion_tokens': cloud_completion_tokens,
            'edge_prompt_tokens': edge_prompt_tokens,
            'edge_completion_tokens': edge_completion_tokens,
            'paradigm': 'jointinference',
            'hard_example_mining': 'CloudOnly' if is_cloud else 'OracleRouter',
            'edgemodel': model_name if not is_cloud else 'N/A',
            'edgemodel_backend': backend if not is_cloud else 'N/A',
            'cloudmodel': model_name if is_cloud else 'groq/llama-3.3-70b',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'cache_file': str(CACHE_FILE)
        }
        
        results.append(result)
        model_type = "Cloud" if is_cloud else "Edge"
        print(f"Config {idx} [{model_type}]: {backend or api_provider or model_name} - Accuracy: {accuracy:.2f}%, Samples: {total_samples}")
    
    return results

def write_csv(results):
    """Write results to CSV"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    fieldnames = [
        'rank', 'algorithm', 'accuracy', 'edge_ratio', 'ttft', 'throughput', 'latency',
        'cloud_prompt_tokens', 'cloud_completion_tokens', 'edge_prompt_tokens', 'edge_completion_tokens',
        'paradigm', 'hard_example_mining', 'edgemodel', 'edgemodel_backend', 'cloudmodel',
        'timestamp', 'cache_file'
    ]
    
    with open(OUTPUT_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n✓ Results saved to: {OUTPUT_FILE}")
    print(f"✓ Total configurations: {len(results)}")

if __name__ == "__main__":
    print("="*60)
    print("Generating Results from Cache")
    print("="*60)
    
    results = calculate_metrics_from_cache()
    write_csv(results)
    
    print("\nDone!")
