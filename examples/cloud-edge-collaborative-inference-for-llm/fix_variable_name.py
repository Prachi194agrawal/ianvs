import os

file_path = "/home/prachi/ianvs/venv/lib/python3.12/site-packages/core/testenvmanager/dataset/dataset.py"

print(f"Fixing variable name in: {file_path}...")

with open(file_path, 'r') as f:
    content = f.read()

# Replace the incorrect variable 'func' with 'feature_process'
# We only target the specific lines added by our previous patch to avoid breaking other things
if "if func:" in content and "data.x = func(raw_data)" in content:
    new_content = content.replace("if func:", "if feature_process:")
    new_content = new_content.replace("data.x = func(raw_data)", "data.x = feature_process(raw_data)")
    
    with open(file_path, 'w') as f:
        f.write(new_content)
    print("SUCCESS: Replaced 'func' with 'feature_process'.")
else:
    # Fallback: simple string replacement if indentation varies
    new_content = content.replace("if func:", "if feature_process:")
    new_content = new_content.replace("data.x = func(raw_data)", "data.x = feature_process(raw_data)")
    if new_content != content:
        with open(file_path, 'w') as f:
            f.write(new_content)
        print("SUCCESS: Fixed variable name via fallback method.")
    else:
        print("WARNING: Could not find the erroneous code. Check if file is already fixed.")
