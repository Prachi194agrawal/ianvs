#!/usr/bin/env python3
"""
Add 'question' and 'answer' fields to GPQA dataset for Sedna compatibility
"""
import json

def fix_jsonl_fields(input_path, output_path):
    """Add question/answer fields while preserving original fields"""
    with open(input_path, 'r', encoding='utf-8') as infile:
        with open(output_path, 'w', encoding='utf-8') as outfile:
            for line in infile:
                line = line.strip()
                if not line:
                    continue
                    
                data = json.loads(line)
                
                # Add 'question' field (combination of prompt + query)
                data['question'] = data.get('prompt', '') + data.get('query', '')
                
                # Add 'answer' field (from response)
                data['answer'] = data.get('response', '')
                
                outfile.write(json.dumps(data) + '\n')
    
    print(f"✓ Fixed {input_path} -> {output_path}")

# Fix test dataset
fix_jsonl_fields(
    '/home/prachi/ianvs/dataset/gpqa/test_data/data.jsonl',
    '/home/prachi/ianvs/dataset/gpqa/test_data/data_fixed.jsonl'
)

# Fix train dataset (even though it's empty, for completeness)
fix_jsonl_fields(
    '/home/prachi/ianvs/dataset/gpqa/train_data/data.jsonl',
    '/home/prachi/ianvs/dataset/gpqa/train_data/data_fixed.jsonl'
)

print("\n✅ Dataset field names fixed for Sedna compatibility!")
