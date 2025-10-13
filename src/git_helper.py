import subprocess
from pathlib import Path
from typing import Optional


# ##################################################################
# git helper
# centralized git operations for workflow version tracking
class GitHelper:
    OUTPUT_DIR = Path("output")
    WORKFLOWS_DIR = OUTPUT_DIR / "workflows"

    # ##################################################################
    # run git command
    # execute git command in output directory with error handling
    @staticmethod
    def run_git_command(args: list[str]) -> str:
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=GitHelper.OUTPUT_DIR,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as err:
            stderr_msg = err.stderr if err.stderr else "no error message"
            stdout_msg = err.stdout if err.stdout else ""
            raise RuntimeError(f"Git command failed: {' '.join(args)} stderr={stderr_msg} stdout={stdout_msg}")

    # ##################################################################
    # commit workflow
    # add and commit workflow file with descriptive message
    @staticmethod
    def commit_workflow(workflow_file: str, message: str) -> None:
        GitHelper.run_git_command(["add", f"workflows/{workflow_file}"])
        GitHelper.run_git_command(["commit", "-m", message])

    # ##################################################################
    # get workflow filename
    # map workflow id to standard filename
    @staticmethod
    def get_workflow_filename(workflow_id: str) -> str:
        mapping = {
            "hlVEk90tMPk0Ydxw": "futuretools_scraping.json",
            "j2cswHsA24ALBGjH": "hacker_news.json",
            "n7pkss4ObgeQhEL5": "my_workflow.json",
            "PSKLQw7n4aXBHLhi": "discord_claude_assistant.json"
        }
        return mapping.get(workflow_id, f"workflow_{workflow_id}.json")

    # ##################################################################
    # commit before change
    # export and commit current state before making changes
    @staticmethod
    def commit_before_change(workflow_id: str, workflow_name: str, change_description: str) -> None:
        from n8n_client import N8nWorkflows
        import json

        filename = GitHelper.get_workflow_filename(workflow_id)
        filepath = GitHelper.WORKFLOWS_DIR / filename

        workflow = N8nWorkflows.get_workflow(workflow_id)

        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(workflow, f, indent=2)

        message = f"Pre-change: {workflow_name} - {change_description}"
        GitHelper.commit_workflow(filename, message)

    # ##################################################################
    # commit after change
    # export and commit new state after making changes
    @staticmethod
    def commit_after_change(workflow_id: str, workflow_name: str, change_description: str) -> None:
        from n8n_client import N8nWorkflows
        import json

        filename = GitHelper.get_workflow_filename(workflow_id)
        filepath = GitHelper.WORKFLOWS_DIR / filename

        workflow = N8nWorkflows.get_workflow(workflow_id)

        with open(filepath, 'w') as f:
            json.dump(workflow, f, indent=2)

        message = f"Changed: {workflow_name} - {change_description}"
        GitHelper.commit_workflow(filename, message)

    # ##################################################################
    # show history
    # display git log for a workflow file
    @staticmethod
    def show_history(workflow_id: str, limit: Optional[int] = 10) -> str:
        filename = GitHelper.get_workflow_filename(workflow_id)
        args = ["log", "--oneline", f"workflows/{filename}"]
        if limit:
            args.insert(1, f"-n{limit}")
        return GitHelper.run_git_command(args)

    # ##################################################################
    # show diff
    # display changes between commits for a workflow
    @staticmethod
    def show_diff(workflow_id: str, from_ref: str = "HEAD~1", to_ref: str = "HEAD") -> str:
        filename = GitHelper.get_workflow_filename(workflow_id)
        return GitHelper.run_git_command(["diff", from_ref, to_ref, f"workflows/{filename}"])
