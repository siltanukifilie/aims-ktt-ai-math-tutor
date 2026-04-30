# 🧠 AI Math Tutor for Early Learners (Offline, Multilingual, Adaptive)

## Overview

This project presents an offline AI-powered math tutor designed for children aged 5–9 in low-resource environments. The system delivers foundational numeracy instruction through a combination of visual representations, audio prompts, and interactive feedback, while adapting dynamically to each learner’s progress.

The tutor operates entirely offline, runs on CPU-only devices, and supports multilingual and code-switched input, making it suitable for real-world deployment in settings with limited connectivity and shared devices.

---

## Problem Context

Across many low-resource settings, children complete early primary education without mastering basic numeracy skills. By ages 8–9, many learners still struggle with:

- number recognition  
- simple arithmetic operations  
- problem-solving skills  

The core challenge is not access to schooling, but the lack of **personalized instruction**, compounded by language transitions (e.g., moving from Kinyarwanda to English).

---

## Solution

The system delivers a complete end-to-end tutoring experience:

- presents math problems using visuals and audio  
- accepts responses via text or speech (optional ASR)  
- detects and adapts to the child’s language  
- provides immediate feedback and guided correction  
- repeats questions when needed to reinforce learning  
- adapts difficulty using learner performance  

The focus is on **teaching**, not just evaluation.

---

## Core Capabilities

### 1. Adaptive Learning (Knowledge Tracing)

A Bayesian Knowledge Tracing (BKT) model tracks mastery across skills:

- counting  
- number sense  
- addition  
- subtraction  
- multiplication  
- division  
- word problems  

The system updates learner state after each interaction and selects the next item accordingly.

---

### 2. Multilingual & Code-Switched Interaction

The tutor supports:

- English  
- French  
- Kinyarwanda  
- mixed-language responses  

It detects the dominant language of the child’s input and responds accordingly, while allowing manual language selection.

---

### 3. Visual Grounding (Child-Centered Learning)

Mathematical concepts are presented using simple visual representations:

- Addition → combining objects  
- Subtraction → removing objects  
- Multiplication → repeated groups  
- Division → sharing  

This functions as a lightweight visual reasoning baseline and aligns with how children naturally learn.

---

### 4. Audio Interaction (Offline)

Audio is used to improve accessibility for early learners:

- pre-generated TTS samples in EN / FR / KIN  
- per-question playback  
- fallback to text for reliability  

The system demonstrates a reproducible TTS pipeline while respecting strict footprint constraints.

---

### 5. Teaching Loop (Pedagogical Behavior)

Unlike static quiz systems, the tutor:

- provides hints when answers are incorrect  
- explains correct answers  
- repeats questions until understanding is achieved  
- encourages the learner with positive feedback  

This mimics real teacher behavior in early childhood education.

---

### 6. Local Storage & Progress Tracking

All learner interactions are stored locally using SQLite:

- attempts  
- correctness  
- skill-level progress  

No internet connection is required.

---

### 7. Parent Reporting (Low-Literacy Design)

A weekly report summarizes learner progress using:

- simple icons (😊 ⚠️ ❗)  
- minimal text  
- clear performance indicators  

This ensures usability even for non-literate parents.

---

## Product Design for Real-World Use

### First 90 Seconds Experience

On first launch:

1. The system greets the child in Kinyarwanda  
2. A visual problem is presented (e.g., apples to count)  
3. The tutor asks a simple question  
4. If the child remains silent:
   - a hint is provided  
   - the prompt is repeated  

This creates a guided and supportive entry into learning.

---

### Shared Device Model

Designed for community use:

- multiple children can use the same device  
- each child selects a simple avatar  
- progress is stored locally per learner  
- no login or internet required  

---

## Models and Technical Choices

| Component | Approach |
|----------|--------|
| Knowledge tracing | Bayesian Knowledge Tracing (BKT) |
| ASR (optional) | Whisper-tiny (fallback to text input) |
| Language model (design) | TinyLlama / Phi-3 (LoRA/QLoRA pipeline planned) |
| Visual grounding | Rule-based / blob-style visual representations |

The system prioritizes **lightweight, interpretable, and reliable models** suitable for offline deployment.

---

## Evaluation

The adaptive model is evaluated against a simple baseline:

- baseline: random response prediction  
- model: BKT-based prediction  

Results demonstrate improved prediction accuracy and more effective question selection.

---

## Constraints Compliance

| Requirement | Status |
|-----------|--------|
| Fully offline | ✓ |
| CPU-only | ✓ |
| Latency < 2.5s | ✓ |
| Footprint ≤ 75MB | ✓ |

Notes:
- TTS audio is cached separately and excluded from footprint  
- ASR is optional with fallback support  

---

## Key Strengths

- Complete end-to-end system  
- Designed for real-world constraints  
- Child-friendly learning experience  
- Multilingual and inclusive  
- Adaptive and interactive  
- No dependency on internet connectivity  

---

## Conclusion

This project demonstrates how AI can be applied to deliver **personalized, accessible education** in low-resource environments.

By combining adaptive learning, multilingual interaction, and simple visual teaching methods, the system provides a practical approach to improving early numeracy outcomes without requiring advanced infrastructure.

Website 
https://clever-math-bud.lovable.app
