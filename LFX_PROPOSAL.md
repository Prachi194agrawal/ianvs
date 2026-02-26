# LFX Mentorship 2026 Term 1 - Pre-Test Submission
## CNCF - KubeEdge / Ianvs: Cloud-Edge Simulation Benchmark for LLM Speculative Decoding

**Candidate Name:** [Your Name]  
**Email:** [Your Email]  
**GitHub:** [Your GitHub Username]  
**Date:** February 13, 2026

---

# Task 1: Mini Proposal

## 1. Problem Statement (Understanding)

### Why Speculative Decoding Speedups Are Not Guaranteed in Cloud-Edge Collaboration

Speculative decoding accelerates LLM inference by using a lightweight draft model to propose multiple candidate tokens in parallel, which are then verified by a larger target model. In a single-host setup, this can provide significant speedups (1.5-3x) because:
- Draft tokens are generated quickly by a small model
- Verification is batched and efficient
- All communication is in-memory with minimal latency

However, in **cloud-edge collaborative scenarios**, these speedups are not guaranteed due to:

1. **Network Latency Overhead**: Each draft-verify cycle requires network round-trips (RTT). If RTT >> draft generation time, the network becomes the bottleneck, negating speedup gains.

2. **Bandwidth Constraints**: Transferring draft tokens, logits, and KV caches between edge and cloud consumes bandwidth. Limited bandwidth can create queuing delays, especially with large draft sizes (K).

3. **Heterogeneous Compute Imbalance**: If the edge device is too slow relative to cloud compute, draft generation may not keep up with verification, creating idle time on cloud GPUs.

4. **Network Jitter and Packet Loss**: Variable latency and retransmissions can make end-to-end latency unpredictable, making speculative decoding less effective than deterministic sequential decoding.

5. **Acceptance Rate Variability**: Lower acceptance rates under network delays may force more verification cycles, amplifying network overhead and reducing overall throughput.

### How Network Latency/Bandwidth and Heterogeneous Compute Change End-to-End Gains

- **High RTT (>50ms)**: Network wait time dominates, reducing tokens/s from theoretical 2-3x speedup to potentially <1x (worse than baseline).
- **Limited Bandwidth (<10 Mbps)**: Large draft payloads (logits, hidden states) get queued, increasing TTFT and E2E latency.
- **Slow Edge Device**: If draft generation takes 100ms but cloud verification takes 20ms, cloud is underutilized, and overall pipeline efficiency drops.
- **Concurrency Effects**: Multiple concurrent requests can amplify bandwidth saturation and increase queueing delays, making speculative decoding less practical.

**Key Insight**: Speculative decoding must be evaluated under realistic cloud-edge constraints to determine when it provides actual gains versus when baseline decoding is more efficient.

---

## 2. Benchmark Scope (What to Evaluate)

The benchmark must cover the following key variables:

### Core Variables (Required)

1. **Network Round-Trip Time (RTT)**
   - Range: 5ms, 20ms, 50ms, 100ms, 200ms
   - Models typical edge-cloud distances (same datacenter, regional, cross-region)
   - Critical for understanding network-bounded vs compute-bounded regimes

2. **Network Bandwidth**
   - Range: 1 Mbps, 10 Mbps, 50 Mbps, 100 Mbps, 1 Gbps
   - Models different edge connectivity scenarios (cellular, WiFi, fiber)
   - Affects payload transfer time and queuing

3. **Draft Size (K)**
   - Range: K = 1, 4, 8, 16, 32
   - Larger K increases potential speedup but also network payload and rejection risk
   - Critical trade-off parameter

4. **Heterogeneous Compute Ratio**
   - Draft model size: 0.5B, 1.5B, 3B parameters
   - Verify model size: 7B, 13B, 70B parameters
   - Draft/verify compute time ratio affects pipeline efficiency

### Additional Variables (Recommended)

5. **Prompt Length**
   - Range: 50, 200, 500, 1000 tokens
   - Affects KV cache size and initial processing time

6. **Generation Length**
   - Range: 50, 100, 200, 500 tokens
   - Longer sequences amplify network overhead effects

