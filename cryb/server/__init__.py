import subprocess
import pathlib

from cryb import common


class ServerEntryPoint(common.EntryPoint):
    name = 'server'
    description = 'Cryb Server Orchestrator'

    def run(self, options):
        file_path = pathlib.Path(__file__)
        subprocess.run(
                ['docker-compose', 'up'],
                cwd=file_path.parent.as_posix(),
        )

    def build_parser(self, parser):
        pass


if __name__ == '__main__':
    ServerEntryPoint.main()
