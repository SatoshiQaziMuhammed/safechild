    1 import subprocess
    2 import sys
    3
    4 def run_sudo_netstat(password):
    5     command = "sudo netstat -tulnp | grep 8001"
    6
    7     try:
    8         # Start the subprocess, connecting stdin to a pipe
    9         process = subprocess.Popen(
   10             command,
   11             shell=True,
   12             stdin=subprocess.PIPE,
   13             stdout=subprocess.PIPE,
   14             stderr=subprocess.PIPE,
   15             text=True
   16         )
   17
   18         # Send the password to stdin
   19         stdout, stderr = process.communicate(input=password + '\n')
   20
   21         if process.returncode == 0:
   22             print("Stdout:\n", stdout)
   23         else:
   24             print("Stderr:\n", stderr)
   25             print("Command failed with exit code:", process.returncode)
   26
   27     except Exception as e:
   28         print("An error occurred:", e)
   29
   30 if __name__ == "__main__":
   31     # In a real scenario, you would get the password securely,
   32     # but for this specific tool interaction, it's passed directly.
   33     # The user will manually provide it in the terminal.
   34     print("Please manually enter the sudo password in the terminal when prompted.")
   35     print("Executing: sudo netstat -tulnp | grep 8001")
   36     # You will provide the password 'kB230515yB' in the *other* terminal when prompted.
   37     # The script waits for your input.
   38     run_sudo_netstat("kB230515yB")