7. **Concurrency Level**
   - Requests: 1, 2, 4, 8, 16
   - Tests queuing behavior and resource contention

8. **Network Jitter**
   - Std dev: 0%, 10%, 30% of mean RTT
   - Models real-world network variability

---

## 3. Metrics & Methodology (How to Measure)

### Primary Metrics

1. **Time to First Token (TTFT)**
   - **Definition**: Time from request submission until first generated token is returned
   - **Timing boundaries**: Start = request enters system; End = first token decoded
   - **Includes**: Prompt processing + first draft cycle + first verification + network RTT
   - **Why important**: Critical for interactive applications (chatbots, assistants)
   - **Reporting**: Mean, p50, p95, p99 across all requests

2. **End-to-End Throughput (tokens/s)**
   - **Definition**: Total output tokens generated per second
   - **Calculation**: `total_output_tokens / (end_time - start_time)`
   - **Timing boundaries**: Start = first request submission; End = last token of last request
   - **Includes**: All draft-verify cycles, network overhead, queuing delays
   - **Excludes**: Warmup requests (first 5% of total)
   - **Why important**: Measures overall system efficiency
   - **Reporting**: Mean, p50, p95 per request; aggregate system throughput

3. **End-to-End Latency (seconds)**
   - **Definition**: Total time to complete one request
   - **Timing boundaries**: Start = request submission; End = final token + EOS
   - **Includes**: TTFT + generation time + all network overhead
   - **Why important**: User-perceived responsiveness
   - **Reporting**: Mean, p50, p95, p99

### Secondary Metrics

4. **Acceptance Rate**
   - **Definition**: Percentage of draft tokens accepted by verify model
   - **Formula**: `accepted_tokens / proposed_draft_tokens`
   - **Why important**: Indicates efficiency of speculative decoding

5. **Network Overhead Ratio**
   - **Definition**: Time spent on network vs compute
   - **Formula**: `total_network_time / total_compute_time`
   - **Why important**: Identifies bottleneck location

6. **Draft Utilization**
   - **Definition**: Percentage of time draft model is actively generating
   - **Formula**: `draft_active_time / total_time`
   - **Why important**: Measures pipeline efficiency

7. **Cloud Utilization**
   - **Definition**: Percentage of time verify model is actively processing
   - **Formula**: `verify_active_time / total_time`
   - **Why important**: Measures resource efficiency

### Timing Methodology

```
Timeline for ONE speculative decoding cycle:
[Start Request] 
    → [Prompt Processing @ Cloud]          (t_prompt)
    → [KV Cache Transfer: Cloud → Edge]    (t_network_down)
    → [Draft Generation @ Edge]            (t_draft)
    → [Draft Transfer: Edge → Cloud]       (t_network_up)
    → [Verification @ Cloud]               (t_verify)
    → [Accept/Reject Decision]
    → [Loop until EOS]
[End Request]

TTFT = t_prompt + t_network_down + t_draft + t_network_up + t_verify(first)
E2E Latency = TTFT + (num_cycles × cycle_time)
Throughput = output_length / E2E_Latency
```

### Reproducibility Controls

- **Fixed random seed** for model sampling (temperature=0 or seed=42)
- **Deterministic tokenization** (no byte fallback)
- **Fixed prompt set** (100 diverse prompts, fixed order)
- **Warmup phase** (5% of requests, excluded from metrics)
- **Model version pinning** (e.g., `meta-llama/Llama-2-7b-hf@sha256:abc123`)
- **Network emulation seed** (fixed jitter pattern)
- **System state logging** (CPU/GPU util, memory, network stats every 1s)

---

## 4. High-level Design (How to Land in Ianvs)

### Ianvs Architecture Mapping

```
Ianvs Structure:
├── benchmarkingjob.yaml          # Job orchestration
├── testenv.yaml                  # Dataset + metrics config
├── algorithm/
│   ├── baseline_decoding.yaml    # Sequential baseline
│   ├── speculative_decoding.yaml # Standard spec decoding
│   └── adaptive_spec_decoding.yaml # Innovative method
└── simulation/
    └── network_config.yaml       # RTT, bandwidth, jitter
```

