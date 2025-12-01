import subprocess
import sys

def run_sudo_netstat(password):
    command = "sudo netstat -tulnp | grep 8001"
    
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate(input=password + '\n')

        if process.returncode == 0:
            print("--- Netstat Output ---")
            print(stdout)
        else:
            print("--- Stderr ---")
            print(stderr)
            print("Command failed with exit code:", process.returncode)

    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    # The user will manually provide the password in a separate terminal.
    # The script will use the provided password.
    run_sudo_netstat("kB230515yB")

