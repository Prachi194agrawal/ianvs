import os

file_path = "testalgorithms/query-routing/models/base_llm.py"
print(f"Rewriting BaseLLM in: {file_path}")

# Complete, robust BaseLLM class
new_content = """
import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(filename)s(%(lineno)d) [%(levelname)s] - %(message)s')
logger = logging.getLogger(__name__)

class BaseLLM:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.cache_hash = {}
        self.cache_path = os.path.join(os.getcwd(), "cache.json")
        self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "r") as f:
                    self.cache_hash = json.load(f)
            except Exception:
                self.cache_hash = {}

    def _save_cache(self):
        try:
            with open(self.cache_path, "w") as f:
                json.dump(self.cache_hash, f)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")

    def _try_cache(self, question):
        return self.cache_hash.get(question, None)

    def _add_to_cache(self, question, answer):
        self.cache_hash[question] = answer
        self._save_cache()

    def _infer(self, messages):
        raise NotImplementedError("Subclasses must implement _infer")

    def inference(self, data):
        # [PATCH] Robust Input Handling
        if isinstance(data, dict):
            data = data.get('query') or data.get('question') or str(data)
        
        if data is None:
            data = "Empty prompt"
            
        if isinstance(data, str):
            question = data
        else:
            question = str(data)

        # Check cache
        res = self._try_cache(question)
        if res:
            return res
        
        # Inference
        messages = [{"role": "user", "content": question}]
        response = self._infer(messages)
        
        # Update cache
        self._add_to_cache(question, response)
        return response
"""

with open(file_path, 'w') as f:
    f.write(new_content)

print("SUCCESS: BaseLLM rewritten with full caching support.")
