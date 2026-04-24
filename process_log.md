## Development Timeline (9:30 AM – 2:00 PM)

Total working time: ~4 hours 15 minutes  
Break: 15 minutes  

---

### 9:30 – 10:15 (45 min) — Project Setup & Understanding
- Read and analyzed the full challenge brief
- Understood constraints (offline, ≤75MB, CPU-only)
- Explored provided dataset (curriculum_seed, probes, utterances)
- Planned overall system architecture

---

### 10:15 – 11:00 (45 min) — Curriculum & Data Generation
- Generated full curriculum (≥ 60 items)
- Structured skills: counting, number sense, addition, subtraction, word problems
- Created `full_curriculum.json`
- Built `curriculum_loader.py`

---

### 11:00 – 11:45 (45 min) — Adaptive Model (BKT)
- Implemented Bayesian Knowledge Tracing model
- Designed learner state tracking
- Built next-question selection logic
- Tested adaptive behavior

---

### 11:45 – 12:00 (15 min) — Break

---

### 12:00 – 12:45 (45 min) — Demo + Multilingual System
- Built Gradio demo interface
- Implemented multilingual input (EN / FR / KIN)
- Added language detection + code-switching handling
- Connected adaptive model to UI

---

### 12:45 – 1:30 (45 min) — Storage + Reporting
- Implemented SQLite local storage
- Saved learner progress per interaction
- Built `parent_report.py`
- Designed simple parent-friendly output (icons + summary)

---

### 1:30 – 2:00 (30 min) — Final UX + Audio + Visual Improvements
- Added child-friendly UI (emojis, simple prompts)
- Implemented teaching feedback (hints, repetition)
- Integrated TTS sample audio
- Added math visualizations (addition, subtraction, multiplication, division)
- Final testing and debugging