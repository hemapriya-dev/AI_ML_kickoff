import os

NOTES = {
    "knowledge/resume/education.md": """---
type: Resume
title: Education
---
# Education
## Name
My name is Akula Hema Priya.
## Degree
I am pursuing B.Tech in Computer Science and Artificial Intelligence (CAI).
## College
I study at Kakinada Institute of Engineering and Technologies (KIET).
## Diploma
I completed my Diploma with 83.75%.
""",

    "knowledge/resume/projects.md": """---
type: Project
title: Insurance Fraud Claim Scout
---
# Insurance Fraud Claim Scout
## Purpose
The project flags potentially suspicious insurance claims for review.
## Technologies
The project uses Java and Python.
## Java Role
Java processes claims and applies rules based on previous claims,
claim amount, and policy average.
## Python Role
Python calculates a ratio-based fraud risk score.
## Data Files
The project uses claims.csv and fraud_scores.csv.
"""
}

for path, text in NOTES.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        file.write(text)
    print("Saved:", path)

print("\n✅ Resume notes ready!")

import os
import re
import glob

files = [
    path
    for path in sorted(glob.glob("knowledge/**/*.md", recursive=True))
    if os.path.basename(path) not in ("index.md", "log.md")
]

problems = 0

for path in files:
    with open(path, "r", encoding="utf-8") as file:
        text = file.read()

    missing = []

    if not re.search(r"^type:\s*\S+", text, re.M):
        missing.append("type")
    if not re.search(r"^# .+", text, re.M):
        missing.append("title")
    if not re.search(r"^## .+", text, re.M):
        missing.append("section")

    if missing:
        problems += 1
        print("❌", path, "Missing:", ", ".join(missing))
    else:
        print("✅ OK:", path)

index_text = """---
type: Index
title: Resume Knowledge Index
---
# Resume Knowledge Index
"""

for path in files:
    index_text += f"- {path.removeprefix('knowledge/')}\n"

with open("knowledge/index.md", "w", encoding="utf-8") as file:
    file.write(index_text)

print(f"\nChecked {len(files)} notes.")
print("✅ All notes are good!" if problems == 0
      else f"❌ Fix {problems} note(s) before continuing.")

from sentence_transformers import SentenceTransformer
import numpy as np
import re

def load_pieces():
    pieces = []

    for path in files:
        with open(path, "r", encoding="utf-8") as file:
            text = file.read()

        title = re.search(r"^# (.+)$", text, re.M).group(1)

        sections = re.split(r"^## ", text, flags=re.M)[1:]

        for section in sections:
            pieces.append({
                "file": path,
                "text": f"{title}: {section.strip()}"
            })

    return pieces

PIECES = load_pieces()

if not PIECES:
    raise ValueError("No resume sections found. Check Cells 2 and 3.")

model = SentenceTransformer("all-MiniLM-L6-v2")

VECTORS = model.encode(
    [piece["text"] for piece in PIECES],
    normalize_embeddings=True
)

def find(question):
    question_vector = model.encode(
        [question],
        normalize_embeddings=True
    )[0]

    scores = VECTORS @ question_vector
    best_index = int(np.argmax(scores))

    return float(scores[best_index]), PIECES[best_index]

print("✅ Search ready!")
print("Total sections:", len(PIECES))

score, piece = find("What is my diploma percentage?")

print("\nFound in:", piece["file"])
print("Matching score:", round(score, 2))
print("Information:", piece["text"])

LIMIT = 0.30

path = "knowledge/resume/projects.md"

with open(path, "r", encoding="utf-8") as file:
    text = file.read()

text = text.replace(
    "Python calculates a ratio-based fraud risk score.",
    "Python's role in this project is to calculate a ratio-based "
    "fraud risk score for insurance claims."
)

text = text.replace(
    "The project uses claims.csv and fraud_scores.csv.",
    "The data files used by this project are claims.csv "
    "and fraud_scores.csv."
)

with open(path, "w", encoding="utf-8") as file:
    file.write(text)

print("✅ Project descriptions updated!")

import os
import re
import glob
import numpy as np
import gradio as gr
import inspect

# Fallback or simple implementation of generate_answer since it was missing
def generate_answer(question, context):
    # Simple parser to remove markdown headers and provide just the clean answer text
    clean_context = context
    if ":" in context:
        clean_context = context.split(":", 1)[1].strip()
    return clean_context

# Close the previous interface before creating the new one.
if "demo" in globals():
    demo.close()

