import subprocess
import json
import tempfile
import os

class TestRunnerService:
    def run_tests(self, test_path: str = "."):
        """
        Run pytest on the specified path and capture the output.
        """
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json") as tmpfile:
            report_path = tmpfile.name

        try:
            command = [
                "pytest",
                test_path,
                "--json-report",
                f"--json-report-file={report_path}",
            ]
            
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
            )

            with open(report_path, "r") as f:
                report = json.load(f)

            summary = report.get("summary", {}) if isinstance(report, dict) else {}
            normalized_summary = {
                "passed": summary.get("passed", 0),
                "failed": summary.get("failed", 0),
                "errors": summary.get("errors", 0),
                "skipped": summary.get("skipped", 0),
                "total": summary.get("total", summary.get("collected", 0)),
            }

            return {
                "stdout": process.stdout,
                "stderr": process.stderr,
                "report": report,
                "summary": normalized_summary,
            }
        finally:
            if os.path.exists(report_path):
                os.remove(report_path)

def get_test_runner_service():
    return TestRunnerService()
