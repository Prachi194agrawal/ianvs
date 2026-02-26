#!/usr/bin/env python3
"""
Fix JSONL to JSON format for Sedna/COCO compatibility
Converts JSON Lines format to a proper JSON array
"""
import json
import os

def convert_jsonl_to_json(jsonl_path):
    """Convert JSONL file to JSON array format"""
    if not os.path.exists(jsonl_path):
        print(f"File not found: {jsonl_path}")
        return False
    
    # Read all lines from JSONL file
    data_list = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:  # Skip empty lines
                try:
                    data_list.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Error parsing line: {e}")
                    continue
    
    # Write as proper JSON array
    json_path = jsonl_path.replace('.jsonl', '.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data_list, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Converted {len(data_list)} records from JSONL to JSON")
    print(f"  Input:  {jsonl_path}")
    print(f"  Output: {json_path}")
    return True

# Convert the test dataset
test_data_path = "/home/prachi/ianvs/dataset/gpqa/test_data/data.jsonl"
print("Converting test dataset...")
convert_jsonl_to_json(test_data_path)

# Convert train dataset if it exists
train_data_path = "/home/prachi/ianvs/dataset/gpqa/train_data/data.jsonl"
if os.path.exists(train_data_path):
    print("\nConverting train dataset...")
    convert_jsonl_to_json(train_data_path)

print("\n✅ Dataset format conversion complete!")
