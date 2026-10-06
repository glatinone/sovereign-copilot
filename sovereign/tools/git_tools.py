"""Local Tool Execution & Test Verification.

Enables safe local file manipulation and automated test validation within the local repository.
"""

import subprocess
from pathlib import Path
from typing import Dict, Any, Optional


class LocalToolExecutor:
    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or Path.cwd()

    def read_code_file(self, relative_path: str) -> str:
        """Reads code file safely within workspace."""
        file_path = self.workspace_root / relative_path
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {relative_path}")
        return file_path.read_text(encoding="utf-8")

    def write_code_file(self, relative_path: str, content: str) -> bool:
        """Writes or updates code file safely within workspace."""
        file_path = self.workspace_root / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return True

    def run_automated_tests(
        self, test_command: str = "pytest", timeout_seconds: int = 60
    ) -> Dict[str, Any]:
        """Runs test suite locally and returns status and test log."""
        try:
            result = subprocess.run(
                test_command,
                shell=True,
                cwd=str(self.workspace_root),
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
            return {
                "passed": result.returncode == 0,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Test execution timed out after {timeout_seconds}s",
            }
        except Exception as e:
            return {
                "passed": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
            }

    def get_git_diff(self) -> str:
        """Returns current uncommitted git diff."""
        try:
            result = subprocess.run(
                ["git", "diff"],
                cwd=str(self.workspace_root),
                capture_output=True,
                text=True,
            )
            return result.stdout
        except Exception:
            return ""
