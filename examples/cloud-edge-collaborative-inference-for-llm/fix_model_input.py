import os

# Path to the base model wrapper
file_path = "examples/cloud-edge-collaborative-inference-for-llm/testalgorithms/query-routing/models/base_llm.py"

print(f"Patching: {file_path}")

# We need to modify the inference method to handle dicts
with open(file_path, 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    new_lines.append(line)
    # Find the start of the inference method
    if "def inference(self, data):" in line:
        # Inject code to unwrap dictionary data
        new_lines.append("        # [PATCH] Handle Dictionary Inputs from Data Processor\n")
        new_lines.append("        if isinstance(data, dict):\n")
        new_lines.append("            data = data.get('query') or data.get('question') or str(data)\n")
        new_lines.append("        # [PATCH] Handle None inputs\n")
        new_lines.append("        if data is None:\n")
        new_lines.append("            data = 'Empty prompt'\n")

with open(file_path, 'w') as f:
    f.writelines(new_lines)

print("SUCCESS: Base LLM patched to handle dictionary inputs.")
