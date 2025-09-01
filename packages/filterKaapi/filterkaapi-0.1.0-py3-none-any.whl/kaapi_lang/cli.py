import sys
from kaapi_lang.main import run_kaapi, openFile

def main():
    if len(sys.argv) == 1:
        # REPL
        print("Kaapi REPL (type 'exit' to quit)")
        while True:
            code = input(">>> ")
            if code.strip().lower() == "exit":
                break
            run_kaapi(code)
    else:
        filename = sys.argv[1]
        code = openFile(filename)
        run_kaapi(code)
