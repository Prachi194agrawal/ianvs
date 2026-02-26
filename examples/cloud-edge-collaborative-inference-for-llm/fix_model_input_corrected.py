import os

# FIXED PATH: Relative to your current folder
file_path = "testalgorithms/query-routing/models/base_llm.py"

print(f"Patching: {file_path}")

if not os.path.exists(file_path):
    print(f"ERROR: File still not found at {file_path}. Check your current directory.")
    exit(1)

with open(file_path, 'r') as f:
    lines = f.readlines()

new_lines = []
patched = False
for line in lines:
    new_lines.append(line)
    # Find the start of the inference method
    if "def inference(self, data):" in line:
        # Avoid double-patching if you ran it multiple times
        new_lines.append("        # [PATCH] Handle Dictionary Inputs from Data Processor\n")
        new_lines.append("        if isinstance(data, dict):\n")
        new_lines.append("            data = data.get('query') or data.get('question') or str(data)\n")
        new_lines.append("        # [PATCH] Handle None inputs\n")
        new_lines.append("        if data is None:\n")
        new_lines.append("            data = 'Empty prompt'\n")
        patched = True

with open(file_path, 'w') as f:
    f.writelines(new_lines)

if patched:
    print("SUCCESS: Base LLM patched correctly.")
else:
    print("WARNING: Could not find the function to patch.")
