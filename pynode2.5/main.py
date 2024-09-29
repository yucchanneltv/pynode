import tkinter as tk
import re
import os
import asyncio

class Lexer:
    def __init__(self, code):
        self.code = code
        self.tokens = self.lazy_tokenize()

    def lazy_tokenize(self):
        pattern = r'\s*(let|const|var|delete|print|console\.log|if|else|switch|case|default|for|while|do|function|return|call|async|await|Promise|push|pop|shift|unshift|slice|splice|new|Object\.assign|Object\.keys|[a-zA-Z_]\w*|[0-9]+|".*?"|[=+();{}])\s*'
        return (token for token in re.findall(pattern, self.code))

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.next_token()

    def next_token(self):
        try:
            self.current_token = next(self.tokens)
        except StopIteration:
            self.current_token = None

    def parse(self):
        ast = []
        while self.current_token is not None:
            if self.current_token in ('let', 'const', 'var'):
                var_name = next(self.tokens, None)
                next(self.tokens, None)  # '='
                value = next(self.tokens, None)
                ast.append({'type': 'variable_assignment', 'name': var_name, 'value': value})
            elif self.current_token in ('print', 'console.log'):
                value = next(self.tokens, None)
                ast.append({'type': 'print', 'value': value})
            elif self.current_token == 'if':
                condition = next(self.tokens, None)
                body = []
                next(self.tokens, None)  # '{'
                while self.current_token != '}' and self.current_token is not None:
                    body.append(self.current_token)
                    self.next_token()
                next(self.tokens, None)  # '}'
                ast.append({'type': 'if', 'condition': condition, 'body': body})
            elif self.current_token == 'for':
                var_name = next(self.tokens, None)
                next(self.tokens, None)  # 'in'
                collection = next(self.tokens, None)
                body = []
                next(self.tokens, None)  # '{'
                while self.current_token != '}' and self.current_token is not None:
                    body.append(self.current_token)
                    self.next_token()
                next(self.tokens, None)  # '}'
                ast.append({'type': 'for', 'var': var_name, 'collection': collection, 'body': body})
            else:
                self.next_token()
        return ast

class Interpreter:
    def __init__(self, ast):
        self.ast = ast
        self.variables = {}

    async def interpret(self):
        for node in self.ast:
            if node['type'] == 'variable_assignment':
                self.variables[node['name']] = node['value']
            elif node['type'] == 'print':
                value = node['value']
                print(self.variables.get(value, value))
            elif node['type'] == 'if':
                condition = node['condition']
                if self.variables.get(condition) == 'true':
                    print("If condition met:", node['body'])
            elif node['type'] == 'for':
                collection = self.variables.get(node['collection'], [])
                for item in collection:
                    self.variables[node['var']] = item
                    print(f"For loop item: {item}, Body: {node['body']}")
                    await asyncio.sleep(0)  # 非同期で処理を続ける

async def run_code(code):
    lexer = Lexer(code)
    parser = Parser(lexer.tokens)
    ast = parser.parse()
    interpreter = Interpreter(ast)
    await interpreter.interpret()

class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PN Launcher Ver3")
        self.command_entry = tk.Entry(root, width=50)
        self.command_entry.pack(pady=20)
        self.run_button = tk.Button(root, text="Run", command=self.run_command)
        self.run_button.pack(pady=10)
        self.output_frame = tk.Frame(root)
        self.output_frame.pack(pady=20)
        self.output_text = tk.Text(self.output_frame, height=10, width=50)
        self.output_text.pack()

    def run_command(self):
        command = self.command_entry.get()
        if command.startswith("start "):
            file_name = command.split(" ", 1)[1].strip()
            self.run_file(file_name)
        else:
            self.output_text.insert(tk.END, "Unknown command.\n")

    def run_file(self, file_name):
        if os.path.exists(file_name) and file_name.endswith('.pn'):
            with open(file_name, 'r', buffering=1) as file:  # Buffered I/O
                code = file.read()
            self.output_text.delete(1.0, tk.END)  # Clear previous output
            asyncio.run(run_code(code))  # 非同期でコードを実行
        else:
            self.output_text.insert(tk.END, "File not found or invalid extension.\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = LauncherApp(root)
    root.mainloop()
