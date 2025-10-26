from Functions.shell import Shell
quit_commands = {'q!', 'Q!', 'quit', 'QUIT'}

def __main__():
    try:
        shell = Shell()
        while True:
            try:
                command = input(shell.prompt)
                if len(command):
                    if command.strip() in quit_commands:
                        break
                    else:
                        shell.fetch(command.strip())
            except KeyboardInterrupt:
                print()
                continue
            except Exception as e:
                print("...[ERROR]:", e)
                continue
    except Exception as e:
        print(e)
if __name__ == '__main__':
    __main__()
