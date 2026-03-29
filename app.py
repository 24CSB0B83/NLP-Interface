import streamlit as st
import ast
from utils import *

st.set_page_config(page_title="NL Query Interface", layout="wide")

st.title("Natural Language Query Interface for Compiler")
st.markdown("Ask questions about your code in plain English!")

col1, col2 = st.columns(2)

with col1:
    code = st.text_area("💻 Enter Python Code", height=300)

with col2:
    query = st.text_input("❓ Ask your Query")

if st.button("Run Query"):

    if not code:
        st.warning("Please enter code.")
    elif not query:
        st.warning("Please enter a query.")
    else:
        try:
            tree = ast.parse(code)
            action = interpret_query(query)

            st.subheader("📊 Result")

            if action == "variables":
                variables = get_variables(tree)
                st.success(f"Variables found: {variables}")

            elif action == "functions":
                count = count_functions(tree)
                st.success(f"Number of functions: {count}")

            elif action == "ast":
                st.code(show_ast(tree), language="python")

            elif action == "unused":
                unused = find_unused_variables(tree)
                st.warning(f"Unused variables: {unused}")

            elif action == "ir":
                ir_code = generate_ir(tree)
                st.subheader("Intermediate Representation (IR)")
                if ir_code:
                    for line in ir_code:
                        st.text(line) 
                else:
                    st.info("No IR generated.")
                                   
            elif action == "cfg":
                cfg = generate_cfg(tree)
                st.subheader("Control Flow Graph (CFG)")
                for node, edges in cfg.items():
                    st.text(f"{node} -> {edges}") 
                    
            elif action == "error":
                data = load_errors()
                explanation = explain_error(query, data)

                if explanation:
                    st.error(explanation)
                else:
                    st.info("Error not found in dataset.")

            else:
                st.info("Query not understood. Try different wording.")

        except Exception as e:
            st.error(f"Code Error: {e}")