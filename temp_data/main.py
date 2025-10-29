import os

n = 1
for file_name in os.listdir('.'):
    x = file_name.split('.')[0]
    print(n)
    print("py -3.11 -m venv .venv")
    print("Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned")
    print(".\.venv\Scripts\Activate.ps1")
    print("pip install -r requirements.txt")
    print(f'python main.py --input "{x}.txt" --output "{x} b.txt"')
    print()
    n+=1
# py -3.11 -m venv .venv
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
# .\.venv\Scripts\Activate.ps1
# pip install -r requirements.txt
# python main.py --input "source.txt" --output "source b.txt"