### Component Design

#### 1. **BenchmarkingJob Configuration**

```yaml
# benchmarkingjob_speculative_decoding.yaml
benchmarkingjob:
  name: "spec-decode-cloud-edge-benchmark"
  workspace: "./workspace-spec-decode"
  
  testenv: "./testenv/llm_inference.yaml"
  
  test_object:
    type: "algorithms"
    algorithms:
      - name: "baseline-decoding"
        url: "./algorithms/baseline_decoding.yaml"
      - name: "speculative-decoding-standard"
        url: "./algorithms/spec_decode_standard.yaml"
      - name: "speculative-decoding-adaptive"
        url: "./algorithms/spec_decode_adaptive.yaml"
  
  simulation:
    network:
      enabled: true
      config: "./simulation/network_profiles.yaml"
  
  rank:
    sort_by: ["TTFT", "Throughput"]
    visualization:
      mode: "selected_only"
      plots:
        - type: "line"
          x: "RTT"
          y: "Throughput"
          group_by: "algorithm"
        - type: "heatmap"
          x: "RTT"
          y: "Bandwidth"
          z: "Throughput"
```

#### 2. **Test Environment Configuration**

```yaml
# testenv/llm_inference.yaml
testenv:
  dataset:
    name: "llm-bench-dataset"
    type: "generation"
    url: "./datasets/prompts/"
    samples: 100
    prompt_lengths: [50, 200, 500]
    generation_lengths: [100]
    
  metrics:
    - name: "TTFT"
      url: "./metrics/ttft.py"
      report: ["mean", "p50", "p95", "p99"]
    
    - name: "Throughput"
      url: "./metrics/throughput.py"
      report: ["mean", "p50", "p95"]
    
    - name: "E2E_Latency"
      url: "./metrics/e2e_latency.py"
      report: ["mean", "p50", "p95", "p99"]
    
    - name: "AcceptanceRate"
      url: "./metrics/acceptance_rate.py"
      report: ["mean"]
```

#### 3. **Algorithm Configuration (Speculative Decoding)**

```yaml
# algorithms/spec_decode_standard.yaml
algorithm:
  paradigm_type: "cloud-edge-collaborative-inference"
  
  modules:
    - type: "edge_model"
      name: "DraftModel"
      url: "./models/draft_model.py"
      hyperparameters:
        model_name: "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        device: "cpu"
        max_tokens: 1024
        temperature: 0.0
    
    - type: "cloud_model"
      name: "VerifyModel"
      url: "./models/verify_model.py"
      hyperparameters:
        model_name: "meta-llama/Llama-2-7b-hf"
        device: "cuda"
        max_tokens: 1024
        temperature: 0.0
    
    - type: "routing"
      name: "SpeculativeRouter"
      url: "./routing/spec_decode_router.py"
      hyperparameters:
        draft_size_K: 8
        max_acceptance_rate: 0.8
        pipeline_mode: "standard"  # standard | adaptive
```

#### 4. **Network Simulation Configuration**

```yaml
# simulation/network_profiles.yaml
network_simulation:
  profiles:
    - name: "local-edge"
      rtt_ms: 5
      bandwidth_mbps: 1000
      jitter_percent: 5
      packet_loss: 0.001
    
    - name: "regional-edge"
      rtt_ms: 50
      bandwidth_mbps: 100
      jitter_percent: 10
      packet_loss: 0.01
    
    - name: "remote-edge"
      rtt_ms: 200
      bandwidth_mbps: 10
      jitter_percent: 30
      packet_loss: 0.05
  
  emulation:
    tool: "tc"  # Linux traffic control
    interface: "lo"  # loopback for single-host
    apply_bidirectional: true
```

### Implementation Components

#### Cloud-Edge Simulation Runner

