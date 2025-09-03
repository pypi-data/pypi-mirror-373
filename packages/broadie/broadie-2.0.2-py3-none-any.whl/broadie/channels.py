from langgraph.prebuilt import create_react_agent
from langgraph.types import Command

from broadie.prompts import BASE_CHANNELS_INSTRUCTIONS
from broadie.schemas import ChannelSchema, ModelSchema
from broadie.tools.channels import send_api_tool, send_email_tool, send_slack_tool


class ChannelsAgent:
    def __init__(self, model: ModelSchema):
        self.model = model
        self.runtime = self._init_runtime()

    def _init_runtime(self):
        model_id = f"{self.model.provider.value}:{self.model.name}"
        return create_react_agent(
            model=model_id,
            tools=[send_slack_tool, send_email_tool, send_api_tool],
            prompt=BASE_CHANNELS_INSTRUCTIONS,
        )

    async def run(
        self,
        channel: ChannelSchema,
        output: dict,
        thread_id: str,
        message_id: str,
        run_id: str,
    ):
        content = f"""
Channel type: {channel.type}
Channel target: {channel.target}
Channel instructions: {channel.instructions or "None"}
Raw agent output: {output}
"""
        return await self.runtime.ainvoke(
            Command(
                update={
                    "messages": [{"role": "user", "content": content, "id": message_id}],
                },
            ),
            config={
                "configurable": {"thread_id": thread_id},
                "run_id": run_id,
                "metadata": {"channel": channel.type, "target": channel.target},
            },
        )
