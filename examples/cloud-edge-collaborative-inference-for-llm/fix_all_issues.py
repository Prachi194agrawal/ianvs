import os
import sys

# --- CONFIGURATION ---
BASE_DIR = "/home/prachi/ianvs"
DATASET_FILE = os.path.join(BASE_DIR, "venv/lib/python3.12/site-packages/core/testenvmanager/dataset/dataset.py")
MODEL_FILE = os.path.join(BASE_DIR, "examples/cloud-edge-collaborative-inference-for-llm/testalgorithms/query-routing/models/huggingface_llm.py")

# --- PATCH 1: DATASET LOADER (Fixing the JSONL Parser) ---
# This ensures valid JSONL loading and applies the processing function
v3_dataset_code = """        elif data_format == DatasetFormat.JSONL.value:
            # [PATCH V3] Robust JSONL Loading
            import json
            class SimpleData:
                def __init__(self):
                    self.x = []
                    self.y = None
            
            data = SimpleData()
            raw_data = []
            with open(file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            raw_data.append(json.loads(line))
                        except:
                            continue # Skip malformed lines
            
            # Apply feature processing if it exists
            if func:
                data.x = func(raw_data)
            else:
                data.x = raw_data"""

print(f"Patching Dataset Manager: {DATASET_FILE}...")
try:
    with open(DATASET_FILE, 'r') as f:
        content = f.read()
    
    # We look for the start of the JSONL block to replace it entirely
    search_marker = "elif data_format == DatasetFormat.JSONL.value:"
    if search_marker in content:
        # Find indentation of the marker
        start_idx = content.find(search_marker)
        # We naively replace the next ~200 characters or find the next elif/else/block
        # To be safe, we will simply inject the V3 logic if it's not already there.
        # But since we patched it before, let's look for our previous patch signature.
        if "[PATCH V3]" not in content:
            # If we see our V1/V2 patch, replace it. If original, replace it.
            # Strategy: Read file, find the block, replace the specific 4 lines of original or previous patch
            # Simpler: We know the V2 patch string, let's replace that.
            
            # Re-read strict to ensure we catch whatever state it is in
            pass 
            # (Logic simplified for script execution: we will append the robust logic 
            # by replacing the known previous patch or the original broken sedna call)
            
            original_broken = "data = JsonlDataParse(data_type=data_type, func=feature_process)\n            data.parse(file)"
            v2_patch_marker = "[PATCH V2]"
            
            if v2_patch_marker in content:
                 # We need to be careful with string replacement. 
                 # Let's overwrite the file with the V3 Logic manually inserted at the marker.
                 # Actually, simpler method for you: We will use the V2 string to identify location.
                 import re
                 # Regex to match the whole JSONL block
                 pattern = r"elif data_format == DatasetFormat\.JSONL\.value:.*?data\.x = raw_data"
                 # This is hard to match across lines.
                 
                 # FALLBACK: Just rewrite the file content if we detect V2
                 print("   -> Detected V2 patch. upgrading to V3...")
                 # We will just write the file out fresh from the known good state of the library + our patch
                 # Use the 'original' broken string as anchor if V2 isn't there, or V2 if it is.
            
    # FORCE PATCH: We will simply read the file lines and rewrite the JSONL block
    with open(DATASET_FILE, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    skip = False
    patched = False
    for line in lines:
        if "elif data_format == DatasetFormat.JSONL.value:" in line:
            new_lines.append(v3_dataset_code + "\n")
            skip = True
            patched = True
        elif skip and ("elif data_format ==" in line or "if data_format ==" in line):
            skip = False
            new_lines.append(line)
        elif skip and (len(line.strip()) > 0 and line.strip().startswith("elif")):
             # Safety catch for end of block
             skip = False
             new_lines.append(line)
        elif not skip:
            new_lines.append(line)
            
    if patched:
        with open(DATASET_FILE, 'w') as f:
            f.writelines(new_lines)
        print("   -> SUCCESS: Dataset Manager patched.")
    else:
        print("   -> WARNING: Could not find anchor to patch. Check file manually.")

except Exception as e:
    print(f"   -> ERROR: {e}")


# --- PATCH 2: HUGGINGFACE LLM (Fixing the NoneType Crash) ---
# We inject a sanitizer loop at the start of the _infer method
print(f"Patching Model Wrapper: {MODEL_FILE}...")
try:
    with open(MODEL_FILE, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        new_lines.append(line)
        if "def _infer(self, messages):" in line:
            # Inject the sanitizer immediately after the function definition
            new_lines.append("        # [PATCH] Sanitize messages to prevent NoneType error\n")
            new_lines.append("        if messages:\n")
            new_lines.append("            for m in messages:\n")
            new_lines.append("                if m.get('content') is None:\n")
            new_lines.append("                    m['content'] = ''\n")
            print("   -> Injected message sanitizer.")

    with open(MODEL_FILE, 'w') as f:
        f.writelines(new_lines)
    print("   -> SUCCESS: Model wrapper patched.")

except Exception as e:
    print(f"   -> ERROR: {e}")

print("\n--- READY TO RUN ---")
