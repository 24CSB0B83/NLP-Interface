import ast
import json

# -------- VARIABLES -------- #

class VariableVisitor(ast.NodeVisitor):
    def __init__(self):
        self.vars = set()

    def visit_Name(self, node):
        self.vars.add(node.id)

def get_variables(tree):
    visitor = VariableVisitor()
    visitor.visit(tree)
    return visitor.vars


# -------- FUNCTIONS -------- #

class FunctionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.count = 0

    def visit_FunctionDef(self, node):
        self.count += 1

def count_functions(tree):
    visitor = FunctionVisitor()
    visitor.visit(tree)
    return visitor.count


# -------- AST -------- #

def show_ast(tree):
    return ast.dump(tree, indent=2)


# -------- UNUSED VARIABLES -------- #

def find_unused_variables(tree):
    assigned = set()
    used = set()

    class Analyzer(ast.NodeVisitor):
        def visit_Assign(self, node):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    assigned.add(t.id)
            self.generic_visit(node)

        def visit_Name(self, node):
            used.add(node.id)

    Analyzer().visit(tree)
    return assigned - used


# -------- IR -------- #

def generate_ir(tree):
    ir = []
    temp_count = 1

    ops = {
        ast.Add: "+",
        ast.Sub: "-",
        ast.Mult: "*",
        ast.Div: "/"
    }

    class IRGenerator(ast.NodeVisitor):
        def visit_Assign(self, node):
            nonlocal temp_count

            if isinstance(node.value, ast.BinOp):
                left = node.value.left.id if isinstance(node.value.left, ast.Name) else node.value.left.value
                right = node.value.right.id if isinstance(node.value.right, ast.Name) else node.value.right.value

                op = ops.get(type(node.value.op), "?")

                temp = f"t{temp_count}"
                temp_count += 1

                ir.append(f"{temp} = {left} {op} {right}")

                for target in node.targets:
                    ir.append(f"{target.id} = {temp}")

            self.generic_visit(node)

    IRGenerator().visit(tree)
    return ir


# -------- CFG -------- #

def generate_cfg(tree):
    cfg = {}
    node_id = 1

    class CFGBuilder(ast.NodeVisitor):
        def visit(self, node):
            nonlocal node_id
            current = f"N{node_id}"
            node_id += 1

            cfg[current] = []

            for child in ast.iter_child_nodes(node):
                child_id = f"N{node_id}"
                cfg[current].append(child_id)
                self.visit(child)

    CFGBuilder().visit(tree)
    return cfg


# -------- ERROR EXPLANATION -------- #

def load_errors():
    try:
        with open("dataset.json") as f:
            return json.load(f)
    except:
        return []

def explain_error(query, data):
    query = query.lower()

    best_match = None
    max_score = 0

    for item in data:
        error_msg = item["error_message"].lower()
        
        score = sum(1 for word in query.split() if word in error_msg)

        if score > max_score:
            max_score = score
            best_match = item

    if best_match:
        return best_match["explanation"]

    return None


# -------- QUERY INTERPRETER -------- #

def interpret_query(query):
    query = query.lower()

    if "variable" in query:
        return "variables"
    elif "function" in query:
        return "functions"
    elif "ast" in query:
        return "ast"
    elif "unused" in query:
        return "unused"
    elif "ir" in query:
        return "ir"
    elif "cfg" in query:
        return "cfg"
    elif "error" in query or "exception" in query:
        return "error"
    else:
        return "unknown"