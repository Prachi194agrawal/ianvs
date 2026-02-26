# Final Submission Checklist

## ✅ Files Ready for Submission

### PDF Documents (1.6 MB total)
- [ ] **LFX_PROPOSAL.pdf** (482 KB) - Complete proposal with innovative AHSD idea
- [ ] **RUNLOG.pdf** (283 KB) - Reproducible run log with evidence
- [ ] **GITHUB_ISSUE.pdf** (366 KB) - Community improvement with code
- [ ] **SUBMISSION.pdf** (233 KB) - Submission summary
- [ ] **README_SUBMISSION.pdf** (251 KB) - Navigation guide (optional)

### Source Files (for reference)
- [x] LFX_PROPOSAL.md (30 KB)
- [x] RUNLOG.md (17 KB)
- [x] GITHUB_ISSUE.md (17 KB)
- [x] SUBMISSION.md (13 KB)
- [x] README_SUBMISSION.md (7.7 KB)

### Evidence Links (Google Drive)
- [x] **Cache File (Primary Evidence):** [cache.json - 15,104 lines](https://drive.google.com/file/d/16mus7k2T5d2hB4azM-5gegSsi9Z2EIUv/view?usp=sharing)
- [x] **Final Ranking Results (February 2026):** [all_rank_2026.csv](https://drive.google.com/file/d/1DokMJehEl7I0M8C5hHUTJa1qTXriMJbh/view?usp=drive_link)
- [x] **Issue Document PDF:** [GitHub Issue Document](https://drive.google.com/file/d/1DokMJehEl7I0M8C5hHUTJa1qTXriMJbh/view?usp=drive_link)

---

## 📝 Before You Submit

### 1. Personalize Documents
Replace these placeholders in **SUBMISSION.md** and **SUBMISSION.pdf**:

```bash
# Open in editor and replace:
[Your Full Name]        → Your actual name
[Your Email Address]    → Your email
[@your-github-username] → Your GitHub username
```

**Files to edit:**
- SUBMISSION.md (then regenerate PDF)

**Command to regenerate:**
```bash
cd /home/prachi/ianvs
pandoc SUBMISSION.md -s --metadata title="SUBMISSION" -o SUBMISSION.html
google-chrome --headless --disable-gpu --print-to-pdf="SUBMISSION.pdf" "SUBMISSION.html" 2>/dev/null
rm SUBMISSION.html
```

---

### 2. Create GitHub Issue

1. Go to: https://github.com/kubeedge/ianvs/issues/new
2. **Title:** Add Automatic Checkpointing for Long-Running Benchmarks to Prevent Progress Loss
3. **Labels:** Select `enhancement`, `benchmarking` (if available)
4. **Body:** Copy entire content from [GITHUB_ISSUE.md](GITHUB_ISSUE.md)
5. Click "Submit new issue"
6. **Copy the issue URL** (e.g., https://github.com/kubeedge/ianvs/issues/123)

---

### 3. Update SUBMISSION.md with Issue Link

Edit SUBMISSION.md:
```markdown
**GitHub Issue Link:** https://github.com/kubeedge/ianvs/issues/123  
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                      (Replace with actual issue number)
```

Then regenerate SUBMISSION.pdf using the command above.

---

### 4. Prepare Email

**To:** sjhu21@m.fudan.edu.cn  
**Subject:** LFX Mentorship Pre-Test Submission - [Your Name]

**Email Body:**
```
Dear KubeEdge Team,

Please find attached my submission for the LFX Mentorship 2026 Term 1 pre-test 
for the "Cloud-Edge Simulation Benchmark for LLM Speculative Decoding" project.

Submission Contents:
- SUBMISSION.pdf (Submission summary with all links)
- LFX_PROPOSAL.pdf (Task 1: Mini Proposal)
- RUNLOG.pdf (Task 2A: Reproducible Run Log)
- GITHUB_ISSUE.pdf (Task 2B: Community-facing Improvement)

GitHub Issue Link: https://github.com/kubeedge/ianvs/issues/XXXX
(Replace XXXX with your actual issue number)

Key Highlights:
- Innovative Idea: Adaptive Hybrid Speculative Decoding (AHSD)
- Working Implementation: Checkpointing system for long-running benchmarks
- Complete Reproduction: Successfully ran cloud-edge LLM inference example
- Results: 54.55% accuracy, 72.73% edge ratio on GPQA dataset

I look forward to your feedback.

Best regards,
[Your Name]
[Your Email]
[Your GitHub: @username]
```

**Attachments to Include:**
1. SUBMISSION.pdf
2. LFX_PROPOSAL.pdf
3. RUNLOG.pdf
4. GITHUB_ISSUE.pdf

---

### 5. Verify PDFs

Open each PDF and verify:
- [ ] Text is readable
- [ ] Code blocks are formatted correctly
- [ ] Tables are aligned properly
- [ ] No critical content is cut off
- [ ] File size is reasonable (< 500KB each)

**Command to open:**
```bash
cd /home/prachi/ianvs
xdg-open SUBMISSION.pdf
xdg-open LFX_PROPOSAL.pdf
xdg-open RUNLOG.pdf
xdg-open GITHUB_ISSUE.pdf
```

---

### 6. Double-Check Content

#### SUBMISSION.pdf:
- [ ] Name, email, GitHub username filled in
- [ ] GitHub issue link updated
- [ ] All sections complete

#### LFX_PROPOSAL.pdf:
- [ ] Section 6 (Innovative Idea) is clear and detailed
- [ ] All 5 milestones included
- [ ] Code examples are readable

#### RUNLOG.pdf:
- [ ] Environment info documented
- [ ] Step-by-step commands complete
- [ ] Results table shows 54.55% accuracy

#### GITHUB_ISSUE.pdf:
- [ ] Reproduction steps are clear
- [ ] Error logs are complete
- [ ] Proposed solution code is readable

---

## 🚀 Submission Steps

### Step 1: Personalize
```bash
# Edit SUBMISSION.md with your info
nano SUBMISSION.md

# Regenerate PDF
pandoc SUBMISSION.md -s --metadata title="SUBMISSION" -o SUBMISSION.html
google-chrome --headless --disable-gpu --print-to-pdf="SUBMISSION.pdf" "SUBMISSION.html" 2>/dev/null
rm SUBMISSION.html
```

### Step 2: Create GitHub Issue
1. Visit: https://github.com/kubeedge/ianvs/issues/new
2. Paste content from GITHUB_ISSUE.md
3. Submit
4. Copy issue URL

### Step 3: Update Issue Link
```bash
# Edit SUBMISSION.md with issue URL
nano SUBMISSION.md
# Update line: **GitHub Issue Link:** https://github.com/kubeedge/ianvs/issues/XXX

# Regenerate PDF again
pandoc SUBMISSION.md -s --metadata title="SUBMISSION" -o SUBMISSION.html
google-chrome --headless --disable-gpu --print-to-pdf="SUBMISSION.pdf" "SUBMISSION.html" 2>/dev/null
rm SUBMISSION.html
```

### Step 4: Send Email
1. Open your email client
2. Compose new email to: sjhu21@m.fudan.edu.cn
3. Subject: LFX Mentorship Pre-Test Submission - [Your Name]
4. Copy email template above
5. Attach 4 PDFs:
   - SUBMISSION.pdf
   - LFX_PROPOSAL.pdf
   - RUNLOG.pdf
   - GITHUB_ISSUE.pdf
6. **Send!**

---

## 📅 Deadline

**February 15, 2026, 23:59 UTC-12**

Calculate your local time:
- UTC-12 = Hawaii Time
- If you're in India (UTC+5:30), that's **February 16, 2026, 11:29 AM IST**

---

## 🎯 Expected Evaluation

| Criterion | Points | Your Evidence |
|-----------|--------|---------------|
| Task 1: Proposal | 30 | Complete with 6 sections |
| Task 1: Innovation | 25 | AHSD with 4 techniques |
| Task 2A: Reproducibility | 25 | Full runlog with results |
| Task 2B: Issue Quality | 20 | Working code implementation |
| **TOTAL** | **100** | **95-100 expected** |

---

## 📞 Support

**Mentor Contact:** sjhu21@m.fudan.edu.cn  
**Ianvs Repository:** https://github.com/kubeedge/ianvs  
**Community:** https://github.com/kubeedge/community/tree/master/sig-ai

---

## ✅ Final Verification

Before sending, confirm:
- [ ] All 4 PDFs are attached to email
- [ ] GitHub issue is created and link is in SUBMISSION.pdf
- [ ] Personal information (name, email, GitHub) is filled in
- [ ] Email subject matches: "LFX Mentorship Pre-Test Submission - [Your Name]"
- [ ] Sending to correct email: sjhu21@m.fudan.edu.cn
- [ ] Deadline not passed (Feb 15, 2026, 23:59 UTC-12)

---

**You're ready to submit! Good luck! 🍀**

---

*Checklist created: February 13, 2026*  
*Location: /home/prachi/ianvs/*
