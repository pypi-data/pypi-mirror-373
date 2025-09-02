import json
from collections import defaultdict
from typing import List
import litellm
from typing import get_type_hints
from pydantic import BaseModel
from openai.types.chat import ChatCompletionMessage, ChatCompletionMessageToolCall

# this is for anthropic to handle user-user or assistant-assistant messages
litellm.modify_params = True

# this is to drop any input parameters not supported by the openai spec
# https://docs.litellm.ai/docs/completion/input
litellm.drop_params = True

# this is to enable otel logging
# litellm.callbacks = ["otel"]


from gepeto.team.utils import debug_print, func_to_json
from gepeto.prompts import Prompt
from gepeto.team.schema import Response, Result
from gepeto.team.schemas.agent_schema import Agent, AgentFunction


__VARS_NAME__ = "context"


class Team:
    def __init__(self):
        pass

    def run_agent(
        self,
        agent: Agent,
        message_history: List,
        context: dict,
        debug: bool = False,
    ) -> ChatCompletionMessage:

        context = defaultdict(str, context)
        instructions = (
            agent.instructions(context)
            if callable(agent.instructions)
            else (
                agent.instructions.content.format(context)
                if isinstance(agent.instructions, Prompt)
                else agent.instructions.format(context)
            )
        )

        messages = [{"role": "system", "content": instructions}] + message_history
        debug_print(debug, "messages", messages)

        # TODO: flag here for saad
        tools = [func_to_json(f) for f in agent.functions]

        for tool in tools:
            params = tool["function"]["parameters"]
            params["properties"].pop(__VARS_NAME__, None)
            if __VARS_NAME__ in params["required"]:
                params["required"].remove(__VARS_NAME__)

        create_params = {
            "model": agent.model,
            "max_tokens": agent.max_tokens,
            "temperature": agent.temperature,
            "messages": messages,
        }

        if tools:
            create_params["parallel_tool_calls"] = agent.parallel_tool_calls
            create_params["tools"] = tools
            create_params["tool_choice"] = agent.tool_choice

        # this is for structured output of an agent
        response_format = agent.response_format
        if response_format:
            create_params["response_format"] = response_format

        return litellm.completion(**create_params)

    def handle_function_result(self, result, debug) -> Result:
        match result:
            case Result() as result:
                return result

            case Agent() as agent:
                return Result(value=json.dumps({"assistant": agent.name}), agent=agent)

            case _:
                try:
                    return Result(value=str(result))
                except Exception as e:
                    error_message = f"Failed to cast response to string: {result}. Make sure agent functions return a string or Result object. Error: {str(e)}"
                    debug_print(debug, error_message)
                    raise TypeError(error_message)

    def handle_tool_calls(
        self,
        tool_calls: List[ChatCompletionMessageToolCall],
        functions: List[AgentFunction],
        context: dict,
        debug: bool,
    ) -> Response:

        function_map = {f.__name__: f for f in functions}
        constructed_response = Response(messages=[], agent=None, context={})

        for tool_call in tool_calls:
            name = tool_call.function.name

            if name not in function_map:
                debug_print(debug, f"Tool {name} not found in function map")
                constructed_response.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "tool_name": name,
                        "content": f"Error: tool {name} not found in function map",
                    }
                )
                continue

            args = json.loads(tool_call.function.arguments)
            debug_print(
                debug,
                f"Processing tool call: {name} with args: {args} of type {type(args)}",
            )

            func = function_map[name]
            # Get type hints for the function
            type_hints = get_type_hints(func)

            # Convert args to appropriate Pydantic models based on type hints
            converted_args = {}
            for param_name, param_value in args.items():
                if param_name in type_hints:
                    expected_type = type_hints[param_name]
                    # Check if the expected type is a Pydantic model
                    if isinstance(expected_type, type) and issubclass(
                        expected_type, BaseModel
                    ):
                        # If the value is a string, wrap it in a dict with 'type' key
                        if isinstance(param_value, str):
                            param_value = {"type": param_value}
                        # Convert dict to Pydantic model
                        converted_args[param_name] = expected_type(**param_value)
                    else:
                        # Keep original value for non-Pydantic parameters
                        converted_args[param_name] = param_value
                else:
                    converted_args[param_name] = param_value

            if __VARS_NAME__ in func.__code__.co_varnames:
                converted_args[__VARS_NAME__] = context
            raw_result = function_map[name](**converted_args)

            result: Result = self.handle_function_result(raw_result, debug)

            constructed_response.messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "tool_name": name,
                    "content": result.value,
                }
            )

            constructed_response.context.update(result.context)
            if result.agent:
                constructed_response.agent = result.agent

        return constructed_response

    def run(
        self,
        agent: Agent,
        message_history: List,
        context: dict = {},
        debug: bool = False,
        max_turns: int = 1,
        execute_tools: bool = True,
    ) -> Response:
        res = None
        # Send function inputs
        try:
            import requests
            import json
            import os

            url = (
                f"https://gateway.try248.com/server/api/v1/shared/agents/run/{agent.id}"
            )
            if url:
                payload = {
                    "message_history": message_history,
                    "variable_inputs": context,
                    "debug": debug,
                    "prompt_version_id": agent.instructions.id,
                    "max_turns": max_turns,
                }

                res = requests.post(
                    url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "x-api-key": "gpto-b18f-a623-78cf",
                    },
                    # timeout=1  # Short timeout to not block execution
                )
                # return res.json()

        except Exception as e:
            raise e

        try:
            response_data = res.json()
            return Response(
                messages=response_data.get("messages", []),
                agent=response_data.get("agent"),
                context=response_data.get("context", {}),
                response_object=response_data.get("response_object"),
                completion=response_data.get("completion"),
            )
        except Exception as e:
            raise e
