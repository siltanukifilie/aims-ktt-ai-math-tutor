"""
demo.py

Purpose:
- Run the child-facing Gradio demo.
- Show a math question.
- Accept typed or simulated speech input.
- Extract the child answer.
- Score the answer.
- Update the adaptive BKT learner state.
- Save progress locally to SQLite.

Judge Defense:
- This is the on-device inference loop:
  question -> child response -> scoring -> feedback -> next question.
- It uses the BKT adaptive model, multilingual input adapter, and local progress store.
"""

import gradio as gr

from tutor.adaptive import (
    create_learner_state,
    choose_next_item,
    update_learner_state,
    get_feedback,
)

from tutor.asr_adapt import process_child_input
from tutor.storage import save_progress


# -----------------------------
# SESSION STATE
# -----------------------------

learner_state = create_learner_state()
current_item = None
LEARNER_ID = "child_1"


# -----------------------------
# DEMO FUNCTIONS
# -----------------------------

def start_tutor():
    """
    Purpose:
    - Start a new tutor session.
    - Select the first adaptive question.

    Judge Defense:
    - The first question is selected using the adaptive engine,
      not hardcoded.
    """
    global current_item

    current_item = choose_next_item(learner_state)

    return (
        current_item.get("stem_en", "Question missing"),
        current_item.get("visual", "no_visual"),
        "Tutor started. Type an answer like 3, three, trois, or gatatu.",
        str(learner_state),
    )


def answer_question(child_input):
    """
    Purpose:
    - Process child answer.
    - Detect language.
    - Extract numeric answer.
    - Score correctness.
    - Update mastery.
    - Save progress locally.
    - Select next question.

    Judge Defense:
    - This function connects all key components:
      ASR adapter, scoring, BKT update, SQLite storage, and next-item selection.
    """
    global current_item
    global learner_state

    if current_item is None:
        return (
            "Please click Start Tutor first.",
            "no_visual",
            "No question has been selected yet.",
            str(learner_state),
        )

    processed = process_child_input(child_input)

    if processed["answer"] is None:
        return (
            current_item.get("stem_en", "Question missing"),
            current_item.get("visual", "no_visual"),
            processed["message"],
            str(learner_state),
        )

    learner_state, is_correct = update_learner_state(
        learner_state,
        current_item,
        processed["answer"],
    )

    save_progress(
        learner_id=LEARNER_ID,
        item=current_item,
        is_correct=is_correct,
        learner_state=learner_state,
    )

    feedback = get_feedback(is_correct, processed["language"])

    current_item = choose_next_item(learner_state)

    return (
        current_item.get("stem_en", "Question missing"),
        current_item.get("visual", "no_visual"),
        feedback,
        str(learner_state),
    )


# -----------------------------
# GRADIO UI
# -----------------------------

with gr.Blocks() as demo:
    gr.Markdown("# AI Math Tutor for Early Learners")

    gr.Markdown(
        """
        Offline adaptive math tutor demo.

        **Core components used:**
        - Bayesian Knowledge Tracing adaptive model
        - Multilingual input handling: English, French, Kinyarwanda, mixed
        - Local SQLite progress storage
        - Visual reference for object-counting questions
        """
    )

    question_box = gr.Textbox(label="Question", interactive=False)
    visual_box = gr.Textbox(label="Visual reference", interactive=False)
    answer_box = gr.Textbox(label="Child answer / simulated speech")
    feedback_box = gr.Textbox(label="Tutor feedback", interactive=False)
    state_box = gr.Textbox(label="Learner mastery state", interactive=False)

    start_button = gr.Button("Start Tutor")
    answer_button = gr.Button("Submit Answer")

    start_button.click(
        fn=start_tutor,
        outputs=[question_box, visual_box, feedback_box, state_box],
    )

    answer_button.click(
        fn=answer_question,
        inputs=answer_box,
        outputs=[question_box, visual_box, feedback_box, state_box],
    )


if __name__ == "__main__":
    demo.launch()