 Natural Language Query Interface for Compiler

 1. Overview

This project is a "Streamlit-based web application" that allows users to analyze Python code using "natural language queries".

Instead of writing complex analysis programs, users can simply type queries like "find variables" or "generate CFG". The system processes the code using Python’s 'Abstract Syntax Tree (AST)'.
Additionally, the system includes an **evaluation module** to measure the accuracy of error explanations.

 2. Features

* Extract variables from Python code
* Count number of functions
* Display Abstract Syntax Tree (AST)
* Detect unused variables
* Generate Intermediate Representation (IR)
* Generate Control Flow Graph (CFG)
* Explain Python errors using dataset
* Evaluate model accuracy

3. Technologies Used

* Python
* Streamlit
* AST (Abstract Syntax Tree)
* JSON (for dataset)

 4. How to Run the Project

 4.1 Install Dependencies
python -m pip install streamlit

4.2 Run the Application
python -m streamlit run app.py

4.3 Open in Browser
http://localhost:8501

5. How to Use

1. Enter Python code in the left panel
2. Enter a natural language query in the right panel
3. Click "Run Query"
4. View results instantly

 6. Example Queries

* "List all variables"
* "Count functions"
* "Show AST"
* "Find unused variables"
* "Generate IR"
* "Show CFG"
* "Explain SyntaxError"
* "Evaluate model"
* "Check accuracy"

 7. Project Structure

nlp-interface
│── app.py
│── utils.py
│── dataset.json
│── README.md

8. Internal Working

* User query is interpreted using `interpret_query()`
* Code is parsed using `ast.parse()`
* Based on query, corresponding functions are executed:

  * `get_variables()`
  * `count_functions()`
  * `show_ast()`
  * `find_unused_variables()`
  * `generate_ir()`
  * `generate_cfg()`
  * `explain_error()`
  * `evaluate()`

 9. Evaluation Feature

The system evaluates its performance using a dataset of error messages:

* Compares predicted explanation with actual explanation
* Calculates accuracy percentage
* Displays result in the UI

 10. Error Handling

* Warns if code or query is empty
* Handles syntax errors in input code
* Handles unknown queries gracefully

 11. Future Improvements

* CFG visualization using graphs
* Advanced NLP understanding
* Support for multiple programming languages
* Improved evaluation metrics (Precision, Recall)

--Author

Lavanya Varthyavath