CSS = """
.gradio-container {
    max-width: 1050px !important;
    margin: auto !important;
    background: linear-gradient(135deg, #f5f3ff, #fdf2f8) !important;
    padding: 24px !important;
}
#hero {
    background: linear-gradient(120deg, #4c1d95, #7c3aed, #db2777);
    border-radius: 24px;
    padding: 36px;
    margin-bottom: 22px;
    box-shadow: 0 12px 32px rgba(109, 40, 217, 0.18);
}
#hero h1 {
    color: white;
    font-size: clamp(28px, 5vw, 42px);
    margin: 12px 0;
    line-height: 1.2;
}
#hero p {
    color: #ede9fe;
    font-size: 16px;
    line-height: 1.6;
}
.hero-tag {
    display: inline-block;
    color: white;
    background: rgba(255,255,255,0.16);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 30px;
    padding: 7px 14px;
    font-size: 12px;
    letter-spacing: 1px;
}
.design-card {
    background: #ffffff !important;
    border: 1px solid #ddd6fe !important;
    border-radius: 20px !important;
    padding: 22px !important;
    box-shadow: 0 8px 24px rgba(76, 29, 149, 0.07);
}
.design-card h3, .design-card label {
    color: #4c1d95 !important;
}
.design-card textarea, .design-card input {
    background: #faf8ff !important;
    color: #2e1065 !important;
    border-radius: 12px !important;
}
#ask-button {
    background: linear-gradient(110deg, #7c3aed, #a855f7) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    min-height: 46px;
    transition: transform 0.2s, box-shadow 0.2s;
}
#ask-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(124,58,237,0.3);
}
#clear-button {
    background: #ede9fe !important;
    color: #5b21b6 !important;
    border-radius: 12px !important;
}
#footer {
    text-align: center;
    color: #6b7280;
    padding-top: 18px;
    font-size: 13px;
}
@media (max-width: 600px) {
    .gradio-container { padding: 12px !important; }
    #hero { padding: 24px; }
}
"""

def ask_resume(question):
    if not question or not question.strip():
        return "", "", "Please type a question."

    score, piece = find(question.strip())

    if score < LIMIT:
        return (
            "No matching source",
            f"{score:.3f}",
            "No relevant information found in my resume."
        )

    generated = generate_answer(question.strip(), piece["text"])

    return (
        piece["file"],
        f"{score:.3f}",
        f"{generated}\n\nSource note:\n{piece['text']}"
    )

theme = gr.themes.Soft(
    primary_hue="purple",
    secondary_hue="pink",
    neutral_hue="slate"
)

# Support both older and newer Gradio styling locations.
styling = {"theme": theme, "css": CSS}
launch_styling = "css" in inspect.signature(gr.Blocks.launch).parameters

with gr.Blocks(
    title="Resume-Q&A",
    **({} if launch_styling else styling)
) as demo:

    gr.HTML("""
    <div id="hero">
        <span class="hero-tag">HEMA PRIYA · RESUME ASSISTANT</span>
        <h1>Your questions.<br>My experience.</h1>
        <p>Explore my education and Insurance Fraud Claim Scout
        project through answers with source notes.</p>
    </div>
    """)

    with gr.Row():
        with gr.Column(scale=4, min_width=280, elem_classes=["design-card"]):
            gr.Markdown("### 💬 Ask a question")

            question = gr.Textbox(
                label="What would you like to know?",
                placeholder="What does Python do in my project?",
                lines=3
            )

            with gr.Row():
                ask_button = gr.Button(
                    "Ask ✨",
                    variant="primary",
                    elem_id="ask-button"
                )
                clear_button = gr.Button(
                    "Clear",
                    elem_id="clear-button"
                )

            gr.Markdown("### Try an example")
            gr.Examples(
                examples=[
                    ["What is my name?"],
                    ["Where do I study?"],
                    ["What is my diploma percentage?"],
                    ["What does Java do in my project?"],
                    ["What does Python do in my project?"],
                    ["Which data files does my project use?"]
                ],
                inputs=[question]
            )

        with gr.Column(scale=5, min_width=280, elem_classes=["design-card"]):
            gr.Markdown("### ✨ Your answer")

            answer = gr.Textbox(
                label="AI answer and source note",
                placeholder="Your answer will appear here.",
                lines=10,
                interactive=False
            )

            with gr.Row():
                source = gr.Textbox(
                    label="Source",
                    interactive=False
                )
                similarity = gr.Textbox(
                    label="Similarity score",
                    interactive=False
                )

            gr.Markdown(
                "*Check the source note to verify the answer. "
                "Similarity is not a confidence percentage.*"
            )

    gr.HTML(
        '<div id="footer">'
        'Hema Priya Resume Q&A · Education & Projects'
        '</div>'
    )

    ask_button.click(
        fn=ask_resume,
        inputs=[question],
        outputs=[source, similarity, answer]
    )

    question.submit(
        fn=ask_resume,
        inputs=[question],
        outputs=[source, similarity, answer]
    )

    clear_button.click(
        fn=lambda: ("", "", "", ""),
        inputs=[],
        outputs=[question, source, similarity, answer],
        queue=False
    )

if __name__ == "__main__":
    demo.launch(**(styling if launch_styling else {}))