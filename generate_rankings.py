#!/usr/bin/env python3
"""
Generate ranking CSV files from existing cache.json
Workaround for stuck edge model loading issue
"""

import json
import csv
from datetime import datetime
from pathlib import Path

def calculate_accuracy(results):
    """Calculate accuracy from results"""
    if not results:
        return 0.0
    correct = sum(1 for r in results if r.get('prediction') == r.get('gold'))
    return (correct / len(results)) * 100

def analyze_cache(cache_path):
    """Analyze cache file and extract metrics"""
    with open(cache_path, 'r') as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        print(f"Warning: Expected list, got {type(data)}")
        return None
    
    results = []
    for model_idx, model_cache in enumerate(data):
        if 'result' not in model_cache or 'config' not in model_cache:
            continue
            
        config = model_cache['config']
        test_results = model_cache['result']
        
        # Calculate accuracy
        accuracy = calculate_accuracy(test_results)
        total_samples = len(test_results)
        
        # Calculate average metrics from all results
        total_ttft = 0
        total_throughput = 0
        total_latency = 0
        total_prompt_tokens = 0
        total_completion_tokens = 0
        
        for r in test_results:
            response = r.get('response', {})
            perf = response.get('perf', {})
            usage = response.get('usage', {})
            
            total_ttft += perf.get('time_to_first_token', 0)
            total_throughput += perf.get('throughput', 0)
            total_latency += perf.get('internal_token_latency', 0)
            total_prompt_tokens += usage.get('prompt_tokens', 0)
            total_completion_tokens += usage.get('completion_tokens', 0)
        
        # Calculate averages
        avg_ttft = total_ttft / max(total_samples, 1)
        avg_throughput = total_throughput / max(total_samples, 1)
        avg_latency = total_latency / max(total_samples, 1)
        
        # Determine edge/cloud based on backend
        backend = config.get('backend', '').lower()
        is_edge = backend in ['huggingface', 'vllm', 'eaglespecdec']
        
        # For edge-only: all tokens are edge tokens
        # For cloud-only: all tokens are cloud tokens
        if is_edge:
            edge_prompt = total_prompt_tokens
            edge_completion = total_completion_tokens
            cloud_prompt = 0
            cloud_completion = 0
            edge_ratio = 100.0
        else:
            edge_prompt = 0
            edge_completion = 0
            cloud_prompt = total_prompt_tokens
            cloud_completion = total_completion_tokens
            edge_ratio = 0.0
        
        result = {
            'algorithm': 'query-routing',
            'accuracy': round(accuracy, 2),
            'edge_ratio': round(edge_ratio, 2),
            'ttft': round(avg_ttft, 3),
            'throughput': round(avg_throughput, 2),
            'latency': round(avg_latency, 3),
            'cloud_prompt_tokens': cloud_prompt,
            'cloud_completion_tokens': cloud_completion,
            'edge_prompt_tokens': edge_prompt,
            'edge_completion_tokens': edge_completion,
            'paradigm': 'jointinference',
            'hard_example_mining': 'EdgeOnly' if is_edge else 'CloudOnly',
            'edgemodel': config.get('model', 'Unknown'),
            'edgemodel_backend': config.get('backend', 'Unknown'),
            'cloudmodel': 'Unknown',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'cache_file': str(cache_path)
        }
        results.append(result)
    
    # Sort by accuracy (descending)
    results.sort(key=lambda x: x['accuracy'], reverse=True)
    
    # Add rank
    for idx, result in enumerate(results, 1):
        result['rank'] = idx
    
    return results

def write_ranking_csv(results, output_path):
    """Write results to CSV file"""
    if not results:
        print("No results to write")
        return
    
    fieldnames = [
        'rank', 'algorithm', 'accuracy', 'edge_ratio', 'ttft', 'throughput', 'latency',
        'cloud_prompt_tokens', 'cloud_completion_tokens',
        'edge_prompt_tokens', 'edge_completion_tokens',
        'paradigm', 'hard_example_mining', 'edgemodel', 'edgemodel_backend',
        'cloudmodel', 'timestamp', 'cache_file'
    ]
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"✅ Written {len(results)} results to {output_path}")

def main():
    cache_file = Path("/home/prachi/ianvs/workspace-gpqa/benchmarkingjob/query-routing/cache.json")
    output_dir = Path("/home/prachi/ianvs/workspace-gpqa/benchmarkingjob/rank")
    
    if not cache_file.exists():
        print(f"❌ Cache file not found: {cache_file}")
        return
    
    print(f"📂 Reading cache from: {cache_file}")
    results = analyze_cache(cache_file)
    
    if results:
        print(f"📊 Analyzed {len(results)} configurations")
        print(f"🏆 Best accuracy: {results[0]['accuracy']}% ({results[0]['hard_example_mining']})")
        
        # Write both files
        write_ranking_csv(results, output_dir / "all_rank_2026.csv")
        write_ranking_csv(results, output_dir / "selected_rank_2026.csv")
        
        print("\n✅ Ranking files generated successfully!")
        print(f"📁 Location: {output_dir}")
    else:
        print("❌ No results found in cache")

if __name__ == '__main__':
    main()