```python
# core/simulation/cloud_edge_runner.py
class CloudEdgeSimulator:
    def __init__(self, edge_model, cloud_model, network_config):
        self.edge_process = EdgeProcess(edge_model)
        self.cloud_process = CloudProcess(cloud_model)
        self.network = NetworkEmulator(network_config)
    
    def run_inference(self, prompt):
        # Apply network constraints
        with self.network.emulate():
            start_time = time.time()
            
            # Cloud: process prompt
            kv_cache = self.cloud_process.process_prompt(prompt)
            
            # Transfer KV cache to edge
            self.network.transfer(kv_cache, direction="cloud_to_edge")
            
            # Edge: generate draft tokens
            draft_tokens = self.edge_process.generate_draft(kv_cache, K=8)
            
            # Transfer draft to cloud
            self.network.transfer(draft_tokens, direction="edge_to_cloud")
            
            # Cloud: verify and generate
            verified_tokens = self.cloud_process.verify(draft_tokens)
            
            ttft = time.time() - start_time
            
        return verified_tokens, ttft
```

### Reproducibility Configuration Schema

```yaml
# reproducibility_config.yaml
reproducibility:
  random_seed: 42
  deterministic: true
  
  model_versions:
    draft_model: "TinyLlama/TinyLlama-1.1B-Chat-v1.0@sha256:abc123"
    verify_model: "meta-llama/Llama-2-7b-hf@sha256:def456"
  
  dataset:
    fixed_prompts: true
    prompt_file: "./datasets/fixed_prompts_v1.json"
    shuffle: false
  
  sampling:
    temperature: 0.0  # Deterministic
    top_p: 1.0
    top_k: null
  
  warmup:
    enabled: true
    num_requests: 5
    exclude_from_metrics: true
  
  system_logging:
    interval_seconds: 1
    metrics: ["cpu_percent", "gpu_memory", "network_bytes"]
```

---

## 5. Milestones (9–12 Weeks Plan)

### Week 1-2: Milestone 1 - Foundation & Single-Host Simulation

**Deliverables:**
1. Cloud-edge simulation framework integrated into Ianvs
   - Separate edge/cloud processes with IPC
   - Network emulation using Linux `tc` (Traffic Control)
   - Basic logging and metrics collection
2. Baseline decoding implementation
   - Standard sequential generation
   - Metrics: TTFT, E2E latency, throughput
3. Standard speculative decoding implementation
   - Draft generation (edge) + verification (cloud)
   - Configurable draft size K

**Acceptance Criteria:**
- ✅ Two processes can communicate with simulated RTT (5ms, 50ms, 200ms)
- ✅ Baseline decoding produces correct outputs with measured metrics
- ✅ Speculative decoding achieves >1.5x speedup at 5ms RTT
- ✅ All code passes unit tests (>80% coverage)
- ✅ Configuration files validate against schema

---

### Week 3-5: Milestone 2 - Comprehensive Benchmark Suite

**Deliverables:**
1. Full parameter sweep implementation
   - RTT: 5, 20, 50, 100, 200ms
   - Bandwidth: 1, 10, 50, 100, 1000 Mbps
   - Draft size K: 1, 4, 8, 16, 32
   - Network jitter: 0%, 10%, 30%
2. Advanced metrics module
   - Acceptance rate calculation
   - Network overhead ratio
   - Draft/cloud utilization
   - P50/P95/P99 latency percentiles
3. Reproducibility controls
   - Fixed seed, deterministic sampling
   - Prompt dataset (100 diverse samples)
   - Model version pinning

**Acceptance Criteria:**
- ✅ Benchmark completes 5×5×5 = 125 configurations in <24 hours
- ✅ All metrics collected with <1% measurement error
- ✅ Results reproduce within 5% variance across 3 runs
- ✅ Outlier detection and handling (flag runs with >2σ deviation)
- ✅ Logs include all system stats (CPU, GPU, network)

---

### Week 6-8: Milestone 3 - Innovative Acceleration Method

**Deliverables:**
1. Adaptive speculative decoding implementation (see Section 6)
   - Dynamic draft size adjustment
   - Predictive early exit
   - Batch-aware scheduling
