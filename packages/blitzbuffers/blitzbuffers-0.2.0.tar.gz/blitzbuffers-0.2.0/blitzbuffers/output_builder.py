import os


class OutputBuilder:

    def __init__(self, indent_size=4):
        self.parts = []
        self.current_indent = 0
        self.indent_size = indent_size

    def add_line(self, line):
        if self.current_indent > 0 and len(line) > 0:
            self.parts.append(" " * self.current_indent)
        self.parts.append(line)
        self.parts.append("\n")

    def add_lines(self, *lines):
        for line in lines:
            if self.current_indent > 0 and len(line) > 0:
                self.parts.append(" " * self.current_indent)
            self.parts.append(line)
            self.parts.append("\n")

    def add_line_unindented(self, line):
        self.parts.append(line)
        self.parts.append("\n")

    def add_line_without_newline(self, line):
        if self.current_indent > 0 and len(line) > 0:
            self.parts.append(" " * self.current_indent)
        self.parts.append(line)

    def add_line_pre_newline(self, line):
        self.parts.append("\n")
        if self.current_indent > 0 and len(line) > 0:
            self.parts.append(" " * self.current_indent)
        self.parts.append(line)

    def add_text(self, text):
        self.parts.append(text)

    def add_file_contents(self, path):
        script_dir = os.path.dirname(__file__)
        with open(os.path.join(script_dir, path), "r") as file:
            self.parts.append(file.read())

    def skip_line(self, skip_amount=1):
        self.parts.append("\n" * skip_amount)

    def increment_indent(self, times=1):
        self.current_indent += self.indent_size * times

    def decrement_indent(self, times=1):
        change = self.indent_size * times
        if self.current_indent < change:
            raise Exception("Tried to decrement indent further than 0.")
        self.current_indent -= change

    def make(self):
        return "".join(self.parts)
