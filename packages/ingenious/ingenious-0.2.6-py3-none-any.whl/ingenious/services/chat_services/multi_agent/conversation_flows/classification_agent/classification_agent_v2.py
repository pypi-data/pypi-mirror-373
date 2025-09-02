import os
import uuid
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

import ingenious.config.config as config
import ingenious.utils.match_parser as mp
from ingenious.models.chat import ChatRequest
from ingenious.services.chat_services.multi_agent.conversation_patterns.classification_agent.classification_agent_v2 import (
    ConversationPattern,
)


class ConversationFlow:
    @staticmethod
    async def get_conversation_response(chatrequest: ChatRequest) -> tuple[str, str]:
        message = chatrequest.user_prompt
        topics = chatrequest.topic
        thread_memory = chatrequest.thread_memory
        memory_record_switch = chatrequest.memory_record
        event_type = chatrequest.event_type
        # thread_chat_history = chatrequest.thread_chat_history

        _config = config.get_config()
        llm_config: dict[str, object] = {
            "model": _config.models[0].model,
            "api_key": _config.models[0].api_key,
            "azure_endpoint": _config.models[0].base_url,
            "azure_deployment": _config.models[0].deployment,
            "api_version": _config.models[0].api_version,
            "api_type": "azure",
            "authentication_method": _config.models[0].authentication_method,
        }
        memory_path = _config.chat_history.memory_path

        # Load Jinja environment for prompts
        working_dir = Path(os.getcwd())
        template_path = working_dir / "ingenious" / "templates" / "prompts"
        print(template_path)
        env = Environment(loader=FileSystemLoader(template_path), autoescape=True)

        try:
            match = mp.MatchDataParser(payload=message, event_type=event_type)
            message, overBall, timestamp, match_id, feed_id = (
                match.create_detailed_summary()
            )
        except Exception:
            message = "payload undefined"
            timestamp = str(datetime.now())
            match_id = "-"
            feed_id = "-"
            overBall = "-"

        # Convert topic string to list for ConversationPattern
        topics_list: list[str] = [topics] if topics else []

        # Initialize the new conversation pattern
        _classification_agent_pattern = ConversationPattern(
            default_llm_config=llm_config,
            topics=topics_list,
            memory_record_switch=memory_record_switch or False,
            memory_path=memory_path,
            thread_memory=thread_memory or "",
        )

        response_id = str(uuid.uuid4())

        # Add topic agents using the new API
        for topic in [
            "payload_type_1",
            "payload_type_2",
            "payload_type_3",
            "undefined",
        ]:
            try:
                template = env.get_template(f"{topic}_prompt.jinja")
                system_message = template.render(
                    topic=topic,
                    response_id=response_id,
                    feedTimestamp=timestamp,
                    match_id=match_id,
                    feedId=feed_id,
                    overBall=overBall,
                )
            except Exception:
                # Fallback system message if template not found
                system_message = f"I **ONLY** respond when addressed by `planner`, focusing solely on insights about {topic}."
                if topic == "undefined":
                    system_message = "I **ONLY** respond when addressed by `planner` when the payload is undefined."

            _classification_agent_pattern.add_topic_agent(topic, system_message)

        # Get the conversation response
        (
            res,
            memory_summary,
        ) = await _classification_agent_pattern.get_conversation_response(message)

        # Clean up
        await _classification_agent_pattern.close()

        return res, memory_summary
