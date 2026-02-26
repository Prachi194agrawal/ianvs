import os
import re

file_path = "testalgorithms/query-routing/models/huggingface_llm.py"
print(f"Patching attributes in: {file_path}")

# Robust initialization with ALL required attributes
new_class_start = """
class HuggingfaceLLM(BaseLLM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model_name = kwargs.get("model", "meta-llama/Llama-2-7b-chat-hf")
        self.device = kwargs.get("device", "cpu")
        
        # [FIX] Initialize ALL generation parameters used in _infer
        self.max_tokens = int(kwargs.get("max_tokens", 1024))
        self.temperature = float(kwargs.get("temperature", 0.7))
        self.top_p = float(kwargs.get("top_p", 0.9))
        self.repetition_penalty = float(kwargs.get("repetition_penalty", 1.0))
        
        self.tokenizer = None
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            print(f"Loading model: {self.model_name} on {self.device}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
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

with open(file_path, 'r') as f:
    content = f.read()

# Find start of class
match = re.search(r"class HuggingfaceLLM.*?:", content)
if match:
    start_idx = match.start()
    # Find start of _infer method (we preserve the rest of the file)
    infer_match = re.search(r"    def _infer", content)
    if infer_match:
        end_idx = infer_match.start()
        
        # Stitch the new init/load methods with the existing _infer method
        new_content = content[:start_idx] + new_class_start + "\n" + content[end_idx:]
        
        with open(file_path, 'w') as f:
            f.write(new_content)
        print("SUCCESS: HuggingfaceLLM patched with repetition_penalty.")
    else:
        print("WARNING: Could not find _infer method anchor.")
else:
    print("WARNING: Could not find class definition.")
