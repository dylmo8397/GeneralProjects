# Class 10 Student Starter — Agent Harness II

## Goal

Use a coding agent to **vibe-code a thin Streamlit decision-support interface**
around the trusted East-West Airlines optimizer from Class 9.

Do not write a new optimization model.

## Before class

Follow the separate `01_Student_PreClass_Preparation.md` provided by the instructor.
At minimum, make sure:

```bash
py verify_setup.py
```

passes, and complete `MY_INTERFACE_SPEC.md`.

## In class

Use `VIBE_CODING_PROMPTS.md` as prompt cards.

## Run the application on macOS

Open `Class10_Student_Starter` as the VS Code workspace, then run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run appV2.py
```

The included VS Code setting selects `.venv/bin/python` as the project
interpreter. If VS Code was already open when the environment was created,
reload the window before running the app.