2. Comparative evaluation
   - Baseline vs Standard vs Adaptive across all configs
   - Break-even analysis (when each method wins)
3. Visualization dashboard
   - Interactive plots (RTT vs Throughput, heatmaps)
   - Configuration comparison tool

**Acceptance Criteria:**
- ✅ Adaptive method shows >20% improvement over standard in high-RTT scenarios
- ✅ Evaluation includes statistical significance tests (t-test, p<0.05)
- ✅ Documented trade-offs (when adaptive is worse)
- ✅ Visualization renders all key metrics
- ✅ Code integrated into Ianvs with tests

---

### Week 9-11: Milestone 4 - Documentation & Community Integration

**Deliverables:**
1. Comprehensive documentation
   - Quick start guide (5 min to first run)
   - Configuration reference (all YAML fields)
   - Metrics interpretation guide
   - Troubleshooting FAQ
2. Example configs and results
   - 3 preset scenarios (low/medium/high latency)
   - Pre-generated result reports
3. Community contribution
   - Tutorial blog post
   - Demo video (5-10 min)
   - GitHub issue templates

**Acceptance Criteria:**
- ✅ New user can run benchmark in <30 minutes following docs
- ✅ All config fields documented with examples
- ✅ Tutorial covers 90% of common use cases
- ✅ Code review and PR merged into Ianvs main branch
- ✅ Presentation to KubeEdge SIG AI

---

### Week 12: Milestone 5 - Final Report & Reproducibility Package

**Deliverables:**
1. Final technical report (10-15 pages)
   - Methodology
   - Results analysis
   - Insights and recommendations
   - Future work
2. Reproducibility package
   - Docker image with all dependencies
   - Pre-configured datasets
   - One-command run script
   - Expected outputs for validation
3. Community handoff
   - Maintainer documentation
   - CI/CD integration
   - Issue triage guidelines

**Acceptance Criteria:**
- ✅ Report includes all key findings with statistical rigor
- ✅ Docker image runs on 3 different machines (Linux/macOS)
- ✅ Reproducibility validated by 2 external reviewers
- ✅ Benchmark accepted as official Ianvs example
- ✅ At least 2 community members trained on maintenance

---

## 6. Innovative Acceleration Idea: Adaptive Hybrid Speculative Decoding (AHSD)

### Mechanism (What)

**Adaptive Hybrid Speculative Decoding (AHSD)** dynamically adjusts the speculative decoding strategy based on real-time network conditions and model performance. Unlike standard speculative decoding with fixed draft size K, AHSD incorporates:

1. **Dynamic Draft Size Adjustment**
   - Monitor network RTT and bandwidth in real-time
   - Adjust K based on: `K_optimal = f(RTT, bandwidth, acceptance_rate)`
   - When RTT is high, reduce K to minimize network overhead
   - When RTT is low, increase K to maximize speculation

2. **Predictive Early Exit**
   - Train a lightweight predictor (MLP, 10K params) to estimate acceptance probability for each draft position
   - Formula: `P(accept_i) = predictor(draft_token_i, context_embedding, confidence_score)`
   - Skip verification of low-confidence drafts (P < threshold)
   - Only transfer high-confidence tokens to cloud

3. **Batch-Aware Pipelining**
   - When multiple requests are queued, batch draft tokens for single verification call
   - Amortize network RTT across multiple requests
   - Cloud processes batch in parallel using dynamic batching

4. **Hybrid Fallback Mode**
   - If network RTT > threshold (e.g., 100ms), fall back to cloud-only baseline
   - If acceptance rate < threshold (e.g., 0.3), fall back to baseline
   - Dynamic mode switching based on running average (window=10 requests)

### Algorithm Pseudocode

