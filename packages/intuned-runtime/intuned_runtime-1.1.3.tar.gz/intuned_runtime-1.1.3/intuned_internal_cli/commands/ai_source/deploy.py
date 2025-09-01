import json

import arguably
from more_termcolor import bold  # type: ignore
from more_termcolor import cyan  # type: ignore
from more_termcolor import green  # type: ignore
from more_termcolor import red  # type: ignore

from intuned_internal_cli.utils.code_tree import convert_project_to_code_tree

from ...utils.ai_source_project import AiSourceInfo
from ...utils.ai_source_project import deploy_ai_source


@arguably.command  # type: ignore
def ai_source__deploy(
    *,
    ai_source_info_str: str,
    ai_source_info_path: str,
    yes_to_all: bool = False,
):
    """
    Commands to run on AI source projects.

    Args:
        ai_source_info_str (str): [--ai-source-info] JSON string containing the AI source project information.
        ai_source_info_path (str): Path to the JSON file containing the AI source project information. Defaults to <current directory>/ai_source.json.
        yes_to_all (bool): [-y/--yes] Skip confirmation prompts.
    """

    if ai_source_info_str and ai_source_info_path:
        raise ValueError("Only one of ai_source_info or ai_source_info_path should be provided.")

    if not (ai_source_info_str or ai_source_info_path):
        ai_source_info_path = "ai_source.json"

    try:
        if ai_source_info_str:
            ai_source_info_json = json.loads(ai_source_info_str)
        else:
            with open(ai_source_info_path) as f:
                ai_source_info_json = json.load(f)
        ai_source_info = AiSourceInfo(**ai_source_info_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in ai_source_info: {e}") from e
    except FileNotFoundError as e:
        raise ValueError("AI source info file not found") from e
    except OSError as e:
        raise ValueError("Error reading AI source info file") from e
    except TypeError as e:
        raise ValueError("AI source info is invalid:", str(e)) from e

    wait_for_confirm = not yes_to_all

    code_tree = convert_project_to_code_tree(".", wait_for_confirm=wait_for_confirm)

    success = deploy_ai_source(code_tree, ai_source_info)

    if success:
        print(
            f"🚀 AI source deployment triggered for {bold(green(ai_source_info.id))} ({bold(green(ai_source_info.version_id))}). Check progress at {cyan(f"{ai_source_info.environment_url}/__internal-ai-sources/{ai_source_info.id}?version_id={ai_source_info.version_id}")}"
        )
    else:
        print(red(bold("Deployment failed")))
