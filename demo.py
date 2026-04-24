import gradio as gr
import time
import re
import os
from pathlib import Path

from tutor.adaptive import (
    create_learner_state,
    choose_next_item,
    update_learner_state,
    mastery_to_difficulty,
)

from tutor.asr_adapt import process_child_input, process_audio_or_text
from tutor.storage import save_progress
from tutor.curriculum_loader import load_curriculum


learner_state = create_learner_state()
current_item = None
last_time = time.time()
LEARNER_ID = "child_1"

ENABLE_ASR = os.getenv("ENABLE_ASR", "0") == "1" and (Path("models") / "whisper-tiny").exists()
WHISPER_MODEL_DIR = str(Path("models") / "whisper-tiny")

SKILL_OPTIONS = ["adaptive", "addition", "subtraction", "multiplication", "division"]


def choose_next_item_with_skill(learner_state, selected_skill):
    """
    If selected_skill == 'adaptive', use the normal adaptive policy.
    Otherwise, sample an item from that specific skill (bounded by current mastery difficulty).
    """
    if selected_skill == "adaptive":
        return choose_next_item(learner_state)

    curriculum = load_curriculum()
    mastery = learner_state.get(selected_skill, {}).get("mastery", 0.30)
    max_difficulty = mastery_to_difficulty(mastery)

    candidates = [
        item
        for item in curriculum
        if item.get("skill") == selected_skill and item.get("difficulty", 1) <= max_difficulty
    ]

    if not candidates:
        candidates = [item for item in curriculum if item.get("skill") == selected_skill]

    if not candidates:
        return choose_next_item(learner_state)

    import random

    return random.choice(candidates)


# -----------------------------
# CHILD-FRIENDLY VISUALS
# -----------------------------

def render_math_visual(item):
    skill = item["skill"]
    text = item.get("stem_en", "")
    nums = list(map(int, re.findall(r"\d+", text)))

    if skill == "addition" and len(nums) >= 2:
        a, b = nums
        return f"{'🍎'*a} ➕ {'🍎'*b}"

    if skill == "subtraction" and len(nums) >= 2:
        a, b = nums
        return f"{'🍎'*a} ➖ {'❌'*b}"

    if skill == "multiplication" and len(nums) >= 2:
        a, b = nums
        return "\n".join(["🍎"*b for _ in range(a)])

    if skill == "division" and len(nums) >= 2:
        a, b = nums
        return f"🍎{'🍎'*a} ➗ {b} 👧👦"

    if "goats" in item.get("visual",""):
        return "🐐🐐🐐🐐🐐🐐🐐🐐🐐"

    return item.get("visual", "")


# -----------------------------
# LANGUAGE + QUESTION
# -----------------------------

def get_question_text(item, lang):
    if lang == "kin":
        return item.get("stem_kin", item["stem_en"])
    if lang == "fr":
        return item.get("stem_fr", item["stem_en"])
    return item["stem_en"]


# -----------------------------
# AUDIO
# -----------------------------

def get_audio_path(item, lang):
    base = "tts_audio"
    file_id = item["id"].lower()

    path = f"{base}/{lang}/{file_id}.wav"
    if os.path.exists(path):
        return path

    fallback = f"{base}/en/{file_id}.wav"
    if os.path.exists(fallback):
        return fallback

    return None


# -----------------------------
# TEACHING FEEDBACK
# -----------------------------

def generate_feedback(is_correct, item, lang):
    correct = item["answer_int"]

    if is_correct:
        return {
            "en": "🎉 Great job!",
            "fr": "🎉 Bravo!",
            "kin": "🎉 Ni byo!"
        }.get(lang, "🎉 Good!")

    hint = f"💡 Answer is {correct}"

    if item["skill"] == "addition":
        hint = f"💡 Add them together → {correct}"

    if item["skill"] == "subtraction":
        hint = f"💡 Remove some → {correct}"

    if item["skill"] == "multiplication":
        hint = f"💡 Groups → {correct}"

    if item["skill"] == "division":
        hint = f"💡 Share equally → {correct}"

    return {
        "en": f"❗ Try again! {hint}",
        "fr": f"❗ Essaie encore! {hint}",
        "kin": f"❗ Ongera! {hint}"
    }.get(lang, hint)


