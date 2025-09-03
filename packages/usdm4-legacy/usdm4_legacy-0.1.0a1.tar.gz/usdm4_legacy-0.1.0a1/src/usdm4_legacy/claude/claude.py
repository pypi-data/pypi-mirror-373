import json
from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation
from anthropic import Anthropic
from d4k_ms_base.service_environment import ServiceEnvironment


class Claude:
    MODULE = "usdm4_legacy.claude.claude.Claude"
    CLAUDE_MODEL = "claude-sonnet-4-20250514"
    MODEL_PRICING = {CLAUDE_MODEL: {"input": 15.0, "output": 75.0}}

    def __init__(self, errors: Errors):
        api_key = ServiceEnvironment().get("ANTHROPIC_API_KEY")
        self._errors = errors
        self._client = None
        if not api_key:
            location = KlassMethodLocation(self.MODULE, "__init__")
            errors.error("Anthropic API key environment variable is not set", location)
        else:
            self._client = Anthropic(api_key=api_key)

    def prompt(self, text: str) -> str:
        message = self._client.messages.create(
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": text,
                }
            ],
            model=self.CLAUDE_MODEL,
        )
        return message.content[0].text

    def extract_json(self, text: str) -> dict:
        result = text.replace("\n", "")
        s_index = result.find("{")
        e_index = result.rfind("}")
        if s_index >= 0 and e_index >= 0 and e_index > s_index:
            result = result[s_index : e_index + 1]
            try:
                return json.loads(result)
            except Exception as e:
                location = KlassMethodLocation(self.MODULE, "extract_json")
                self._errors.exception("Error decoding Claude JSON", e, location)
                return None
        else:
            location = KlassMethodLocation(self.MODULE, "extract_json")
            self._errors.error("Error decoding Claude response", location)
            return None

    # def system_prompt(self, content: str, system: str) -> str:
    #     message = self._client.messages.create(
    #         model=self.CLAUDE_MODEL,
    #         max_tokens=1024,
    #         temperature=0,
    #         system=system,
    #         messages=[
    #             {"role": "user",
    #             "content": content}
    #         ]
    #     )
    #     return message

    # def process_streamed_response(self, stream, protocol_id, table_id="table-001"):
    #     full_response = ""
    #     progress_marker = 0
    #     token_stats = {
    #         "input_tokens": 0,
    #         "output_tokens": 0,
    #         "completion_tokens": 0  # Will be set from response metadata
    #     }

    #     try:
    #         application_logger.info(f"🔄 Receiving streamed response...")
    #         for chunk in stream:
    #             if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'text'):
    #                 content = chunk.delta.text
    #                 full_response += content

    #                 # Show progress periodically
    #                 if len(full_response) - progress_marker > 1000:
    #                     application_logger.info(f"🔄 Received {len(full_response)} characters so far...")
    #                     progress_marker = len(full_response)

    #             # Capture token usage when available
    #             if hasattr(chunk, 'usage'):
    #                 if hasattr(chunk.usage, 'input_tokens'):
    #                     token_stats['input_tokens'] = chunk.usage.input_tokens
    #                 if hasattr(chunk.usage, 'output_tokens'):
    #                     token_stats['output_tokens'] = chunk.usage.output_tokens

    #     except Exception as e:
    #         application_logger.error(f"❌ Error processing stream: {str(e)}")

    #     application_logger.info(f"✅ Stream complete, received {len(full_response)} characters total")

    #     # Get final usage from the last message
    #     if hasattr(stream, 'usage'):
    #         if hasattr(stream.usage, 'input_tokens'):
    #             token_stats['input_tokens'] = stream.usage.input_tokens
    #         if hasattr(stream.usage, 'output_tokens'):
    #             token_stats['output_tokens'] = stream.usage.output_tokens
    #         if hasattr(stream.usage, 'completion_tokens'):
    #             token_stats['completion_tokens'] = stream.usage.completion_tokens

    #     return {
    #         "text": full_response,
    #         "token_stats": token_stats
    #     }

    # def streaming_response(self, messages: List, system_message: str, protocol_id: str, table_id: str) -> str:
    #     """
    #     Send a prompt with system context to Claude and get the response.

    #     Args:
    #         text: The prompt text
    #         system: The system context prompt

    #     Returns:
    #         The response text from Claude
    #     """

    #     # max_tokens=4000,
    #     # Create a streaming API call
    #     with self._client.messages.stream(
    #         model=self.CLAUDE_MODEL,
    #         # max_tokens=1024,  # Default for smaller extractions
    #         max_tokens=24000,  # Increased for larger extractions
    #         temperature=0,     # Zero temperature for deterministic output
    #         system=system_message,
    #         messages=messages
    #     ) as stream:
    #         # Process the streamed response
    #         response_data = self.process_streamed_response(stream, protocol_id, table_id)
    #         result_text = response_data["text"]
    #         token_stats = response_data["token_stats"]
    #         cost_info = self.calculate_token_cost(token_stats)

    #     return result_text, cost_info,token_stats
