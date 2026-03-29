import streamlit as st
import ast
import graphviz
from utils import *

# ------------------ Evaluation Function ------------------
def evaluate(explainer, dataset):
    correct = 0
    total = len(dataset[:50])

    for item in dataset[:50]:
        pred = explainer.explain(item["error_message"])
        if item["explanation"].lower() in pred["explanation"].lower():
            correct += 1

    return round(correct / total * 100, 2)


# ------------------ Streamlit UI ------------------
st.set_page_config(page_title="NL Query Interface", layout="wide")

st.title("🧠 Natural Language Query Interface for Compiler")
st.markdown("Ask questions about your Python code in plain English!")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 💻 Python Code")
    code = st.text_area("Enter your Python code here:", height=300, label_visibility="collapsed")

with col2:
    st.markdown("### ❓ Your Query")
    query = st.text_input("Type your query (e.g. 'show CFG', 'find unused variables'):", label_visibility="collapsed")

    st.markdown("**💡 Example Queries:**")
    examples = [
        "List all variables",
        "Count functions",
        "Show AST",
        "Find unused variables",
        "Generate IR",
        "Show CFG",
        "Explain SyntaxError",
        "Evaluate model",
    ]
    cols = st.columns(2)
    for i, ex in enumerate(examples):
        cols[i % 2].caption(f"• {ex}")

st.markdown("---")

# ------------------ Main Logic ------------------
if st.button("🚀 Run Query", use_container_width=True):

    if not code:
        st.warning("⚠️ Please enter some Python code.")
    elif not query:
        st.warning("⚠️ Please enter a query.")
    else:
        try:
            tree = ast.parse(code)
            action = interpret_query(query)

            st.subheader("📊 Result")

            # -------- Variables --------
            if action == "variables":
                variables = get_variables(tree)
                if variables:
                    st.success(f"✅ Found {len(variables)} variable(s):")
                    for v in variables:
                        st.markdown(f"- `{v}`")
                else:
                    st.info("No variables found.")

            # -------- Functions --------
            elif action == "functions":
                count = count_functions(tree)
                st.success(f"✅ Number of functions defined: **{count}**")

            # -------- AST --------
            elif action == "ast":
                st.markdown("#### 🌳 Abstract Syntax Tree")
                st.code(show_ast(tree), language="python")

            # -------- Unused Variables --------
            elif action == "unused":
                unused = find_unused_variables(tree)
                if unused:
                    st.warning(f"⚠️ Found {len(unused)} unused variable(s):")
                    for v in unused:
                        st.markdown(f"- `{v}`")
                else:
                    st.success("✅ No unused variables found!")

            # -------- IR --------
            elif action == "ir":
                ir_code = generate_ir(tree)
                st.markdown("#### ⚙️ Intermediate Representation (IR)")
                if ir_code:
                    st.code("\n".join(ir_code), language="python")
                else:
                    st.info("No IR generated.")

            # -------- CFG --------
            elif action == "cfg":
                cfg = generate_cfg(tree)
                st.markdown("#### 🔀 Control Flow Graph (CFG)")

                if cfg:
                    # Render as visual graph using graphviz
                    dot = graphviz.Digraph()
                    dot.attr(rankdir="TB")
                    dot.attr(
                        "node",
                        shape="box",
                        style="filled",
                        fillcolor="#dbeafe",
                        fontname="Helvetica",
                        fontsize="12",
                        color="#1e40af"
                    )
                    dot.attr("edge", color="#374151", fontname="Helvetica", fontsize="10")

                    # Add all nodes first
                    all_nodes = set(cfg.keys())
                    for edges in cfg.values():
                        for e in edges:
                            all_nodes.add(e)

                    for node in all_nodes:
                        if node == "START":
                            dot.node(str(node), str(node), shape="oval", fillcolor="#bbf7d0", color="#15803d")
                        elif node == "END":
                            dot.node(str(node), str(node), shape="oval", fillcolor="#fecaca", color="#b91c1c")
                        else:
                            dot.node(str(node), str(node))

                    # Add edges
                    for node, edges in cfg.items():
                        for edge in edges:
                            dot.edge(str(node), str(edge))

                    st.graphviz_chart(dot.source)

                    # Also show text representation below
                    with st.expander("📄 View CFG as text"):
                        for node, edges in cfg.items():
                            st.text(f"{node} → {edges}")
                else:
                    st.info("No CFG generated for this code.")

            # -------- Error Explanation --------
            elif action == "error":
                data = load_errors()
                explanation = explain_error(query, data)
                st.markdown("#### 🐛 Error Explanation")
                if explanation:
                    st.error(f"**Explanation:** {explanation}")
                else:
                    st.info("Error not found in dataset. Try rephrasing, e.g. 'Explain NameError'.")

            # -------- Evaluation --------
            elif action == "evaluate":
                st.markdown("#### 📈 Evaluation Results")

                data = load_errors()

                with st.spinner("Running evaluation on 50 samples..."):

                    class ExplainerWrapper:
                        def explain(self, error_msg):
                            explanation = explain_error(error_msg, data)
                            return {"explanation": explanation if explanation else ""}

                    explainer = ExplainerWrapper()
                    accuracy = evaluate(explainer, data)

                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Samples Tested", "50")
                col_b.metric("Correct Matches", f"{int(accuracy / 2)}")
                col_c.metric("Accuracy", f"{accuracy}%")

                if accuracy >= 75:
                    st.success(f"✅ Model accuracy: {accuracy}% — Good performance!")
                elif accuracy >= 50:
                    st.warning(f"⚠️ Model accuracy: {accuracy}% — Moderate performance.")
                else:
                    st.error(f"❌ Model accuracy: {accuracy}% — Needs improvement.")

            # -------- Unknown Query --------
            else:
                st.info("🤔 Query not understood. Try rephrasing.")
                st.markdown("**Supported queries:** List variables · Count functions · Show AST · Find unused variables · Generate IR · Show CFG · Explain [ErrorType] · Evaluate model")

        except SyntaxError as e:
            st.error(f"❌ Syntax Error in your code: {e}")
        except Exception as e:
            st.error(f"❌ Error: {e}")
