import os

# Path to the dataset loader
file_path = "/home/prachi/ianvs/venv/lib/python3.12/site-packages/core/testenvmanager/dataset/dataset.py"

print(f"Applying V5 Patch (Kaggle Compatibility) to: {file_path}...")

# The Robust Code Block
# 1. Reads JSONL line-by-line.
# 2. Extracts 'question' string for X (Fixes unhashable dict error).
# 3. Extracts 'correct_answer' string for Y (Fixes NoneType error).
new_block = """        elif data_format == DatasetFormat.JSONL.value:
            # [PATCH V5] Fix for Kaggle GPQA Dataset
            import json
            class SimpleData:
                def __init__(self):
                    self.x = []
                    self.y = []
            
            data = SimpleData()
            
            if os.path.exists(file):
                with open(file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            try:
                                item = json.loads(line)
                                # Extract string fields safely
                                # GPQA usually uses 'Question' or 'question'
                                q_text = item.get('Question') or item.get('question') or item.get('prompt') or str(item)
                                a_text = item.get('Correct Answer') or item.get('correct_answer') or item.get('response') or ""
                                
                                data.x.append(q_text)
                                data.y.append(a_text)
                            except:
                                pass

            # Apply processor if available
            processor = locals().get('feature_process', locals().get('func'))
            if processor:
                data.x = processor(data.x)"""

with open(file_path, 'r') as f:
    lines = f.readlines()

output_lines = []
skip = False
patched = False

for line in lines:
    # Find start of JSONL block
    if "elif data_format == DatasetFormat.JSONL.value:" in line:
        output_lines.append(new_block + "\n")
        skip = True
        patched = True
    # Find start of NEXT block (to stop skipping)
    elif skip and ("if data_format ==" in line or "elif data_format ==" in line):
        skip = False
        output_lines.append(line)
    # Heuristic to detect end of the indented block
    elif skip and len(line.strip()) > 0 and not line.startswith("            "):
         if "elif" in line or "else" in line or "return" in line:
             skip = False
             output_lines.append(line)
    elif not skip:
        output_lines.append(line)

if patched:
    with open(file_path, 'w') as f:
        f.writelines(output_lines)
    print("SUCCESS: dataset.py patched to read Kaggle GPQA strings correctly.")
else:
    print("WARNING: Could not find the JSONL block. Please reset the file.")
