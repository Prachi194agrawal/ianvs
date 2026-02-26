# Task 2A: Reproducible Run Log - Ianvs Cloud-Edge LLM Example

## Environment Information

- **OS**: Linux (Ubuntu-based)
- **Python Version**: Python 3.12
- **CPU**: Not specified (sufficient for testing)
- **GPU**: Not required for this run (using cached results)
- **Virtual Environment**: `/home/prachi/ianvs/venv`

---

## Step-by-Step Commands from Scratch

### 1. Clone Ianvs Repository

```bash
git clone https://github.com/kubeedge/ianvs.git
cd ianvs
```

### 2. Set Up Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install Ianvs core dependencies
pip install -r requirements.txt

# Install cloud-edge LLM example dependencies
pip install -r examples/cloud-edge-collaborative-inference-for-llm/requirements.txt

# Install Sedna (required for dataset loading)
pip install examples/resources/third_party/sedna-0.6.0.1-py3-none-any.whl

# Install Ianvs CLI
python setup.py install
```

### 4. Download and Prepare Dataset

```bash
# Install Kaggle CLI (if not already installed)
pip install kaggle

# Set up Kaggle credentials (download kaggle.json from Kaggle account settings)
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# Download the GPQA dataset (example - adjust as needed)
# Note: GPQA dataset was already present in dataset/gpqa/ folder
```

### 5. Fix Dataset Format Issue

**Critical Bug Found**: The dataset was in JSONL format (JSON Lines), but Sedna expects standard JSON array format.

Created conversion script:

```bash
cat > fix_dataset_format.py << 'EOF'
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
EOF

# Run the conversion script
python fix_dataset_format.py
```

**Output:**
```
Converting test dataset...
✓ Converted 198 records from JSONL to JSON
  Input:  /home/prachi/ianvs/dataset/gpqa/test_data/data.jsonl
  Output: /home/prachi/ianvs/dataset/gpqa/test_data/data.json

Converting train dataset...
✓ Converted 0 records from JSONL to JSON
  Input:  /home/prachi/ianvs/dataset/gpqa/train_data/data.jsonl
  Output: /home/prachi/ianvs/dataset/gpqa/train_data/data.json

✅ Dataset format conversion complete!
```

### 6. Configure API Credentials

The benchmark requires API credentials for the cloud model. Set the appropriate environment variables:

**For GROQ:**
```bash
export GROQ_API_KEY="your_groq_api_key_here"
```

**Or for OpenAI:**
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
export OPENAI_BASE_URL="https://api.openai.com/v1"
```

### 7. Run the Benchmark

```bash
cd examples/cloud-edge-collaborative-inference-for-llm
ianvs -f benchmarkingjob.yaml
```

---

## Evidence of Success

### Dataset Conversion Success
The JSONL to JSON conversion successfully processed 198 test records from the GPQA dataset.

### Initial Run Output
```
[2026-02-10 16:42:48,228] edge_model.py(43) [INFO] - Initializing EdgeModel with kwargs: {'model': 'TinyLlama/TinyLlama-1.1B-Chat-v1.0', 'backend': 'huggingface', ...}
[2026-02-10 16:42:48,229] cloud_model.py(34) [INFO] - Initializing CloudModel with kwargs: {'api_provider': 'groq', 'model': 'llama-3.1-8b-instant', ...}
```

The benchmark successfully:
- Loaded the configuration files
- Initialized the Edge Model (TinyLlama)
- Attempted to initialize the Cloud Model (requires API key)

---

## Adjustments Made

### 1. Virtual Environment
- Used system Python virtual environment instead of conda
- Path: `/home/prachi/ianvs/venv`

### 2. Dataset Format Fix
- **Problem**: Dataset files were in JSONL format (one JSON object per line)
- **Solution**: Created conversion script to wrap records in JSON array `[]`
- **Impact**: Resolved `json.decoder.JSONDecodeError: Extra data` error

### 3. API Configuration
- The benchmark configuration uses GROQ API by default
- Model: `llama-3.1-8b-instant`
- Requires `GROQ_API_KEY` environment variable
- Can be switched to OpenAI by modifying `testalgorithms/query-routing/test_queryrouting.yaml`

---

## Next Steps for Full Run

To complete the benchmark run, you need to:

1. **Set API Key**:
   ```bash
   export GROQ_API_KEY="your_key_here"
   ```

2. **Re-run Benchmark**:
   ```bash
   ianvs -f benchmarkingjob.yaml
   ```

3. **Expected Output**: 
   - Progress bar showing inference completion
   - Final results table with metrics (Accuracy, Edge Ratio, TTFT, Throughput, etc.)
   - Results saved to `workspace-gpqa/` directory

---

## File Structure

```
/home/prachi/ianvs/
├── core/                          # Ianvs core modules
├── examples/
│   └── cloud-edge-collaborative-inference-for-llm/
│       ├── benchmarkingjob.yaml  # Main config
│       ├── testenv/               # Test environment configs
│       ├── testalgorithms/        # Algorithm implementations
│       └── workspace-gpqa/        # Output directory
├── dataset/
│   └── gpqa/
│       ├── test_data/
│       │   ├── data.json         # Converted (fixed)
│       │   ├── data.jsonl        # Original
│       │   └── metadata.json
│       └── train_data/
│           ├── data.json         # Converted (fixed)
│           └── data.jsonl        # Original
├── fix_dataset_format.py         # Dataset conversion script
├── requirements.txt              # Core dependencies
└── venv/                         # Virtual environment
```

---

## Key Insights

1. **Dataset Format Compatibility**: Sedna/COCO expects JSON arrays, not JSONL format
2. **API Requirements**: Cloud-edge benchmarking requires both edge (local) and cloud (API-based) models
3. **Caching Mechanism**: The example includes result caching to save API costs during repeated runs
4. **Reproducibility**: Temperature set to ~0 (0.0000001) for deterministic results

---

## Conclusion

Successfully set up the Ianvs cloud-edge collaborative inference example, identified and fixed a critical dataset format incompatibility issue, and prepared the environment for benchmarking. The run is blocked only by the requirement for an API key, which is expected for cloud-edge collaborative inference scenarios.
