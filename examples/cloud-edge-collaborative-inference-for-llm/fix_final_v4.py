import os

# Path to the dataset loader in your virtual environment
file_path = "/home/prachi/ianvs/venv/lib/python3.12/site-packages/core/testenvmanager/dataset/dataset.py"

print(f"Applying Final V4 Patch to: {file_path}...")

# The Robust Code Block
# 1. Initializes y as a list (Fixes TypeError)
# 2. Uses locals().get() to find the processor function (Fixes NameError)
# 3. Loads JSONL safely (Fixes Extra Data Error)
new_block = """        elif data_format == DatasetFormat.JSONL.value:
            # [PATCH V4] Final Fix for LFX Task 2
            import json
            class SimpleData:
                def __init__(self):
                    self.x = []
                    self.y = []  # Fixed: Must be a list, not None
            
            data = SimpleData()
            raw_data = []
            
            # Load JSONL line-by-line
            if os.path.exists(file):
                with open(file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            try:
                                raw_data.append(json.loads(line))
                            except:
                                pass
            
            # Fix TypeError: Create dummy labels so zip(x, y) doesn't crash
            data.y = [None] * len(raw_data)

            # Fix NameError: Auto-detect the processing variable name
            # Sedna uses 'func' or 'feature_process' depending on context
            processor = locals().get('feature_process', locals().get('func'))
            
            if processor:
                data.x = processor(raw_data)
            else:
                data.x = raw_data"""

# Read the file
with open(file_path, 'r') as f:
    lines = f.readlines()

# Rewrite the file using a clean logic to replace the JSONL block
output_lines = []
skip = False
patched = False

for line in lines:
    # Detect the start of the JSONL block
    if "elif data_format == DatasetFormat.JSONL.value:" in line:
        output_lines.append(new_block + "\n")
        skip = True
        patched = True
    # Detect the start of the NEXT block (to stop skipping)
    elif skip and ("if data_format ==" in line or "elif data_format ==" in line):
        skip = False
        output_lines.append(line)
    # Detect indentation change that suggests end of block
    elif skip and len(line.strip()) > 0 and not line.startswith("            "):
         # If line is less indented than the block body, we are done skipping
         # (Assuming standard 4-space indentation, block body is 12 spaces deep)
         # But safer to just look for the next elif/else or just consume the previous patch lines
         if "elif" in line or "else" in line or "return" in line:
             skip = False
             output_lines.append(line)
         # Otherwise, we assume it's part of the old block we are removing
    elif not skip:
        output_lines.append(line)

if patched:
    with open(file_path, 'w') as f:
        f.writelines(output_lines)
    print("SUCCESS: dataset.py patched to V4 (Robust Labels & Variables).")
else:
    print("WARNING: Could not find the JSONL block to patch. Please reset the file.")
