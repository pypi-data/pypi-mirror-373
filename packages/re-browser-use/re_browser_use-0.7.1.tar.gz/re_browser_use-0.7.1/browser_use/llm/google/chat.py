import json
import logging
from dataclasses import dataclass
from typing import Any, Literal, TypeVar, overload

from google import genai
from google.auth.credentials import Credentials
from google.genai import types
from google.genai.types import MediaModality
from pydantic import BaseModel

from browser_use.llm.base import BaseChatModel
from browser_use.llm.exceptions import ModelProviderError
from browser_use.llm.google.serializer import GoogleMessageSerializer
from browser_use.llm.messages import BaseMessage
from browser_use.llm.schema import SchemaOptimizer
from browser_use.llm.views import ChatInvokeCompletion, ChatInvokeUsage

T = TypeVar('T', bound=BaseModel)


VerifiedGeminiModels = Literal[
	'gemini-2.0-flash', 'gemini-2.0-flash-exp', 'gemini-2.0-flash-lite-preview-02-05', 'Gemini-2.0-exp'
]

logger = logging.getLogger(__name__)


def _is_retryable_error(exception):
	"""Check if an error should be retried based on error message patterns."""
	error_msg = str(exception).lower()

	# Rate limit patterns
	rate_limit_patterns = ['rate limit', 'resource exhausted', 'quota exceeded', 'too many requests', '429']

	# Server error patterns
	server_error_patterns = ['service unavailable', 'internal server error', 'bad gateway', '503', '502', '500']

	# Connection error patterns
	connection_patterns = ['connection', 'timeout', 'network', 'unreachable']

	all_patterns = rate_limit_patterns + server_error_patterns + connection_patterns
	return any(pattern in error_msg for pattern in all_patterns)


