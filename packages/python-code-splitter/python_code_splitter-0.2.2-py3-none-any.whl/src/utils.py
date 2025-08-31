import re
import subprocess


def git(sub_command: str):
    command = f"git {sub_command}"
    print(command)
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise Exception(f"Failed to execute the command: {command}. {result.stderr=}")
    return result.stdout.decode("utf-8")


# Function to convert class name to snake case
def to_snake_case(class_name: str) -> str:
    try:
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", class_name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
    except Exception as e:
        print(f"Error: parsing {class_name}. {e}")
        raise
