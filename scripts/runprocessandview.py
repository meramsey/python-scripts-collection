from subprocess import Popen, PIPE, STDOUT
from shlex import split
import sys


def run_command(cmd):
    try:
        print(f"executing: {str(cmd)} ")
        process = Popen(split(cmd), stdout=PIPE, stderr=STDOUT, encoding='utf8')
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                print("no output")
                break
            if output:
                print(output.strip())
        rc = process.poll()
        return rc
    except KeyboardInterrupt:
        # process.terminate()
        exit()
    except Exception as ex:
        print("Encountered an error : ", ex)


# install netcat to use
# run_command('nc -k -l 6514')
run_command('ls -lah')
