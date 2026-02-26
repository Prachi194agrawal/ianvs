import os

file_path = "testalgorithms/query-routing/models/base_llm.py"
print(f"Rewriting inference method in: {file_path}")

# The new robust inference method
new_method = """    def inference(self, data):
        # [PATCH] Robust Input Handling for LFX Task 2
        # 1. Unwrap dictionary if needed
        if isinstance(data, dict):
            data = data.get('query') or data.get('question') or str(data)
        
        # 2. Handle None
        if data is None:
            data = "Empty prompt"
            
        # 3. Handle String (Normal case)
        if isinstance(data, str):
            question = data
        else:
            # Fallback for unknown types
            question = str(data)

        # Proceed with caching logic
        res = self._try_cache(question)
        if res:
            return res
        
        # Call actual model inference
        messages = [{"role": "user", "content": question}]
        response = self._infer(messages)
        
        # Cache result
        self._add_to_cache(question, response)
        return response
"""

# Read file
with open(file_path, 'r') as f:
    lines = f.readlines()

output_lines = []
skip = False
patched = False

for line in lines:
    # Detect start of the original inference method
    if "def inference(self, data):" in line:
        output_lines.append(new_method)
        skip = True
        patched = True
    elif skip:
        # We skip lines until we hit the next method definition or end of class
        # Heuristic: Look for unindented or less-indented lines that aren't empty
        if line.strip() and not line.startswith("        ") and not line.startswith("    #") and not line.startswith("    \""):
             # If indentation is 4 spaces (start of new method) or 0 (end of class), stop skipping
             if len(line) - len(line.lstrip()) <= 4:
                 skip = False
                 output_lines.append(line)
    else:
        output_lines.append(line)

if patched:
    with open(file_path, 'w') as f:
        f.writelines(output_lines)
    print("SUCCESS: base_llm.py patched with clean inference method.")
else:
    print("WARNING: Could not find 'def inference(self, data):' to replace.")
