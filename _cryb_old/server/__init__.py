import subprocess
import pathlib

from cryb import common


class ServerEntryPoint(common.EntryPoint):
    name = 'server'
    description = 'Cryb Server Orchestrator'

    def run(self, options):
        file_path = pathlib.Path(__file__)
        docker_compose_file_path = file_path.parent.as_posix()
        try:
            subprocess.run(
                ['docker-compose', 'up'],
                cwd=docker_compose_file_path,
            )
        except KeyboardInterrupt:
            subprocess.run(
                ['docker-compose', 'stop'],
                cwd=docker_compose_file_path,
            )

    def build_parser(self, parser):
        pass


if __name__ == '__main__':
    ServerEntryPoint.main()
