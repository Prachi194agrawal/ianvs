import os

# Relative path to the model wrapper
file_path = "testalgorithms/query-routing/models/huggingface_llm.py"

print(f"Patching: {file_path}")

if not os.path.exists(file_path):
    print("ERROR: File not found.")
    exit(1)

with open(file_path, 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    new_lines.append(line)
    # Find the __init__ method to ensure tokenizer is set
    if "self.model_name = model_name" in line:
        new_lines.append("        self.tokenizer = None\n")
        new_lines.append("        self.model = None\n")
    
    # Find where the model is loaded and force tokenizer loading
    if "self.model = AutoModelForCausalLM.from_pretrained" in line:
        new_lines.append("        # [PATCH] Explicitly load tokenizer\n")
        new_lines.append("        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)\n")
        new_lines.append("        if not self.tokenizer.pad_token:\n")
        new_lines.append("            self.tokenizer.pad_token = self.tokenizer.eos_token\n")

with open(file_path, 'w') as f:
    f.writelines(new_lines)

print("SUCCESS: HuggingfaceLLM patched to ensure tokenizer loads.")
