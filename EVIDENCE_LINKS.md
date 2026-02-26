# Evidence Links - LFX Mentorship Submission

**Candidate:** Prachi Agrawal  
**Submission Date:** February 15, 2026  
**Project:** CNCF - KubeEdge/Ianvs: Cloud-Edge Simulation Benchmark for LLM Speculative Decoding

---

## 📊 Primary Evidence (Google Drive)

### 1. Cache File (Primary Evidence)
- **File:** cache.json
- **Size:** 15,104 lines (2.5 MB)
- **Content:** Complete benchmark results with all API responses and performance metrics
- **Link:** [View cache.json on Google Drive](https://drive.google.com/file/d/16mus7k2T5d2hB4azM-5gegSsi9Z2EIUv/view?usp=sharing)

**What's Inside:**
- 15,104 lines of formatted JSON data
- Complete API responses from Groq and edge models
- Performance metrics: TTFT, throughput, latency
- Token usage statistics (cloud + edge)
- Prediction vs gold answer comparisons

### 2. Final Ranking Results (February 2026)
- **File:** all_rank_2026.csv
- **Content:** Complete rankings with accuracy, throughput, latency metrics
- **Link:** [View Rankings on Google Drive](https://drive.google.com/file/d/1DokMJehEl7I0M8C5hHUTJa1qTXriMJbh/view?usp=drive_link)

**Ranking Summary:**
```csv
rank,algorithm,accuracy,edge_ratio,ttft,throughput,latency
1,query-routing,40.91,0.0,0.762,66.64,0.016
2,query-routing,27.78,100.0,0.121,110.5,0.009
3,query-routing,27.27,100.0,0.06,46.96,0.021
4,query-routing,24.24,100.0,0.073,38.84,0.026
```

### 3. Issue Document PDF
- **File:** GitHub Issue Document
- **Content:** Complete GitHub issue with reproduction steps and code solution
- **Link:** [View Issue Document on Google Drive](https://drive.google.com/file/d/1DokMJehEl7I0M8C5hHUTJa1qTXriMJbh/view?usp=drive_link)

---

## 📁 Local Files (Repository)

### Submission Documents
1. **SUBMISSION.md** - Main submission summary (includes all links above)
2. **LFX_PROPOSAL.md** - Task 1: Mini Proposal with AHSD innovation
3. **RUNLOG.md** - Task 2A: Reproducible run log with step-by-step commands
4. **GITHUB_ISSUE.md** - Task 2B: Community improvement (checkpointing)
5. **README_SUBMISSION.md** - Navigation guide for reviewers

### Generated Artifacts
1. **cache.json** (Local) - `/home/prachi/ianvs/workspace-gpqa/benchmarkingjob/query-routing/cache.json`
2. **all_rank_2026.csv** (Local) - `/home/prachi/ianvs/workspace-gpqa/benchmarkingjob/rank/all_rank_2026.csv`
3. **checkpoint.json** - Progress checkpoint (142 completed test cases)

---

## 🔗 Quick Access Links

| Item | Type | Link |
|------|------|------|
| Cache File | Google Drive | [cache.json](https://drive.google.com/file/d/16mus7k2T5d2hB4azM-5gegSsi9Z2EIUv/view?usp=sharing) |
| Ranking Results | Google Drive | [all_rank_2026.csv](https://drive.google.com/file/d/1DokMJehEl7I0M8C5hHUTJa1qTXriMJbh/view?usp=drive_link) |
| Issue Document | Google Drive | [GitHub Issue PDF](https://drive.google.com/file/d/1DokMJehEl7I0M8C5hHUTJa1qTXriMJbh/view?usp=drive_link) |
| Ianvs Repository | GitHub | [kubeedge/ianvs](https://github.com/kubeedge/ianvs) |
| Example Used | GitHub | [cloud-edge-collaborative-inference-for-llm](https://github.com/kubeedge/ianvs/tree/main/examples/cloud-edge-collaborative-inference-for-llm) |

---

## ✅ Verification

### Cache File Verification
```bash
# Line count
wc -l /home/prachi/ianvs/workspace-gpqa/benchmarkingjob/query-routing/cache.json
# Output: 15104

# File size
du -h /home/prachi/ianvs/workspace-gpqa/benchmarkingjob/query-routing/cache.json
# Output: ~2.5 MB

# Valid JSON check
python3 -m json.tool cache.json > /dev/null && echo "Valid JSON"
```

### Ranking File Verification
```bash
# Check rankings
head -6 /home/prachi/ianvs/workspace-gpqa/benchmarkingjob/rank/all_rank_2026.csv

# Output:
# rank,algorithm,accuracy,edge_ratio,ttft,throughput,latency,...
# 1,query-routing,40.91,0.0,0.762,66.64,0.016,...
# 2,query-routing,27.78,100.0,0.121,110.5,0.009,...
# 3,query-routing,27.27,100.0,0.06,46.96,0.021,...
# 4,query-routing,24.24,100.0,0.073,38.84,0.026,...
```

---

## 📝 Usage in Submission

These links are embedded in the following documents:

1. **SUBMISSION.md:**
   - Section "Evidence of Success" (lines 93-100)
   - Section "Generated Artifacts" (lines 184-195)
   - Section "GitHub Issue" (line 109)

2. **README_SUBMISSION.md:**
   - Section "Results Achieved" (lines 124-127)
   - Section "Issue Document" (line 103)

3. **LFX_SUBMISSION_PDF.md:**
   - Section "Results" (lines 320-325)
   - PDF export format with hyperlinks

4. **GITHUB_ISSUE.md:**
   - Header section with document link (line 5)

5. **FINAL_CHECKLIST.md:**
   - Section "Evidence Links" (new section after line 15)

---

## 🎯 For Reviewers

**To verify the submission:**

1. **View Cache Evidence:** Click the [cache.json link](https://drive.google.com/file/d/16mus7k2T5d2hB4azM-5gegSsi9Z2EIUv/view?usp=sharing) to see 15,104 lines of benchmark results
2. **View Rankings:** Click the [all_rank_2026.csv link](https://drive.google.com/file/d/1DokMJehEl7I0M8C5hHUTJa1qTXriMJbh/view?usp=drive_link) to see complete performance rankings
3. **View Issue Document:** Click the [Issue Document PDF link](https://drive.google.com/file/d/1DokMJehEl7I0M8C5hHUTJa1qTXriMJbh/view?usp=drive_link) for the complete GitHub issue

**All links are publicly accessible and do not require authentication.**

---

## 📧 Contact

**Candidate:** Prachi Agrawal  
**Email:** agrawalprachi7718@gmail.com  
**GitHub:** [@your-github-username](https://github.com/your-github-username)

**Mentor Contact:** sjhu21@m.fudan.edu.cn  
**Submission Deadline:** February 15, 2026, 23:59 UTC-12

---

*Document created: February 15, 2026*  
*Last updated: February 15, 2026*