```python
class AdaptiveHybridSpeculativeDecoding:
    def __init__(self, edge_model, cloud_model, network_monitor):
        self.edge = edge_model
        self.cloud = cloud_model
        self.network = network_monitor
        self.predictor = ConfidencePredictor()  # Trained offline
        self.acceptance_history = deque(maxlen=10)
        
    def generate(self, prompt):
        # Step 1: Decide strategy based on network conditions
        rtt = self.network.get_current_rtt()
        bandwidth = self.network.get_current_bandwidth()
        avg_acceptance = np.mean(self.acceptance_history) if self.acceptance_history else 0.8
        
        # Adaptive threshold: high RTT or low acceptance → fallback
        if rtt > 100 or avg_acceptance < 0.3:
            return self.cloud_only_baseline(prompt)
        
        # Step 2: Adaptive draft size
        K = self.compute_optimal_k(rtt, bandwidth, avg_acceptance)
        # Formula: K = max(1, min(32, base_k * (50/rtt) * acceptance_rate))
        # Example: RTT=5ms, base_k=16 → K=160 (capped at 32)
        #          RTT=100ms, base_k=16 → K=8
        
        # Step 3: Generate draft with early exit
        draft_tokens, confidences = self.edge.generate_with_confidence(prompt, K)
        
        # Step 4: Predictive early exit
        high_conf_tokens = [
            token for token, conf in zip(draft_tokens, confidences)
            if self.predictor.predict(token, context, conf) > 0.7
        ]
        
        if len(high_conf_tokens) == 0:
            return self.cloud_only_baseline(prompt)  # Safety fallback
        
        # Step 5: Transfer only high-confidence tokens (reduced payload)
        self.network.transfer(high_conf_tokens, direction="edge_to_cloud")
        
        # Step 6: Verification
        accepted, rejected = self.cloud.verify(high_conf_tokens)
        
        # Step 7: Update history
        acceptance_rate = len(accepted) / len(high_conf_tokens)
        self.acceptance_history.append(acceptance_rate)
        
        return accepted
    
    def compute_optimal_k(self, rtt, bandwidth, acceptance_rate):
        # Heuristic: K inversely proportional to RTT, proportional to acceptance
        base_k = 16
        rtt_factor = min(50 / max(rtt, 1), 3.0)  # Cap at 3x
        acceptance_factor = max(acceptance_rate, 0.3)  # Floor at 0.3
        bandwidth_factor = min(bandwidth / 10, 2.0)  # Cap at 2x for >100Mbps
        
        optimal_k = int(base_k * rtt_factor * acceptance_factor * bandwidth_factor)
        return max(1, min(optimal_k, 32))  # Clamp to [1, 32]
```

---

### Why It Helps in Cloud-Edge (Why)

#### Connection to Cloud-Edge Constraints

**1. Network RTT / Bandwidth Constraint**
- **Problem**: Fixed-K speculative decoding wastes network bandwidth when RTT is high (e.g., 200ms). Transferring 32 tokens costs 200ms × payload_size, negating speedup.
- **AHSD Solution**: Dynamic K adjustment reduces draft size when RTT increases.
  - At RTT=5ms: K=32 (maximize speculation)
  - At RTT=100ms: K=4 (minimize network overhead)
- **Expected gain**: 30-50% reduction in E2E latency at high RTT scenarios

**2. Heterogeneous Compute Constraint**
- **Problem**: If edge is slow (e.g., mobile CPU), generating large draft (K=32) may take longer than cloud verification, creating idle time.
- **AHSD Solution**: Adjust K based on draft generation speed vs network RTT.
  - If `t_draft(K) > RTT`: reduce K until `t_draft ≈ RTT` (pipeline balance)
- **Expected gain**: 20-30% improvement in cloud GPU utilization

**3. Network Jitter / Packet Loss**
- **Problem**: Variable RTT makes fixed-K strategies unpredictable. High jitter can cause timeouts.
- **AHSD Solution**: Running average of RTT (10-request window) smooths out spikes.
  - Hybrid fallback mode switches to cloud-only when jitter is extreme
- **Expected gain**: 15-25% reduction in p95/p99 latency variance

**4. Concurrency / Queuing**
- **Problem**: Multiple concurrent requests saturate bandwidth, causing queuing delays.
- **AHSD Solution**: Batch-aware pipelining amortizes RTT across requests.
  - Collect 4-8 draft sequences, send in one batch, verify in parallel
