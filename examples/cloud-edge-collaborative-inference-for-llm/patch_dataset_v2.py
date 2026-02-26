import os

file_path = "/home/prachi/ianvs/venv/lib/python3.12/site-packages/core/testenvmanager/dataset/dataset.py"

# The V1 patch we applied earlier (which is now in the file)
v1_block = """            data = SimpleData()
            with open(file, 'r', encoding='utf-8') as f:
                data.x = [json.loads(line) for line in f if line.strip()]"""

# The V2 patch (Adds the missing 'func' application)
v2_block = """            data = SimpleData()
            with open(file, 'r', encoding='utf-8') as f:
                raw_data = [json.loads(line) for line in f if line.strip()]
            
            # [PATCH V2] Apply the feature_process func to format data for LLM
            if func:
                data.x = func(raw_data)
            else:
                data.x = raw_data"""

with open(file_path, 'r') as f:
    content = f.read()

if v1_block in content:
    # Upgrade V1 to V2
    new_content = content.replace(v1_block, v2_block)
    with open(file_path, 'w') as f:
        f.write(new_content)
    print("SUCCESS: dataset.py upgraded to V2 (Data Processing Enabled).")
elif "Apply the feature_process func" in content:
    print("INFO: File is already patched with V2.")
else:
    print("WARNING: Could not find the V1 patch block. Please reset the file or check content manually.")
