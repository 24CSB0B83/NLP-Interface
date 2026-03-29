 Natural Language Query Interface for Compiler

> Analyze Python code using plain English — no complex tooling required.

I.Table of Contents

- [Overview](#overview)
- [Demo](#demo)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Query Reference](#query-reference)
- [How It Works](#how-it-works)
- [Evaluation](#evaluation)
- [Error Handling](#error-handling)
- [Future Improvements](#future-improvements)
- [Author](#author)
- [License](#license)


1. Overview

"NL Query Interface for Compiler" is a Streamlit web app that lets you inspect and analyze Python code using natural language queries.

Instead of writing analysis scripts yourself, you type queries like `"find unused variables"` or `"generate CFG"` and the app does the heavy lifting using Python's built-in `ast` module. It also includes an evaluation module that measures how accurately the system explains Python errors against a curated dataset.

2. Demo

> **Run it locally** — see [Installation](#installation) below.

┌─────────────────────────────┬──────────────────────────────┐
│  💻 Enter Python Code       │  ❓ Ask your Query           │
│                             │                              │
│  def add(a, b):             │  find unused variables       │
│      result = a + b         │                              │
│      unused = 42            │  [ Run Query ]               │
│      return result          │                              │
│                             │  📊 Result                   │
│                             │  ⚠ Unused variables: [unused]│
└─────────────────────────────┴──────────────────────────────┘

3. Features

| Feature | Query Trigger | Description |
|---|---|---|
| Extract variables | `list variables` | Lists all assigned variable names |
| Count functions | `count functions` | Returns total number of defined functions |
| Show AST | `show AST` | Dumps the full abstract syntax tree |
| Detect unused variables | `find unused variables` | Identifies variables assigned but never used |
| Generate IR | `generate IR` | Produces an intermediate representation |
| Generate CFG | `show CFG` | Outputs a control flow graph |
| Explain errors | `explain SyntaxError` | Matches errors against a known dataset |
| Evaluate accuracy | `evaluate model` | Runs accuracy check over 50 dataset samples |


4. Tech Stack

- Python 3.8+
- [Streamlit](https://streamlit.io/) — web UI
- `ast` — Python's built-in Abstract Syntax Tree module
- graphviz — visual Control Flow Graph rendering
- JSON — error explanation dataset (`dataset.json`)

5. Project Structure
nlp-interface/
├── app.py            # Main Streamlit application
├── utils.py          # Core analysis functions (AST, CFG, IR, etc.)
├── dataset.json      # Error messages and explanations dataset
├── requirements.txt  # Python dependencies
└── README.md

6. Key modules

`app.py`— Handles the Streamlit UI, user input, query routing, and evaluation logic.

`utils.py` — Contains all analysis functions:
- `interpret_query(query)` — maps natural language to an action string
- `get_variables(tree)` — extracts assigned variable names from the AST
- `count_functions(tree)` — counts `def` statements
- `show_ast(tree)` — returns a formatted AST dump
- `find_unused_variables(tree)` — detects assigned-but-unreferenced variables
- `generate_ir(tree)` — walks the AST to produce IR lines
- `generate_cfg(tree)` — builds a basic control flow graph
- `explain_error(query, data)` — looks up an error in the dataset
- `load_errors()` — loads `dataset.json`

7. Prerequisites

- Python 3.8 or higher
- pip
- Graphviz (system install — see Installation)

8. Installation

1. Clone the repository

git clone https://github.com/LavanyaVarthyavath/NLP-Interface.git
cd NLP-Interface

2. (Optional but recommended) Create a virtual environment

python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

3. Install dependencies

python -m pip install -r requirements.txt

# Windows: download from https://graphviz.org/download/ and add to PATH
# Linux:
sudo apt install graphviz
# macOS:
brew install graphviz
Or manually:
pip install streamlit

4. Run the app
python -m streamlit run app.py

5. Open in your browser

http://localhost:8501

9.. Usage

1. Paste any valid Python code into the **left panel**
2. Type a natural language query into the **right panel**
3. Click **Run Query**
4. View the result instantly below

10. Query Reference

| What you want | Example query |
|---|---|
| List all variables | `"List all variables"` / `"find variables"` |
| Count functions | `"Count functions"` / `"how many functions"` |
| View the AST | `"Show AST"` / `"display AST"` |
| Find unused variables | `"Find unused variables"` / `"unused vars"` |
| Intermediate representation | `"Generate IR"` |
| Control flow graph | `"Show CFG"` / `"generate CFG"` |
| Explain an error | `"Explain SyntaxError"` / `"what is NameError"` |
| Run evaluation | `"Evaluate model"` / `"check accuracy"` |

Queries are matched loosely — you don't need exact wording.


11.How It Works
User Input (code + query)
        │
        ▼
  ast.parse(code)  ──►  AST Tree
        │
        ▼
  interpret_query(query)  ──►  action string
        │
        ▼
  Route to handler:
  ┌─────────────────────────────────┐
  │  "variables"  → get_variables() │
  │  "functions"  → count_functions()│
  │  "ast"        → show_ast()      │
  │  "unused"     → find_unused_variables() │
  │  "ir"         → generate_ir()   │
  │  "cfg"        → generate_cfg()  │
  │  "error"      → explain_error() │
  │  "evaluate"   → evaluate()      │
  └─────────────────────────────────┘
        │
        ▼
  Streamlit renders result

12. Evaluation

The evaluation module tests how accurately the system explains Python errors.

- Runs against the first **50 entries** in `dataset.json`
- For each entry, it calls `explain_error()` and checks whether the expected explanation appears in the predicted output
- Reports a **percentage accuracy score**

To trigger it, type any of: `"evaluate model"`, `"check accuracy"`, `"run evaluation"`


13. Error Handling

| Scenario | Behaviour |
|---|---|
| No code entered | Warning: `"Please enter code."` |
| No query entered | Warning: `"Please enter a query."` |
| Invalid Python syntax in input | Error shown via `st.error()` |
| Query not recognised | Info: `"Query not understood. Try different wording."` |
| Error not found in dataset | Info: `"Error not found in dataset."` |

14. Future Improvements

- [ ] CFG visualization using a graph rendering library (e.g. `graphviz`, `networkx`)
- [ ] Advanced NLP query understanding (e.g. spaCy, sentence transformers)
- [ ] Support for additional languages (JavaScript, C, Java)
- [ ] Improved evaluation metrics: Precision, Recall, F1-score
- [ ] Downloadable analysis reports (PDF/JSON export)
- [ ] File upload support (analyze `.py` files directly)

---

15. Author

Lavanya Varthyavath

- GitHub: @LavanyaVarthyavath
- Email: vl24csb0b83@gmail.com

16. License

This project is licensed under the [MIT License](LICENSE).
MIT License

Copyright (c) 2025 Lavanya Varthyavath

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
