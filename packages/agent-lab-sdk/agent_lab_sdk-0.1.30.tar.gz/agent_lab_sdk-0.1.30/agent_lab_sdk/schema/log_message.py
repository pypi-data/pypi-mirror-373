from langchain.schema import BaseMessage, AIMessage
import os

IS_LOG_MESSAGE_CUSTOM = os.environ.get("IS_LOG_MESSAGE_CUSTOM", 'False').lower() in ('true', '1', 't')

if IS_LOG_MESSAGE_CUSTOM:
    class LogMessage(BaseMessage):
        def __init__(self, content: str):
            super().__init__(type='log', content=content, additional_kwargs={})
        def dict(self, **kwargs):
            d = super().dict(**kwargs)
            d["type"] = 'log'
            return d
else:
    class LogMessage(AIMessage):
        def __init__(self, content: str):
            super().__init__(content=content, additional_kwargs = {"type": "log"})
