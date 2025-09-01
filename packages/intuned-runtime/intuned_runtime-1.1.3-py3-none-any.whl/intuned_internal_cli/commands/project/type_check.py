import json
import os
import subprocess
import sys

import arguably

current_dir = os.path.dirname(os.path.abspath(__file__))
PYRIGHT_CONFIG_PATH = os.path.join(current_dir, "..", "..", "pyright_type_check.json")
PYRIGHT_CONFIG_PATH = os.path.abspath(PYRIGHT_CONFIG_PATH)


@arguably.command  # type: ignore
async def project__type_check():
    """
    Run type checking on the API directory using pyright.

    This function executes pyright type checker on the API directory and processes its output.
    It parses the JSON output from pyright and formats any type checking issues found.

    Returns:
        None

    Raises:
        Exception: In the following cases:
            - If pyright finds any type checking issues (with detailed error messages)
            - If pyright output cannot be parsed as JSON
            - If pyright subprocess fails to run
            - For any other unexpected errors during type checking

    The function collects type checking issues including:
        - File path where issue was found
        - Line number of the issue
        - Severity level of the issue
        - Error message
        - Rule type (always "type-check")
    """
    project_dir = os.getcwd()
    print("📦 Checking Types...")

    try:
        pyright_issues = []
        pyright_result = subprocess.run(
            ["pyright", "--outputjson", project_dir, "--project", PYRIGHT_CONFIG_PATH],
            capture_output=True,
            text=True,
            check=False,
        )

        if pyright_result.stdout:
            pyright_data = json.loads(pyright_result.stdout)
            for diagnostic in pyright_data.get("generalDiagnostics", []):
                severity = diagnostic.get("severity", "").lower()
                severity_emoji = "ℹ️" if severity == "information" else "⚠️" if severity == "warning" else "🔴"

                pyright_issues.append(
                    {
                        "path": diagnostic.get("file", ""),
                        "line": diagnostic.get("range", {}).get("start", {}).get("line", 0) + 1,
                        "severity": diagnostic.get("severity", ""),
                        "message": diagnostic.get("message", ""),
                        "rule": "type-check",
                    }
                )

                file_path = diagnostic.get("file", "")
                if "api/" in file_path:
                    file_path = file_path[file_path.index("api/") :]
                line_num = diagnostic.get("range", {}).get("start", {}).get("line", 0) + 1
                message = diagnostic.get("message", "")
                print(f"{severity_emoji} {file_path}:{line_num} - {message}")

                if severity.lower() == "error":
                    print("\n🔴 Type check failed")
                    sys.exit(1)

            if pyright_issues:
                has_warnings = any(issue["severity"].lower() == "warning" for issue in pyright_issues)
                if has_warnings:
                    print("\n⚠️ Type check passed with warnings")
                    sys.exit(0)

            print("✨ Python type checking passed without errors.")
            sys.exit(0)
    except json.JSONDecodeError:
        print("🔴 Failed to parse pyright output as JSON")
        sys.exit(1)
    except subprocess.SubprocessError:
        print("🔴 Failed to run pyright type checker")
        sys.exit(1)
    except Exception as e:
        print(f"🔴 Type checking failed: {str(e)}")
        sys.exit(1)
