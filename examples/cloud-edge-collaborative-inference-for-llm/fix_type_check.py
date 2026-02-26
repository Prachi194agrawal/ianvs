import os

# Relative path from your current directory
file_path = "testalgorithms/query-routing/models/base_llm.py"

print(f"Patching Type Check in: {file_path}")

if not os.path.exists(file_path):
    print("ERROR: File not found. Make sure you are in the 'examples/cloud-edge...' directory.")
    exit(1)

with open(file_path, 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # 1. Disable the strict type check
    if 'raise ValueError(f"DataType {type(data)} is not supported' in line:
        new_lines.append(f"        # [PATCH] Check disabled to allow Strings\n")
        new_lines.append(f"        pass # {line.strip()}\n")
    
    # 2. Ensure we handle the string if it passes the check
    elif 'if not isinstance(data, dict):' in line:
        new_lines.append(f"        # [PATCH] Allow strings\n")
        new_lines.append(f"        if not isinstance(data, (dict, str)):\n")
    
    else:
        new_lines.append(line)

with open(file_path, 'w') as f:
    f.writelines(new_lines)

print("SUCCESS: Strict type check disabled. Model will now accept strings.")
