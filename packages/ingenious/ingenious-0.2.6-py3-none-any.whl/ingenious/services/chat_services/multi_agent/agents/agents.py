import os
import re
from typing import Any, Dict, List


def decrement_heading_levels(content: str) -> str:
    # Decrement the level of any headings within the content
    return re.sub(
        r"^(#{3,})", lambda m: "#" * (len(m.group(1)) - 1), content, flags=re.MULTILINE
    )


def parse_markdown_to_object(markdown_content: str) -> Dict[str, Any]:
    lines = markdown_content.split("\n")
    obj: Dict[str, Any] = {}
    current_section: str | None = None
    current_content: List[str] = []

    for line in lines:
        if line.startswith("# "):
            obj_name = line[2:].strip()
            obj["Title"] = obj_name
        elif line.startswith("## "):
            if current_section:
                content = "\n".join(current_content).strip()
                obj[current_section] = decrement_heading_levels(content)
            current_section = line[3:].strip()
            current_content = []
        else:
            current_content.append(line)

    if current_section:
        content = "\n".join(current_content).strip()
        obj[current_section] = decrement_heading_levels(content)

    return obj


def GetAgent(agent_name: str) -> Dict[str, Any]:
    markdown_content = ""
    # Get the content from the markdown file
    with open(
        f"./ingenious/services/chat_services/multi_agent/agents/{agent_name}/agent.md",
        "r",
        encoding="utf-8",
    ) as file:
        markdown_content = file.read()

    agent_settings = parse_markdown_to_object(markdown_content)

    # Pretty print the agent settings
    # print(json.dumps(agent_settings, indent=4))

    agent_tasks = []

    tasks = os.listdir(
        f"./ingenious/services/chat_services/multi_agent/agents/{agent_name}/tasks"
    )
    for task in tasks:
        with open(
            f"./ingenious/services/chat_services/multi_agent/agents/{agent_name}/tasks/{task}",
            "r",
            encoding="utf-8",
        ) as file:
            markdown_content = file.read()
            agent_tasks.append(parse_markdown_to_object(markdown_content))

    agent_settings["Tasks"] = agent_tasks
    return agent_settings
