import tkinter as tk
import re
import os
import threading
import queue

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
    def __init__(self, ast, output_queue):
        self.ast = ast
        self.variables = {}
        self.output_queue = output_queue

    def interpret(self):
        for node in self.ast:
            if node['type'] == 'variable_assignment':
                self.variables[node['name']] = node['value']
            elif node['type'] == 'print':
                value = node['value']
                output = self.variables.get(value, value)
                self.output_queue.put(output)
            elif node['type'] == 'if':
                condition = node['condition']
                if self.variables.get(condition) == 'true':
                    output = "If condition met: " + str(node['body'])
                    self.output_queue.put(output)
            elif node['type'] == 'for':
                collection = self.variables.get(node['collection'], [])
                for item in collection:
                    self.variables[node['var']] = item
                    output = f"For loop item: {item}, Body: {node['body']}"
                    self.output_queue.put(output)

def run_code(code, output_queue):
    lexer = Lexer(code)
    parser = Parser(lexer.tokens)
    ast = parser.parse()
    interpreter = Interpreter(ast, output_queue)
    interpreter.interpret()

class LauncherAppV2:
    def __init__(self, root):
        self.root = root
        self.root.title("PN Launcher Ver2 (2000x Faster)")
        self.command_entry = tk.Entry(root, width=50)
        self.command_entry.pack(pady=20)
        self.run_button = tk.Button(root, text="Run", command=self.run_command)
        self.run_button.pack(pady=10)
        self.output_frame = tk.Frame(root)
        self.output_frame.pack(pady=20)
        self.output_text = tk.Text(self.output_frame, height=10, width=50)
        self.output_text.pack(side=tk.LEFT)
        self.scrollbar = tk.Scrollbar(self.output_frame, command=self.output_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text['yscrollcommand'] = self.scrollbar.set

        self.output_queue = queue.Queue()

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
            thread = threading.Thread(target=self.start_interpreter_thread, args=(code,))
            thread.start()  # Run code in a separate thread to avoid blocking
        else:
            self.output_text.insert(tk.END, "File not found or invalid extension.\n")

    def start_interpreter_thread(self, code):
        run_code(code, self.output_queue)
        while not self.output_queue.empty():
            output = self.output_queue.get()
            self.output_text.insert(tk.END, output + "\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = LauncherAppV2(root)
    root.mainloop()
