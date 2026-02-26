import os

file_path = "testalgorithms/query-routing/models/huggingface_llm.py"
print(f"Patching missing methods in: {file_path}")

# The missing helper method
method_code = """
    def _format_response(self, outputs, input_length):
        # Decode the generated tokens (skipping the input prompt)
        generated_tokens = outputs[0][input_length:]
        return self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
"""

with open(file_path, 'r') as f:
    content = f.read()

# Check if method already exists
if "_format_response" not in content:
    # Append it to the end of the file (assuming indentation allows it, 
    # but safer to inject it inside the class before _infer or at end of class)
    
    # We'll inject it before "def _infer" to ensure it's inside the class scope
    import re
    match = re.search(r"    def _infer", content)
    if match:
        idx = match.start()
        new_content = content[:idx] + method_code + "\n" + content[idx:]
        
        with open(file_path, 'w') as f:
            f.write(new_content)
        print("SUCCESS: Added _format_response method.")
    else:
        print("WARNING: Could not find anchor to inject method.")
else:
    print("INFO: Method already exists.")
