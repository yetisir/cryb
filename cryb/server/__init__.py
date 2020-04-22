import subprocess

def run():
    file_path = pathlib.Path(__file__)
    subprocess.run(['docker-compose', 'up'], cwd=file_path.parent)
