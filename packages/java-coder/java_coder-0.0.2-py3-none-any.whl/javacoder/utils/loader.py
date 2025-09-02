import subprocess


def load_content(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as file:
        full_content = file.read()
    return full_content


def get_git_config_property(git_property):
    return subprocess.check_output(['git', 'config', git_property]).strip().decode('utf-8')


def get_run_command_output(command):
    process = subprocess.run(command, capture_output=True, text=True, shell=True)
    if process.returncode == 0:
        return process.stdout.strip()
    else:
        raise Exception(process.stderr)
