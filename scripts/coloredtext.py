# Colors in Python
# Source: https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal

def prRed(prt): return '\033[91m{}\033[00m'.format(prt)


def prGreen(prt): return '\033[92m{}\033[00m'.format(prt)


def prYellow(prt): return '\033[93m{}\033[00m'.format(prt)


def prLightPurple(prt): return '\033[94m{}\033[00m'.format(prt)


def prPurple(prt): return '\033[95m{}\033[00m'.format(prt)


def prCyan(prt): return '\033[96m{}\033[00m'.format(prt)


def prLightGray(prt): return '\033[97m{}\033[00m'.format(prt)


def prBlack(prt): return '\033[98m{}\033[00m'.format(prt)


print(prRed("Hello world"))
print(prGreen("Hello world"))
print(prYellow("Hello world"))
print(prLightPurple("Hello world"))
print(prPurple("Hello world"))
print(prCyan("Hello world"))
print(prLightGray("Hello world"))
print(prBlack("Hello world"))


def black(text):
    print('\033[30m', text, '\033[0m', sep='')


def red(text):
    print('\033[31m', text, '\033[0m', sep='')


def green(text):
    print('\033[32m', text, '\033[0m', sep='')


def yellow(text):
    print('\033[33m', text, '\033[0m', sep='')


def blue(text):
    print('\033[34m', text, '\033[0m', sep='')


def magenta(text):
    print('\033[35m', text, '\033[0m', sep='')


def cyan(text):
    print('\033[36m', text, '\033[0m', sep='')


def gray(text):
    print('\033[90m', text, '\033[0m', sep='')


black("BLACK")
red("RED")
green("GREEN")
yellow("YELLOW")
blue("BLACK")
magenta("MAGENTA")
cyan("CYAN")
gray("GRAY")