# -----------------------------
# START
# -----------------------------

def start_tutor(lang, selected_skill):
    global current_item, last_time
    last_time = time.time()

    current_item = choose_next_item_with_skill(
        learner_state,
        selected_skill if selected_skill in SKILL_OPTIONS else "adaptive",
    )

    welcome = {
        "en": "👋 Hello! Let's learn math 🎉",
        "fr": "👋 Bonjour! Apprenons 🎉",
        "kin": "👋 Muraho! Twigire kubara 🎉"
    }.get(lang, "👋 Hello!")

    return (
        welcome + "\n\n" + get_question_text(current_item, lang),
        render_math_visual(current_item),
        get_audio_path(current_item, lang),
        "😊 Answer below!",
        str(learner_state)
    )


# -----------------------------
# ANSWER
# -----------------------------

def answer_question(child_input, child_audio, lang, selected_skill):
    global current_item, learner_state, last_time

    now = time.time()

    if now - last_time > 10:
        return (
            get_question_text(current_item, lang),
            render_math_visual(current_item),
            get_audio_path(current_item, lang),
            "💡 Count slowly…",
            str(learner_state)
        )

    last_time = now

    if ENABLE_ASR and child_audio:
        processed = process_audio_or_text(
            audio_path=child_audio,
            typed_text=child_input,
            model_dir=WHISPER_MODEL_DIR,
            enable_asr=True,
        )
    else:
        processed = process_child_input(child_input)
    if lang == "auto":
        lang = processed["language"]

    if processed["answer"] is None:
        return (
            get_question_text(current_item, lang),
            render_math_visual(current_item),
            get_audio_path(current_item, lang),
            "🤔 Say a number!",
            str(learner_state)
        )

    learner_state, is_correct = update_learner_state(
        learner_state,
        current_item,
        processed["answer"]
    )

    save_progress(LEARNER_ID, current_item, is_correct, learner_state)

    feedback = generate_feedback(is_correct, current_item, lang)

    if not is_correct:
        return (
            get_question_text(current_item, lang),
            render_math_visual(current_item),
            get_audio_path(current_item, lang),
            feedback,
            str(learner_state)
        )

    current_item = choose_next_item_with_skill(
        learner_state,
        selected_skill if selected_skill in SKILL_OPTIONS else "adaptive",
    )

    return (
        get_question_text(current_item, lang),
        render_math_visual(current_item),
        get_audio_path(current_item, lang),
        feedback,
        str(learner_state)
    )


# -----------------------------
# UI
# -----------------------------

with gr.Blocks() as demo:
    gr.Markdown("# 🎈 Fun Math Tutor")

    lang_selector = gr.Dropdown(
        ["auto", "en", "fr", "kin"],
        value="auto",
        label="🌍 Language"
    )

    skill_selector = gr.Dropdown(
        SKILL_OPTIONS,
        value="adaptive",
        label="🧮 Skill (practice mode)",
    )

    question = gr.Textbox(label="📚 Question", interactive=False)
    visual = gr.Textbox(label="🖼️ Look!", interactive=False)
    audio = gr.Audio(label="🔊 Listen")
    child_audio = gr.Audio(sources=["microphone"], type="filepath", label="🎙️ Speak (optional)")
    answer = gr.Textbox(label="🎤 Your Answer")
    feedback = gr.Textbox(label="💬 Feedback", interactive=False)
    state = gr.Textbox(label="📊 Progress", interactive=False)

    start = gr.Button("▶️ Start")
    submit = gr.Button("✅ Answer")

    start.click(
        start_tutor,
        inputs=[lang_selector, skill_selector],
        outputs=[question, visual, audio, feedback, state]
    )

    submit.click(
        answer_question,
        inputs=[answer, child_audio, lang_selector, skill_selector],
        outputs=[question, visual, audio, feedback, state]
    )

demo.launch()