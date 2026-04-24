import gradio as gr

from tutor.adaptive import (
    create_learner_state,
    choose_next_item,
    update_learner_state,
)

from tutor.asr_adapt import process_child_input
from tutor.storage import save_progress


learner_state = create_learner_state()
current_item = None

LEARNER_ID = "child_1"


def get_question_text(item, language):
    """
    Return question in correct language.
    """
    if language == "fr" and "stem_fr" in item:
        return item["stem_fr"]

    if language == "kin" and "stem_kin" in item:
        return item["stem_kin"]

    return item.get("stem_en", "Question missing")


def simplify_question(item, language):
    base = get_question_text(item, language)

    if item.get("skill") == "number_sense":
        return {
            "en": "👉 Which is bigger? 4 or 7?",
            "fr": "👉 Lequel est plus grand? 4 ou 7?",
            "kin": "👉 Ni iyihe nini? 4 cyangwa 7?",
        }.get(language, base)

    return base


def render_visual(item):
    visual = str(item.get("visual", ""))

    if "goats" in visual:
        return "🐐🐐🐐🐐🐐🐐🐐🐐🐐"
    if "apples" in visual:
        return "🍎🍎🍎"
    if "compare" in visual:
        return "4️⃣   vs   7️⃣"

    return visual or "no_visual"


def render_math_visual(item):
    """
    Render visual teaching for math operations using emojis
    """

    skill = item.get("skill")

    # Try to extract numbers from question
    text = item.get("stem_en", "")

    import re

    nums = list(map(int, re.findall(r"\d+", text)))

    if skill == "addition" and len(nums) >= 2:
        a, b = nums[0], nums[1]
        return f"{'🍎' * a} + {'🍎' * b} = ?"

    if skill == "subtraction" and len(nums) >= 2:
        a, b = nums[0], nums[1]
        return f"{'🍎' * a} - {'❌' * b} = ?"

    if skill == "multiplication" and len(nums) >= 2:
        a, b = nums[0], nums[1]
        return "\n".join(["🍎" * b for _ in range(a)])

    if skill == "division" and len(nums) >= 2:
        a, b = nums[0], nums[1]
        return f"{a} items shared into {b} groups"

    # fallback
    return render_visual(item)


def generate_teaching_feedback(is_correct, item, child_answer, language):
    correct_answer = item["answer_int"]

    if is_correct:
        return {
            "en": "🎉 Correct! Great job!",
            "fr": "🎉 Bravo! C'est correct!",
            "kin": "🎉 Ni byo! Komereza aho!",
        }.get(language, "🎉 Correct!")

    import re

    nums = list(map(int, re.findall(r"\d+", item.get("stem_en", ""))))

    # TEACHING FEEDBACK (CRITICAL)
    hint = {
        "en": f"💡 The correct answer is {correct_answer}. Let's count together.",
        "fr": f"💡 La bonne réponse est {correct_answer}. Comptons ensemble.",
        "kin": f"💡 Igisubizo ni {correct_answer}. Reka tubare hamwe.",
    }.get(language, f"💡 The correct answer is {correct_answer}. Let's count together.")

    if item.get("skill") == "number_sense":
        hint = {
            "en": "💡 7 is bigger than 4. Bigger means the larger number.",
            "fr": "💡 7 est plus grand que 4. Plus grand veut dire le plus grand nombre.",
            "kin": "💡 7 ni nini kurusha 4. Nini bivuze umubare munini.",
        }.get(language, "💡 7 is bigger than 4. Bigger means the larger number.")

    if item.get("skill") == "counting":
        hint = {
            "en": f"💡 Count carefully. The answer is {correct_answer}.",
            "fr": f"💡 Compte bien. La réponse est {correct_answer}.",
            "kin": f"💡 Bara neza. Igisubizo ni {correct_answer}.",
        }.get(language, f"💡 Count carefully. The answer is {correct_answer}.")

    if item.get("skill") == "addition" and len(nums) >= 2:
        hint = f"💡 Add them: {nums[0]} + {nums[1]} = {correct_answer}"

    elif item.get("skill") == "subtraction" and len(nums) >= 2:
        hint = f"💡 Remove items: {nums[0]} - {nums[1]} = {correct_answer}"

    elif item.get("skill") == "multiplication" and len(nums) >= 2:
        hint = f"💡 Groups of {nums[1]} repeated {nums[0]} times"

    elif item.get("skill") == "division" and len(nums) >= 2:
        hint = f"💡 Share {nums[0]} into {nums[1]} groups"

    return {
        "en": f"❗ Not quite. {hint}",
        "fr": f"❗ Pas encore. {hint}",
        "kin": f"❗ Ongera ugerageze. {hint}",
    }.get(language, hint)


def start_tutor(selected_lang):
    global current_item
    current_item = choose_next_item(learner_state)

    if selected_lang == "kin":
        welcome = "👋 Muraho! Reka twigire kubara 🎉"
    elif selected_lang == "fr":
        welcome = "👋 Bonjour! Apprenons les mathématiques 🎉"
    else:
        welcome = "👋 Hello! Let's learn math 🎉"

    language = selected_lang if selected_lang != "auto" else "kin"

    return (
        welcome + "\n\n" + simplify_question(current_item, language),
        f"👀 {render_math_visual(current_item)}",
        welcome,
        "Subiza ikibazo 😊",
        str(learner_state),
    )


def answer_question(child_input, selected_lang):
    global current_item, learner_state

    processed = process_child_input(child_input)

    # Priority: user selection > auto-detect
    if selected_lang != "auto":
        language = selected_lang
    else:
        language = processed["language"]

    if processed["answer"] is None:
        return (
            simplify_question(current_item, language),
            render_math_visual(current_item),
            processed["message"],
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

    feedback = generate_teaching_feedback(
        is_correct,
        current_item,
        processed["answer"],
        language,
    )

    # Teaching loop: repeat until correct
    if not is_correct:
        return (
            simplify_question(current_item, language),
            render_math_visual(current_item),
            feedback,
            feedback,
            str(learner_state),
        )

    current_item = choose_next_item(learner_state)

    return (
        simplify_question(current_item, language),
        f"👀 {render_math_visual(current_item)}",
        feedback,
        feedback,
        str(learner_state),
    )


with gr.Blocks() as demo:
    gr.Markdown("# 🧠 AI Math Tutor (Offline)")

    gr.Markdown(
        """
        👶 Designed for children (5–9 years)  
        🌍 Works offline  
        🗣️ Multilingual (EN / FR / KIN)  
        🧠 Adaptive learning  
        """
    )

    question_box = gr.Textbox(label="📚 Question", interactive=False)
    visual_box = gr.Textbox(label="🖼️ Visual", interactive=False)
    audio_box = gr.Textbox(label="🔊 Audio (text)", interactive=False)
    answer_box = gr.Textbox(label="🎤 Your Answer")
    feedback_box = gr.Textbox(label="💬 Feedback", interactive=False)
    state_box = gr.Textbox(label="📊 Progress", interactive=False)

    lang_selector = gr.Dropdown(
        choices=["auto", "en", "fr", "kin"],
        value="auto",
        label="🌍 Language",
    )

    start_button = gr.Button("▶️ Start")
    answer_button = gr.Button("✅ Submit")

    start_button.click(
        start_tutor,
        inputs=[lang_selector],
        outputs=[question_box, visual_box, audio_box, feedback_box, state_box],
    )

    answer_button.click(
        answer_question,
        inputs=[answer_box, lang_selector],
        outputs=[question_box, visual_box, audio_box, feedback_box, state_box],
    )


demo.launch()