- **Expected gain**: 40-60% improvement in aggregate throughput under high concurrency

**5. Low Acceptance Rate Scenarios**
- **Problem**: When draft model quality is poor (acceptance <30%), standard speculative decoding makes many wasted network trips.
- **AHSD Solution**: Predictive early exit skips low-confidence drafts.
  - Only send tokens with P(accept) > 0.7, reducing wasted transfers by 50%
  - Fall back to cloud-only if acceptance drops below threshold
- **Expected gain**: 25-35% reduction in network overhead when draft quality is poor

---

### Trade-offs / Risks

#### What Could Get Worse

1. **Complexity**
   - **Risk**: More code paths (adaptive K, early exit, fallback) increase bugs and maintenance burden
   - **Mitigation**: Extensive testing, gradual rollout, fallback to standard mode on errors

2. **Predictor Training Overhead**
   - **Risk**: Confidence predictor needs training data and may not generalize across models/domains
   - **Mitigation**: Train on diverse dataset, validate on held-out set, provide pre-trained weights

3. **Latency for Small K**
   - **Risk**: When K is reduced to 1-2, overhead of adaptive logic may exceed gains
   - **Mitigation**: Add fast path for K=1 (cloud-only equivalent), skip predictor for K<4

4. **Fallback Decision Delays**
   - **Risk**: Monitoring RTT/acceptance every request adds 1-5ms overhead
   - **Mitigation**: Use lightweight async monitoring (separate thread), cache decisions for 100ms

5. **Batch Pipelining Latency**
   - **Risk**: Waiting to batch requests increases TTFT for first request
   - **Mitigation**: Adaptive batching timeout (e.g., max wait 50ms), single-request fast path

6. **Determinism / Reproducibility**
   - **Risk**: Adaptive strategies make results non-deterministic (K varies by run)
   - **Mitigation**: Log all adaptive decisions, provide fixed-K mode for reproducibility testing

7. **Acceptance Rate Estimation Error**
   - **Risk**: If predictor is miscalibrated, may skip good drafts or send bad drafts
   - **Mitigation**: Conservative threshold (P>0.7), periodic recalibration, ablation study

---

### Evaluation Plan (How to Verify)

#### Baselines

1. **Baseline Decoding**: Sequential cloud-only generation (no speculation)
2. **Standard Speculative Decoding**: Fixed K=8, no adaptation
3. **AHSD (Proposed)**: Adaptive K, early exit, batch pipelining

#### Experimental Variables

**Independent Variables** (factors we control):
- RTT: [5ms, 20ms, 50ms, 100ms, 200ms]
- Bandwidth: [1Mbps, 10Mbps, 50Mbps, 100Mbps, 1Gbps]
- Concurrency: [1, 2, 4, 8 requests]
- Prompt length: [50, 200, 500 tokens]
- Generation length: [100 tokens, fixed]

**Fixed Variables**:
- Draft model: TinyLlama-1.1B
- Verify model: Llama-2-7B
- Dataset: 100 fixed prompts from GPQA
- Temperature: 0 (deterministic)
- Hardware: Same machine, same GPU

#### Metrics

**Primary Metrics**:
1. **TTFT (p50, p95)**: Lower is better
2. **E2E Latency (p50, p95)**: Lower is better
3. **Throughput (tokens/s, p50)**: Higher is better

**Secondary Metrics**:
4. Acceptance rate (mean)
5. Network overhead ratio
6. Cloud GPU utilization

#### Hypothesis & Expected "Break-Even" Regions

**Hypothesis:**
- **AHSD wins when**: RTT > 50ms OR concurrency > 2 OR bandwidth < 50Mbps
- **Standard spec wins when**: RTT < 20ms AND bandwidth > 100Mbps AND concurrency = 1
- **Baseline wins when**: Acceptance rate < 30% OR RTT > 200ms

**Expected Performance Regions**:

