import subprocess
import re

elf_file = "/flag"

proc = subprocess.Popen([elf_file],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True)

output = proc.stdout.readline().strip()
print(f"[+] Execute Sucess: {output}")

expr_match = re.search(r"([\d\s\+\-\*/]+)= \?", output)
if not expr_match:
    print("[!] Faied to Extrict Formula")
    proc.kill()
    exit(1)

expr = expr_match.group(1).strip()
print(f"[+] Formula: {expr}")

try:
    result_value = eval(expr)
    print(f"[+] Calculation Result: {expr} = {result_value}")
except Exception as e:
    print(f"[!] Calculation Failed: {e}")
    proc.kill()
    exit(1)

proc.stdin.write(f"{result_value}\n")
proc.stdin.flush()

remaining_output = proc.stdout.read()
if remaining_output:
    print("[+] Extra Execute:")
    print(remaining_output.strip())

proc.wait()

