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
                left = node.value.left.id if isinstance(node.value.left, ast.Name) else str(node.value.left.value) if isinstance(node.value.left, ast.Constant) else "?"
                right = node.value.right.id if isinstance(node.value.right, ast.Name) else str(node.value.right.value) if isinstance(node.value.right, ast.Constant) else "?"

                op = ops.get(type(node.value.op), "?")

                temp = f"t{temp_count}"
                temp_count += 1

                ir.append(f"{temp} = {left} {op} {right}")

                for target in node.targets:
                    if isinstance(target, ast.Name):
                        ir.append(f"{target.id} = {temp}")

            elif isinstance(node.value, ast.Constant):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        ir.append(f"{target.id} = {node.value.value}")

            elif isinstance(node.value, ast.Name):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        ir.append(f"{target.id} = {node.value.id}")

            self.generic_visit(node)

        def visit_Return(self, node):
            nonlocal temp_count
            if isinstance(node.value, ast.Name):
                ir.append(f"RETURN {node.value.id}")
            elif isinstance(node.value, ast.Constant):
                ir.append(f"RETURN {node.value.value}")
            elif isinstance(node.value, ast.BinOp):
                left = node.value.left.id if isinstance(node.value.left, ast.Name) else str(node.value.left.value) if isinstance(node.value.left, ast.Constant) else "?"
                right = node.value.right.id if isinstance(node.value.right, ast.Name) else str(node.value.right.value) if isinstance(node.value.right, ast.Constant) else "?"
                op = ops.get(type(node.value.op), "?")
                temp = f"t{temp_count}"
                temp_count += 1
                ir.append(f"{temp} = {left} {op} {right}")
                ir.append(f"RETURN {temp}")
            self.generic_visit(node)

        def visit_FunctionDef(self, node):
            ir.append(f"FUNC {node.name}({', '.join(a.arg for a in node.args.args)}):")
            self.generic_visit(node)

        def visit_If(self, node):
            nonlocal temp_count
            if isinstance(node.test, ast.Compare):
                left = node.test.left.id if isinstance(node.test.left, ast.Name) else str(node.test.left.value)
                op = ast.dump(node.test.ops[0]).split("(")[0]
                right = node.test.comparators[0].id if isinstance(node.test.comparators[0], ast.Name) else str(node.test.comparators[0].value)
                ir.append(f"IF {left} {op} {right} GOTO true_branch ELSE false_branch")
            self.generic_visit(node)

    IRGenerator().visit(tree)
    return ir


# -------- CFG (PROPER CONTROL FLOW GRAPH) -------- #

def generate_cfg(tree):
    cfg = {}

    def get_label(node):
        """Return a human-readable label for an AST node."""
        if isinstance(node, ast.FunctionDef):
            return f"def {node.name}()"
        elif isinstance(node, ast.If):
            try:
                return f"if {ast.unparse(node.test)}"
            except:
                return "if <condition>"
        elif isinstance(node, ast.For):
            try:
                return f"for {ast.unparse(node.target)} in {ast.unparse(node.iter)}"
            except:
                return "for <loop>"
        elif isinstance(node, ast.While):
            try:
                return f"while {ast.unparse(node.test)}"
            except:
                return "while <condition>"
        elif isinstance(node, ast.Assign):
            try:
                return ast.unparse(node)
            except:
                return "assignment"
        elif isinstance(node, ast.Return):
            try:
                return f"return {ast.unparse(node.value)}"
            except:
                return "return"
        elif isinstance(node, ast.Expr):
            try:
                return ast.unparse(node)
            except:
                return "expression"
        elif isinstance(node, ast.Import):
            return f"import {', '.join(a.name for a in node.names)}"
        elif isinstance(node, ast.ImportFrom):
            return f"from {node.module} import ..."
        else:
            return type(node).__name__

    def build_cfg(stmts, prefix=""):
        """Build CFG nodes for a list of statements, returns list of node keys."""
        keys = []
        for i, stmt in enumerate(stmts):
            label = get_label(stmt)
            key = label

            # Handle duplicate labels by appending index
            original_key = key
            count = 1
            while key in cfg:
                key = f"{original_key} [{count}]"
                count += 1

            cfg[key] = []
            keys.append(key)

            # Handle branching nodes
            if isinstance(stmt, ast.If):
                # True branch
                if stmt.body:
                    true_keys = build_cfg(stmt.body, prefix + "  ")
                    if true_keys:
                        cfg[key].append(f"[True] {true_keys[0]}")
                        for j in range(len(true_keys) - 1):
                            if true_keys[j] in cfg:
                                cfg[true_keys[j]].append(true_keys[j + 1])

                # False branch (else)
                if stmt.orelse:
                    false_keys = build_cfg(stmt.orelse, prefix + "  ")
                    if false_keys:
                        cfg[key].append(f"[False] {false_keys[0]}")
                        for j in range(len(false_keys) - 1):
                            if false_keys[j] in cfg:
                                cfg[false_keys[j]].append(false_keys[j + 1])
                else:
                    cfg[key].append("[False] → next")

            elif isinstance(stmt, ast.For) or isinstance(stmt, ast.While):
                # Loop body
                if stmt.body:
                    body_keys = build_cfg(stmt.body, prefix + "  ")
                    if body_keys:
                        cfg[key].append(f"[Loop] {body_keys[0]}")
                        for j in range(len(body_keys) - 1):
                            if body_keys[j] in cfg:
                                cfg[body_keys[j]].append(body_keys[j + 1])
                        # Loop back edge
                        if body_keys[-1] in cfg:
                            cfg[body_keys[-1]].append(f"[Back] {key}")
                cfg[key].append("[Exit loop]")

            elif isinstance(stmt, ast.FunctionDef):
                # Function body
                if stmt.body:
                    body_keys = build_cfg(stmt.body, prefix + "  ")
                    if body_keys:
                        cfg[key].append(body_keys[0])
                        for j in range(len(body_keys) - 1):
                            if body_keys[j] in cfg:
                                cfg[body_keys[j]].append(body_keys[j + 1])

        # Chain sequential statements
        for i in range(len(keys) - 1):
            if keys[i] in cfg and not isinstance(stmts[i], (ast.If, ast.For, ast.While, ast.FunctionDef)):
                cfg[keys[i]].append(keys[i + 1])

        return keys

    # Start with START node
    cfg["START"] = []

    if isinstance(tree, ast.Module) and tree.body:
        top_keys = build_cfg(tree.body)
        if top_keys:
            cfg["START"].append(top_keys[0])

    # Add END node
    cfg["END"] = []

    # Connect leaf nodes (nodes with no outgoing edges) to END
    for key in list(cfg.keys()):
        if key != "END" and key != "START" and not cfg[key]:
            cfg[key].append("END")

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

    if "variable" in query and "unused" not in query:
        return "variables"
    elif "function" in query or "def" in query:
        return "functions"
    elif "ast" in query or "syntax tree" in query:
        return "ast"
    elif "unused" in query:
        return "unused"
    elif "ir" in query or "intermediate" in query:
        return "ir"
    elif "cfg" in query or "control flow" in query or "flow graph" in query:
        return "cfg"
    elif "evaluate" in query or "accuracy" in query or "check" in query:
        return "evaluate"
    elif "error" in query or "exception" in query or "explain" in query:
        return "error"
    else:
        return "unknown"