| RTT | Bandwidth | Best Method | Expected Speedup vs Baseline |
|-----|-----------|-------------|------------------------------|
| 5ms | 1Gbps | Standard Spec | 2.5x |
| 5ms | 10Mbps | AHSD | 2.0x (batch pipelining) |
| 50ms | 1Gbps | AHSD | 1.8x (adaptive K) |
| 50ms | 10Mbps | AHSD | 1.4x (K reduction) |
| 100ms | 100Mbps | AHSD | 1.2x (early exit) |
| 200ms | 10Mbps | Baseline | 1.0x (fallback mode) |

**Statistical Validation**:
- Each config: 5 runs × 100 prompts = 500 samples
- Paired t-test between methods (p < 0.05)
- Cohen's d effect size (report if >0.5)
- Confidence intervals (95%) on all metrics

---

### Ianvs Integration (Minimal Requirements)

#### New Config Fields Required

```yaml
# algorithms/ahsd.yaml
algorithm:
  paradigm_type: "cloud-edge-collaborative-inference"
  
  modules:
    - type: "routing"
      name: "AdaptiveSpeculativeRouter"
      url: "./routing/ahsd.py"
      hyperparameters:
        # Adaptive K parameters
        base_draft_size_K: 16
        K_min: 1
        K_max: 32
        rtt_threshold_ms: 100  # Fallback if exceeded
        
        # Early exit parameters
        confidence_threshold: 0.7
        predictor_model_path: "./models/confidence_predictor.pt"
        
        # Fallback parameters
        acceptance_rate_threshold: 0.3
        fallback_mode: "cloud_only"
        
        # Batch pipelining
        batch_enabled: true
        batch_timeout_ms: 50
        batch_max_size: 8
        
        # Monitoring
        monitor_interval_ms: 100
        history_window_size: 10
```

#### New Logging Fields

```python
# logs/ahsd_detailed.json
{
  "request_id": "req_001",
  "timestamp": 1707840000,
  "prompt_length": 200,
  "network_state": {
    "rtt_ms": 45.3,
    "bandwidth_mbps": 85.2,
    "jitter_ms": 5.1
  },
  "adaptive_decisions": {
    "initial_K": 16,
    "adjusted_K": 12,
    "adjustment_reason": "high_rtt",
    "early_exit_tokens_skipped": 3,
    "fallback_triggered": false
  },
  "timing": {
    "ttft_ms": 523.1,
    "e2e_latency_ms": 2341.5,
    "draft_time_ms": 145.2,
    "network_time_ms": 201.3,
    "verify_time_ms": 89.7
  },
  "acceptance": {
    "proposed": 12,
    "accepted": 9,
    "rate": 0.75
  }
}
```

#### Metrics Module Extensions

```python
# metrics/ahsd_metrics.py
class AHSDMetrics:
    def compute(self, logs):
        return {
            "avg_K": np.mean([log["adaptive_decisions"]["adjusted_K"] for log in logs]),
            "K_variance": np.std([log["adaptive_decisions"]["adjusted_K"] for log in logs]),
            "fallback_rate": sum(log["adaptive_decisions"]["fallback_triggered"] for log in logs) / len(logs),
            "early_exit_savings": sum(log["adaptive_decisions"]["early_exit_tokens_skipped"] for log in logs),
            "adaptation_overhead_ms": np.mean([log["timing"]["adaptation_overhead_ms"] for log in logs])
        }
```

---

# Summary of Innovative Idea

**Adaptive Hybrid Speculative Decoding (AHSD)** addresses cloud-edge constraints through:
1. **Dynamic K**: Adapts draft size to network conditions (RTT, bandwidth)
2. **Early Exit**: Skips low-confidence drafts using lightweight predictor
3. **Batch Pipelining**: Amortizes network overhead across concurrent requests
4. **Smart Fallback**: Switches to cloud-only when speculation becomes inefficient

**Key Differentiator**: Unlike static speculation, AHSD continuously adapts to real-time conditions, making it robust to variable network environments typical in edge computing.

**Expected Impact**: 20-50% improvement over standard speculative decoding in high-RTT, low-bandwidth, or high-concurrency scenarios, while maintaining deterministic fallback for reproducibility.

---

