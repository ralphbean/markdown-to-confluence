import subprocess

import pytest


class Script:
    def __init__(self, root):
        self.root = root
        self.path = root / "test.md"

    def set_content(self, content):
        self.path.write(content)

    def run(self):
        args = [
            "python3",
            "bin/markdown-to-confluence.py",
            "--confluence-url",
            "https://confluence.example.com",
            "--confluence-space",
            "SOME_SPACE",
            "--root",
            self.root,
            "--path",
            ".",
            "--dry-run",
        ]

        with subprocess.Popen(args, stderr=subprocess.PIPE) as proc:
            out = proc.stderr.read().decode()
            print(out)
            return out


@pytest.fixture
def script(tmpdir):
    return Script(tmpdir)
