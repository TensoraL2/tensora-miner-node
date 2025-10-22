# 🧠 Tensora Miner Beta - AI Inference System

**Production-ready decentralized AI inference on Tensora L2**

## 🎯 **What This Is:**

A complete AI compute marketplace where:
- **Subnets** post AI inference jobs (ONNX models, LLMs)
- **Miners** execute real AI workloads and earn TORA
- **Validators** verify results and ensure quality
- **Smart contracts** handle payments and disputes on BSC

---

## 🏗️ **Architecture:**

```
┌─────────────── BSC Mainnet (L1) ───────────────┐
│                                                 │
│  SubnetJobs (0x...)    ← Job marketplace       │
│  SubnetRegistry        ← Subnet tracking        │
│  ValidatorRewards      ← Reward distribution    │
│  TORA Token            ← Payment currency       │
│                                                 │
└─────────────────────────────────────────────────┘
                    ▼
┌──────────── Tensora L2 (44444444) ─────────────┐
│                                                 │
│  RPC: https://rpc.tensora.sh                   │
│  Events & transactions                          │
│                                                 │
└─────────────────────────────────────────────────┘
                    ▼
┌───────────── Off-Chain Services ───────────────┐
│                                                 │
│  ┌────────────┐  ┌──────────────┐  ┌─────────┐│
│  │Miner Node  │  │Validator Node│  │Coord    ││
│  │            │  │              │  │         ││
│  │ONNX Runtime│  │Verify Results│  │Matchmake││
│  │vLLM Engine │  │Pay Rewards   │  │Track    ││
│  │            │  │              │  │         ││
│  └────────────┘  └──────────────┘  └─────────┘│
│                                                 │
└─────────────────────────────────────────────────┘
                    ▼
┌──────────── IPFS Storage ─────────────────────┐
│                                                 │
│  Models (ONNX, GGUF)                           │
│  Input Data (images, text, embeddings)         │
│  Output Results (verifiable hashes)            │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 🚀 **Quick Start:**

### **For Miners:**

```bash
# Install
npm install -g @tensora/cli

# Start mining
tensora miner start --engine onnx

# Or for LLMs
tensora miner start --engine vllm --model llama2
```

### **For Subnet Owners:**

```bash
# Post a job
tensora subnet jobs post \
  --subnet 1 \
  --fee 25 \
  --model ipfs://QmModel \
  --input ipfs://QmInput \
  --spec "4cpu,8ram,8vram,gpu"
```

### **For Validators:**

```bash
# Start validator
tensora validator start

# Check pending verifications
tensora validator pending

# Claim rewards
tensora validator claim
```

---

## 🎯 **How It Works:**

### **1. Job Posting:**
- Subnet owner approves TORA
- Calls `SubnetJobs.postJob(spec)` on BSC
- Job broadcast to miners via events

### **2. Job Execution (Miner):**
- Miner node polls for jobs matching their hardware
- Downloads model from IPFS
- Executes inference (ONNX or vLLM)
- Generates Proof of Compute:
  ```
  PoC = sign(resultHash + inputHash + envHash + timestamps)
  ```
- Submits to chain: `submitResult(jobId, resultHash, proof)`

### **3. Verification (Validator):**
- Validator node monitors submitted jobs
- Re-executes 10% of jobs deterministically
- Challenges if result doesn't match
- After challenge window: calls `finalize(jobId)`

### **4. Rewards:**
- 80% → Miner (instant transfer)
- 20% → ValidatorRewards contract (for validators)

---

## 📋 **Integrated With Existing Tensora:**

✅ **SubnetRegistry** (`0x3419dfa79a415a4599b2142d30d73c49692829c6`)
- Jobs are per-subnet
- Subnet owners control parameters

✅ **ValidatorRewards** (`0x404F245E672AE2832851fB0f1F3A3d8a07BaF34D`)
- Validators earn from job verification
- Existing claiming mechanism works

✅ **@tensora/cli** (v1.0.1)
- Extends with `tensora miner` commands
- Uses existing wallet/keystore

✅ **@tensora/subnet-sdk** (v1.0.0)
- Add job management methods
- TypeScript SDK for developers

---

## 🔧 **Components:**

### **Miner Node** (Python + TypeScript)
- `engine/onnx_runtime.py` - ONNX model execution
- `engine/vllm_runtime.py` - LLM inference (vLLM)
- `job_queue.py` - SQLite-backed job queue
- `job_worker.py` - Main execution loop
- `proof_submitter.ts` - Submit to BSC via viem

### **Validator Node** (Python + TypeScript)
- `validator_engine.py` - Deterministic re-execution
- `verifier.py` - Result comparison logic
- `payout_agent.ts` - Call finalize() on BSC

### **Coordinator** (TypeScript/Fastify)
- Job matchmaking
- Miner registry (hardware specs)
- Health monitoring

---

## 🎯 **AI Engines:**

### **ONNX Runtime:**
```python
import onnxruntime as ort
import numpy as np

def run_onnx(model_path, input_data):
    session = ort.InferenceSession(model_path)
    outputs = session.run(None, input_data)
    return outputs
```

### **vLLM:**
```python
from vllm import LLM, SamplingParams

def run_vllm(model_name, prompts):
    llm = LLM(model=model_name, seed=0)
    params = SamplingParams(temperature=0, max_tokens=100)
    outputs = llm.generate(prompts, params)
    return [out.outputs[0].text for out in outputs]
```

---