@dataclass
class ChatGoogle(BaseChatModel):
	"""
	A wrapper around Google's Gemini chat model using the genai client.

	This class accepts all genai.Client parameters while adding model,
	temperature, and config parameters for the LLM interface.

	Args:
		model: The Gemini model to use
		temperature: Temperature for response generation
		config: Additional configuration parameters to pass to generate_content
			(e.g., tools, safety_settings, etc.).
		api_key: Google API key
		vertexai: Whether to use Vertex AI
		credentials: Google credentials object
		project: Google Cloud project ID
		location: Google Cloud location
		http_options: HTTP options for the client

	Example:
		from google.genai import types

		llm = ChatGoogle(
			model='gemini-2.0-flash-exp',
			config={
				'tools': [types.Tool(code_execution=types.ToolCodeExecution())]
			}
		)
	"""

	# Model configuration
	model: VerifiedGeminiModels | str
	temperature: float | None = None
	top_p: float | None = None
	seed: int | None = None
	thinking_budget: int | None = None
	config: types.GenerateContentConfigDict | None = None

	# Client initialization parameters
	api_key: str | None = None
	vertexai: bool | None = None
	credentials: Credentials | None = None
	project: str | None = None
	location: str | None = None
	http_options: types.HttpOptions | types.HttpOptionsDict | None = None
	
	# This was suggested to me by Perplexity and, empirically, it seems to reduce the number of 429 RESOURCE_EXHAUSTED errors.
	client: genai.Client | None = None
	

	# Static
	@property
	def provider(self) -> str:
		return 'google'

	def _get_client_params(self) -> dict[str, Any]:
		"""Prepare client parameters dictionary."""
		# Define base client params
		base_params = {
			'api_key': self.api_key,
			'vertexai': self.vertexai,
			'credentials': self.credentials,
			'project': self.project,
			'location': self.location,
			'http_options': self.http_options,
		}

		# Create client_params dict with non-None values
		client_params = {k: v for k, v in base_params.items() if v is not None}

		return client_params
	
	def get_client(self) -> genai.Client:
		"""
    Returns a genai.Client instance.

    Returns:
        genai.Client: An instance of the Google genai client.
    """
		# This was suggested to me by Perplexity and, empirically, it seems to reduce the number of 429 RESOURCE_EXHAUSTED errors.
		if not self.client:
			client_params = self._get_client_params()
			self.client = genai.Client(**client_params)
			
		return self.client

	@property
	def name(self) -> str:
		return str(self.model)

	def _get_usage(self, response: types.GenerateContentResponse) -> ChatInvokeUsage | None:
		usage: ChatInvokeUsage | None = None

		if response.usage_metadata is not None:
			image_tokens = 0
			if response.usage_metadata.prompt_tokens_details is not None:
				image_tokens = sum(
					detail.token_count or 0
					for detail in response.usage_metadata.prompt_tokens_details
					if detail.modality == MediaModality.IMAGE
				)

			usage = ChatInvokeUsage(
				prompt_tokens=response.usage_metadata.prompt_token_count or 0,
				completion_tokens=(response.usage_metadata.candidates_token_count or 0)
				+ (response.usage_metadata.thoughts_token_count or 0),
				total_tokens=response.usage_metadata.total_token_count or 0,
				prompt_cached_tokens=response.usage_metadata.cached_content_token_count,
				prompt_cache_creation_tokens=None,
				prompt_image_tokens=image_tokens,
			)

		return usage

	@overload
	async def ainvoke(self, messages: list[BaseMessage], output_format: None = None) -> ChatInvokeCompletion[str]: ...

	@overload
	async def ainvoke(self, messages: list[BaseMessage], output_format: type[T]) -> ChatInvokeCompletion[T]: ...

	async def ainvoke(
		self, messages: list[BaseMessage], output_format: type[T] | None = None
	) -> ChatInvokeCompletion[T] | ChatInvokeCompletion[str]:
		"""
		Invoke the model with the given messages.

		Args:
			messages: List of chat messages
			output_format: Optional Pydantic model class for structured output

		Returns:
			Either a string response or an instance of output_format
		"""

		# Serialize messages to Google format
		contents, system_instruction = GoogleMessageSerializer.serialize_messages(messages)

		# Build config dictionary starting with user-provided config
		config: types.GenerateContentConfigDict = {}
		if self.config:
			config = self.config.copy()

		# Apply model-specific configuration (these can override config)
		if self.temperature is not None:
			config['temperature'] = self.temperature

		# Add system instruction if present
		if system_instruction:
			config['system_instruction'] = system_instruction

		if self.top_p is not None:
			config['top_p'] = self.top_p

		if self.seed is not None:
			config['seed'] = self.seed

		if self.thinking_budget is not None:
			thinking_config_dict: types.ThinkingConfigDict = {'thinking_budget': self.thinking_budget}
			config['thinking_config'] = thinking_config_dict
		
		def clean_response_before_parsing(response: str) -> str:
			# Cleans the raw LLM response string before attempting to parse it as JSON.
			# - Removes markdown code block fences (```json ... ```).
			# - Replaces Python-specific string escapes like \\' with a standard single quote.

			json_text = response.strip()
			if json_text.startswith('```json'):
				json_text = json_text[len('```json'): -len('```')].strip()
			elif json_text.startswith('```'):
				json_text = json_text[len('```'): -len('```')].strip()

			# The response might have escaped single quotes from python's repr, which are not valid in JSON
			json_text = json_text.replace("\\'", "'")
			return json_text
		
		# --- Helper Functions for Readability ---
		def is_char_escaped(s: str, index: int) -> bool:
			# Checks if the character at a given index in a string is escaped by a backslash.
			# Handles multiple preceding backslashes (e.g., "abc\\\"def" -> '\"' is escaped).
			if index == 0:
				return False

			num_backslashes = 0
			i = index - 1
			while i >= 0 and s[i] == '\\':
				num_backslashes += 1
				i -= 1

			# If the number of preceding backslashes is odd, the character is escaped.
			return num_backslashes % 2 == 1
		
		def find_next_non_whitespace(text: str, start_index: int) -> int:
			# Finds the index of the next non-whitespace character from a starting position.
			for i in range(start_index, len(text)):
				if not text[i].isspace():
					return i
			return -1
		
		def find_next_unescaped_char(text: str, char_to_find: str, start_index: int) -> int:
			# Finds the next occurrence of a character that is not escaped by a backslash.
			pos = text.find(char_to_find, start_index)
			while pos != -1:
				if not is_char_escaped(text, pos):
					return pos
				# It was escaped, so search again from the next character.
				pos = text.find(char_to_find, pos + 1)
			return -1
		
		def repair_json(text: str) -> str:
			# Repairs a JSON-like string by finding and escaping string values.
			# This version uses a two-pass approach for clarity and correctness:
			# 1. First pass: Identify all string values that need repair.
			# 2. Second pass: Build the new string using the identified segments.

			repairs = []
			cursor = 0

			# Pass 1: Find all segments to repair.
			while cursor < len(text):
				# Find a key-value pair where the value is a string.
				key_start_pos = find_next_unescaped_char(text, '"', cursor)
				if key_start_pos == -1: break

				key_end_pos = find_next_unescaped_char(text, '"', key_start_pos + 1)
				if key_end_pos == -1: break

				colon_pos = find_next_non_whitespace(text, key_end_pos + 1)
				if colon_pos == -1 or text[colon_pos] != ':':
					cursor = key_start_pos + 1
					continue

				value_start_pos = find_next_non_whitespace(text, colon_pos + 1)
				if value_start_pos == -1 or text[value_start_pos] != '"':
					cursor = value_start_pos if value_start_pos != -1 else colon_pos + 1
					continue

				# Find the true end of the string value.
				content_start_pos = value_start_pos + 1
				search_pos = content_start_pos
				value_end_pos = -1

				while search_pos < len(text):
					potential_end_pos = find_next_unescaped_char(text, '"', search_pos)
					if potential_end_pos == -1: break

					char_after_quote_pos = find_next_non_whitespace(text, potential_end_pos + 1)
					if char_after_quote_pos != -1 and text[char_after_quote_pos] in ',}]':
						value_end_pos = potential_end_pos
						break
					else:
						search_pos = potential_end_pos + 1

				if value_end_pos != -1:
					# Found a segment. Store its start, end, and the escaped content.
					content = text[content_start_pos:value_end_pos]
					escaped_content = json.dumps(content)[1:-1]
					repairs.append((content_start_pos, value_end_pos, escaped_content))
					cursor = value_end_pos + 1
				else:
					# Malformed, could not find end. Skip past this key to avoid getting stuck.
					cursor = key_start_pos + 1

			# Pass 2: Build the new string from the original text and the repairs.
			if not repairs:
				return text

			output_parts = []
			last_pos = 0
			for start, end, replacement in repairs:
				output_parts.append(text[last_pos:start])
				output_parts.append(replacement)
				last_pos = end

			output_parts.append(text[last_pos:])

			return "".join(output_parts)

		async def _make_api_call():
			import asyncio
			# Timeout for LLM API calls in seconds: Gemini is killing me and getting stuck forever ...
			LLM_TIMEOUT_SECONDS = 20
			if output_format is None:
				# Return string response
				response = await asyncio.wait_for(self.get_client().aio.models.generate_content(
					model=self.model,
					contents=contents,  # type: ignore
					config=config,
				), timeout=LLM_TIMEOUT_SECONDS)

				# Handle case where response.text might be None
				text = response.text or ''

				usage = self._get_usage(response)

				return ChatInvokeCompletion(
					completion=text,
					usage=usage,
				)

			else:
				# Return structured response
				config['response_mime_type'] = 'application/json'
				# Convert Pydantic model to Gemini-compatible schema
				optimized_schema = SchemaOptimizer.create_optimized_json_schema(output_format)

				gemini_schema = self._fix_gemini_schema(optimized_schema)
				config['response_schema'] = gemini_schema

				response = await asyncio.wait_for(self.get_client().aio.models.generate_content(
					model=self.model,
					contents=contents,
					config=config,
				), timeout=LLM_TIMEOUT_SECONDS)

				usage = self._get_usage(response)

				# Handle case where response.parsed might be None
				if response.parsed is None:
					# When using response_schema, Gemini returns JSON as text
					if response.text:
						try:
							# Parse the JSON text and validate with the Pydantic model
							parsed_data = json.loads(repair_json(clean_response_before_parsing(response.text)))
							return ChatInvokeCompletion(
								completion=output_format.model_validate(parsed_data),
								usage=usage,
							)
						except (json.JSONDecodeError, ValueError) as e:
							raise ModelProviderError(
								message=f'Failed to parse or validate response: {str(e)}',
								status_code=500,
								model=self.model,
							) from e
					else:
						raise ModelProviderError(
							message='No response from model',
							status_code=500,
							model=self.model,
						)

				# Ensure we return the correct type
				if isinstance(response.parsed, output_format):
					return ChatInvokeCompletion(
						completion=response.parsed,
						usage=usage,
					)
				else:
					# If it's not the expected type, try to validate it
					return ChatInvokeCompletion(
						completion=output_format.model_validate(response.parsed),
						usage=usage,
					)

		try:
			# Use manual retry loop for Google API calls
			last_exception = None
			for attempt in range(10):  # Match our 10 retry attempts from other providers
				try:
					return await _make_api_call()
				except Exception as e:
					last_exception = e
					if not _is_retryable_error(e) or attempt == 9:  # Last attempt
						break

					# Simple exponential backoff
					import asyncio

					delay = min(60.0, 1.0 * (2.0**attempt))  # Cap at 60s
					error_msg = str(e)
					prefix = f'❌ Invocation to LLM number {attempt} failed. Waiting for {delay} seconds before retrying:\n '
					logger.error(f'{prefix}{error_msg}')
					await asyncio.sleep(delay)

			# Re-raise the last exception if all retries failed
			if last_exception:
				raise last_exception
			else:
				# This should never happen, but ensure we don't return None
				raise ModelProviderError(
					message='All retry attempts failed without exception',
					status_code=500,
					model=self.name,
				)

		except Exception as e:
			# Handle specific Google API errors
			error_message = str(e)
			status_code: int | None = None

			# Check if this is a rate limit error
			if any(
				indicator in error_message.lower()
				for indicator in ['rate limit', 'resource exhausted', 'quota exceeded', 'too many requests', '429']
			):
				status_code = 429
			elif any(
				indicator in error_message.lower()
				for indicator in ['service unavailable', 'internal server error', 'bad gateway', '503', '502', '500']
			):
				status_code = 503

			# Try to extract status code if available
			if hasattr(e, 'response'):
				response_obj = getattr(e, 'response', None)
				if response_obj and hasattr(response_obj, 'status_code'):
					status_code = getattr(response_obj, 'status_code', None)

			raise ModelProviderError(
				message=error_message,
				status_code=status_code or 502,  # Use default if None
				model=self.name,
			) from e

	def _fix_gemini_schema(self, schema: dict[str, Any]) -> dict[str, Any]:
		"""
		Convert a Pydantic model to a Gemini-compatible schema.

		This function removes unsupported properties like 'additionalProperties' and resolves
		$ref references that Gemini doesn't support.
		"""

		# Handle $defs and $ref resolution
		if '$defs' in schema:
			defs = schema.pop('$defs')

			def resolve_refs(obj: Any) -> Any:
				if isinstance(obj, dict):
					if '$ref' in obj:
						ref = obj.pop('$ref')
						ref_name = ref.split('/')[-1]
						if ref_name in defs:
							# Replace the reference with the actual definition
							resolved = defs[ref_name].copy()
							# Merge any additional properties from the reference
							for key, value in obj.items():
								if key != '$ref':
									resolved[key] = value
							return resolve_refs(resolved)
						return obj
					else:
						# Recursively process all dictionary values
						return {k: resolve_refs(v) for k, v in obj.items()}
				elif isinstance(obj, list):
					return [resolve_refs(item) for item in obj]
				return obj

			schema = resolve_refs(schema)

		# Remove unsupported properties
		def clean_schema(obj: Any) -> Any:
			if isinstance(obj, dict):
				# Remove unsupported properties
				cleaned = {}
				for key, value in obj.items():
					if key not in ['additionalProperties', 'title', 'default']:
						cleaned_value = clean_schema(value)
						# Handle empty object properties - Gemini doesn't allow empty OBJECT types
						if (
							key == 'properties'
							and isinstance(cleaned_value, dict)
							and len(cleaned_value) == 0
							and isinstance(obj.get('type', ''), str)
							and obj.get('type', '').upper() == 'OBJECT'
						):
							# Convert empty object to have at least one property
							cleaned['properties'] = {'_placeholder': {'type': 'string'}}
						else:
							cleaned[key] = cleaned_value

				# If this is an object type with empty properties, add a placeholder
				if (
					isinstance(cleaned.get('type', ''), str)
					and cleaned.get('type', '').upper() == 'OBJECT'
					and 'properties' in cleaned
					and isinstance(cleaned['properties'], dict)
					and len(cleaned['properties']) == 0
				):
					cleaned['properties'] = {'_placeholder': {'type': 'string'}}

				return cleaned
			elif isinstance(obj, list):
				return [clean_schema(item) for item in obj]
			return obj

		return clean_schema(schema)
