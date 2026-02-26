# Ianvs Setup Complete ✓

## Installation Summary

Successfully set up the ianvs benchmarking framework on your local Linux system.

### What was installed:

1. **Ianvs v0.1.0** - Cloud-Edge AI Benchmarking Framework
2. **Sedna v0.4.1** - Edge-Cloud Synergy Framework (from GitHub)
3. **All required dependencies** including:
   - colorlog, pyyaml, watchdog
   - websockets, requests, fastapi, pydantic
   - numpy, pandas, scikit-learn, matplotlib
   - minio, uvicorn, tenacity

### Changes made to resolve compatibility issues:

- Fixed sedna import compatibility in `/home/prachi/ianvs/core/testenvmanager/dataset/dataset.py`
  - Created aliases for `JsonlDataParse` and `JSONMetaDataParse` which don't exist in sedna 0.4.1

### How to use:

1. **Activate the virtual environment** (always do this first):
   ```bash
   cd /home/prachi/ianvs
   source venv/bin/activate
   ```

2. **Run benchmarks**:
   ```bash
   cd examples/cloud-edge-collaborative-inference-for-llm
   ianvs -f benchmarkingjob.yaml
   ```

3. **Check version**:
   ```bash
   ianvs --version
   ```

### Important notes for running on local CPU:

Since you're running this on your local Linux machine without a GPU:

1. The cloud-edge-collaborative-inference-for-llm example requires additional dependencies:
   ```bash
   pip install vllm transformers openai accelerate datamodel_code_generator kaggle groq
   ```

2. You'll need to modify configuration files to use smaller models (like TinyLlama) instead of large models.

3. Some examples may require Docker for containerized edge/cloud simulation.

### Next steps:

1. Navigate to the example directory you want to test
2. Review and modify the benchmarkingjob.yaml and testenv.yaml files
3. Run the benchmark with `ianvs -f benchmarkingjob.yaml`

### Repository location:
`/home/prachi/ianvs`

### Virtual environment:
`/home/prachi/ianvs/venv`

---

**Setup completed on:** February 1, 2026
**Python version:** 3.12
**OS:** Linux (dual boot)
