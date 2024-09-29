import tkinter as tk
import re
import os
import threading

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
    def __init__(self, ast, output_callback):
        self.ast = ast
        self.variables = {}
        self.output_callback = output_callback  # 出力のためのコールバック関数

    def interpret(self):
        for node in self.ast:
            if node['type'] == 'variable_assignment':
                self.variables[node['name']] = node['value']
            elif node['type'] == 'print':
                value = node['value']
                output_value = self.variables.get(value, value)
                self.output_callback(output_value)  # 結果を表示
            elif node['type'] == 'if':
                condition = node['condition']
                if self.variables.get(condition) == 'true':
                    self.output_callback(f"If condition met: {node['body']}")
            elif node['type'] == 'for':
                collection = self.variables.get(node['collection'], [])
                for item in collection:
                    self.variables[node['var']] = item
                    self.output_callback(f"For loop item: {item}, Body: {node['body']}")

def run_code(code, output_callback):
    lexer = Lexer(code)
    parser = Parser(lexer.tokens)
    ast = parser.parse()
    interpreter = Interpreter(ast, output_callback)
    interpreter.interpret()

class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PN2 Launcher")

        self.command_entry = tk.Entry(root, width=50)
        self.command_entry.pack(pady=20)

        self.run_button = tk.Button(root, text="Run", command=self.run_command)
        self.run_button.pack(pady=10)

        # 出力用のフレームを作成
        self.output_frame = tk.Frame(root)
        self.output_frame.pack(pady=20)

    def run_command(self):
        command = self.command_entry.get()
        if command.startswith("start "):
            file_name = command.split(" ", 1)[1].strip()
            self.run_file(file_name)
        else:
            self.display_output("Unknown command.")

    def run_file(self, file_name):
        if os.path.exists(file_name) and file_name.endswith('.pn'):
            with open(file_name, 'r', buffering=1) as file:
                code = file.read()
            self.clear_output()  # 前回の出力をクリア
            thread = threading.Thread(target=run_code, args=(code, self.display_output))
            thread.start()
        else:
            self.display_output("File not found or invalid extension.")

    def display_output(self, text):
        # 新しい出力をフレーム内にラベルとして表示
        output_label = tk.Label(self.output_frame, text=text, anchor="w")
        output_label.pack(fill='x')

    def clear_output(self):
        # 出力フレームをクリア
        for widget in self.output_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = LauncherApp(root)
    root.mainloop()
