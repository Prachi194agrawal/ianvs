import os

file_path = "testalgorithms/query-routing/models/huggingface_llm.py"
print(f"Rewriting HuggingfaceLLM in: {file_path}")

# Robust class definition
new_class_start = """
class HuggingfaceLLM(BaseLLM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model_name = kwargs.get("model", "meta-llama/Llama-2-7b-chat-hf")
        self.device = kwargs.get("device", "cpu")
        self.tokenizer = None
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            print(f"Loading model: {self.model_name} on {self.device}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Fix padding token if missing
            if not self.tokenizer.pad_token:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32 if self.device == "cpu" else torch.float16,
                low_cpu_mem_usage=True
            ).to(self.device)
            print("Model loaded successfully.")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            raise e
"""

# Read existing file
with open(file_path, 'r') as f:
    content = f.read()

# We will perform a slightly aggressive replacement:
# We'll keep the imports at the top, but replace the class definition start
# Find where "class HuggingfaceLLM" starts
import re
match = re.search(r"class HuggingfaceLLM.*?:", content)
if match:
    start_idx = match.start()
    # Find the end of _load_model method to replace up to there
    # Heuristic: Find "def _infer" which usually comes after
    infer_match = re.search(r"    def _infer", content)
    if infer_match:
        end_idx = infer_match.start()
        
        # reconstruct file
        new_content = content[:start_idx] + new_class_start + "\n" + content[end_idx:]
        
        with open(file_path, 'w') as f:
            f.write(new_content)
        print("SUCCESS: HuggingfaceLLM class rewritten.")
    else:
        print("WARNING: Could not find _infer method anchor.")
else:
    print("WARNING: Could not find HuggingfaceLLM class.")
