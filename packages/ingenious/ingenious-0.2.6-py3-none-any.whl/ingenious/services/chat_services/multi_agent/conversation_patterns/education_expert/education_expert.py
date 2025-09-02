import autogen
import autogen.retrieve_utils
import autogen.runtime_logging

import ingenious.services.chat_services.multi_agent.agents.agents as agents


class ConversationPattern:
    class Request:
        def __init__(self):
            pass

    def __init__(self, default_llm_config: dict[str, object]):
        self.default_llm_config = default_llm_config

    async def get_conversation_response(
        self, input_message: str, thread_chat_history: list[object] = []
    ) -> str:
        """
        This function is the main entry point for the conversation pattern. It takes a message as input and returns a
        response. Make sure that you have added the necessary topic agents and agent topic chats before
        calling this function.
        """
        # chat_history_json = json.dumps(thread_chat_history)
        _educator = agents.GetAgent("education_expert")
        # _educator= agents.GetAgent("education_expert")
        educator_tasks = [_educator["Tasks"][0]["Tasks"]]

        # curriculum_expert = autogen.AssistantAgent(
        #     name="curriculum_expert",
        #     description="You are an curriculum expert assistant. Your role is to provide detailed lesson plans based on the Lesson Plans Summary.",
        #     llm_config=self.default_llm_config,
        # )

        educator = autogen.AssistantAgent(
            name="educator",
            description="You are an English subject school teacher.",
            llm_config=self.default_llm_config,
            system_message=_educator["System Message"],
        )

        user = autogen.UserProxyAgent(
            name="User",
            human_input_mode="NEVER",
            is_termination_msg=lambda x: x.get("content", "")
            and x.get("content", "").rstrip().endswith("TERMINATE"),
            # max_consecutive_auto_reply=1,
            code_execution_config=False,
        )

        # groupchat = autogen.GroupChat(agents=[user, educator, curriculum_expert], messages=[], max_round=12)
        # manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=self.default_llm_config)
        # chat_results = user.initiate_chat(manager, message=educator_tasks[0])

        user.initiate_chats(
            [
                {
                    "recipient": educator,
                    "message": educator_tasks[0],
                    "clear_history": True,
                    "silent": False,
                    "cache": None,
                    "max_turns": 1,
                    "summary_method": "last_msg",
                }
            ]
        )

        # Send a response back to the user
        return "chat_results.summary()"
