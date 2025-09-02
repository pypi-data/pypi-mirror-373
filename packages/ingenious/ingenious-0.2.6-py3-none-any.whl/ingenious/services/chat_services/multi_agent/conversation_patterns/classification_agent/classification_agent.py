from typing import Any, Callable, Dict, List, Tuple

import autogen
import autogen.retrieve_utils
import autogen.runtime_logging

from ingenious.core.structured_logging import get_logger

logger = get_logger(__name__)


class ConversationPattern:
    def __init__(
        self,
        default_llm_config: Dict[str, Any],
        topics: List[str],
        memory_record_switch: bool,
        memory_path: str,
        thread_memory: str,
    ) -> None:
        self.default_llm_config = default_llm_config
        self.topics = topics
        self.memory_record_switch = memory_record_switch
        self.memory_path = memory_path
        self.thread_memory = thread_memory
        self.topic_agents: List[autogen.AssistantAgent] = []
        self.termination_msg: Callable[[Dict[str, Any]], bool] = (
            lambda x: "TERMINATE" in x.get("content", "").upper()
        )
        self.context = ""

        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            is_termination_msg=self.termination_msg,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=2,
            system_message="I enhance the user question with context",
            code_execution_config=False,
        )

        # self.researcher = autogen.ConversableAgent(
        #     name="researcher",
        #     system_message=(
        #         "Tasks:\n"
        #         f"-Identify payload type and send to predefined topic agent: {', '.join(self.topics)}.\n"
        #         "Rules:\n"
        #         f"The payload can only be one of the following type: {', '.join(self.topics)}"
        #         "if undefined:"
        #         ""
        #
        #     ),
        #     description="Responds after `planner`.",
        #     llm_config=self.default_llm_config,
        #     human_input_mode="NEVER",
        #     code_execution_config=False,
        #     is_termination_msg=self.termination_msg,
        # )

        self.planner = autogen.ConversableAgent(
            name="planner",
            system_message=(
                "Tasks:\n"
                f"-Pass the payload as plain text to predefined topic agent: {', '.join(self.topics)}.\n"
                "- Wait topic agent compose the final response and say TERMINATE ."
                "- I do not provide answer to user question.\n"
            ),
            description="Responds after `user_proxy` or topic agents",
            llm_config=self.default_llm_config,
            human_input_mode="NEVER",
            code_execution_config=False,
            is_termination_msg=self.termination_msg,
        )

    def add_topic_agent(self, agent: autogen.AssistantAgent) -> None:
        self.topic_agents.append(agent)

    async def get_conversation_response(self, input_message: str) -> Tuple[str, str]:
        """
        This function is the main entry point for the conversation pattern. It takes a message as input and returns a
        response. Make sure that you have added the necessary topic agents and agent topic chats before
        calling this function.
        """

        graph_dict = {}
        graph_dict[self.user_proxy] = [self.planner]
        # graph_dict[self.planner] = [self.researcher]
        graph_dict[self.planner] = self.topic_agents
        for topic_agent in self.topic_agents:
            graph_dict[topic_agent] = [self.planner]

        groupchat = autogen.GroupChat(
            agents=[self.user_proxy, self.planner] + self.topic_agents,
            messages=[],
            max_round=5,
            speaker_selection_method="auto",
            send_introductions=True,
            # select_speaker_auto_verbose=False,  # Removed: unsupported in current autogen version
            allowed_or_disallowed_speaker_transitions=graph_dict,
            # max_retries_for_selecting_speaker=1,  # Removed: unsupported in current autogen version
            speaker_transitions_type="allowed",
        )

        # Clean llm_config for GroupChatManager (remove functions/tools)
        clean_llm_config = {
            k: v
            for k, v in self.default_llm_config.items()
            if k not in ["functions", "tools", "function_call", "tool_choice"]
        }

        manager = autogen.GroupChatManager(
            groupchat=groupchat,
            llm_config=clean_llm_config,
            is_termination_msg=self.termination_msg,
            code_execution_config=False,
        )

        res = await self.user_proxy.a_initiate_chat(
            manager,
            message=(
                "Extract insights from the payload, ensuring that only one type of topic agent is selected. \n"
                "The output must be in JSON format, containing only the JSON string within {} and no additional text outside."
                "Payload: " + input_message
            ),
            summary_method="last_msg",
        )

        return res.summary, self.context
