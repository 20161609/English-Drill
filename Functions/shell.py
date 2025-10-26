import os, sys

TITLE_NAME = 'CLI Translation Practice (GLOBAL → Target=en)'

class Shell:
    def __init__(self):
        print(f"\"Welcome to {TITLE_NAME}\"")
        self.prompt = '>>> '
        print("Type 'help' for commands.")

    def fetch(self, command: str):
        pass