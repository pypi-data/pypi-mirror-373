# This script defines the `LLMApi` class, which serves as an interface
# for interacting with OpenAI-compatible Large Language Model (LLM) APIs.
# It provides functionalities for listing available models, sending prompts
# for text generation, and managing chat completions, including streaming
# responses and performance metrics.

import logging
import time
from typing import List

from openai import OpenAI
from .constants import Constants

class LLMApi:
    """
    Handles interactions with OpenAI-compatible LLM APIs.
    Provides methods for model listing, text generation, and chat completions.
    """
    def __init__(self, api_endpoint: str, api_key: str, client: OpenAI = None):
        """
        Initializes the LLMApi client.

        Args:
            api_endpoint (str): The URL of the LLM API endpoint.
            api_key (str): The API key for authentication.
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.__validate_configuration()
        self.client = client
        
    def __validate_configuration(self):
        if not self.api_endpoint:
            raise ValueError("api_endpoint is empty!")
        if not self.api_endpoint.startswith('http'):
            raise ValueError("api_endpoint does not start with 'http' !")
        
    def get_openai_client(self) -> OpenAI:
        """
        Creates and returns an OpenAI client instance configured with the
        specified API endpoint and key.

        Returns:
            OpenAI: An initialized OpenAI client object.
        """
        if self.client:
            return self.client
        
        # initialize only if not initialized yet
        self.logger.debug(f"Initializing openai client for endpoint {self.api_endpoint}...")
        self.client = OpenAI(
            base_url=self.api_endpoint,
            api_key=self.api_key
        )
        return self.client

    def list_models(self) -> List[str]:
        """
        Lists available models from the configured OpenAI-compatible endpoint.

        Returns:
            List[str]: A sorted list of model IDs available at the endpoint.

        Raises:
            Exception: If there is an error while listing models.
        """
        try:
            client = self.get_openai_client()
            models = client.models.list()
            ret_array = []
            for model in models.data:
                ret_array.append(model.id)
            ret_array.sort()
            return ret_array
            
        except Exception as e:
            self.logger.error(f"Error listing models: {str(e)}", exc_info=True)
            raise

    def send(self, prompt: str, model: str = Constants.DEFAULT_MODEL, context: List[str] = None, max_tokens: int = 2000, temperature: float = 0.7, system_prompt: str = None) -> str:
        """
        Sends a text prompt to the LLM server for generation and returns the response.
        Context can be provided as a list of strings which will be prepended to the main prompt.

        Args:
            prompt (str): The main text prompt to send to the LLM.
            model (str): The name of the model to use for generation. Defaults to Constants.DEFAULT_MODEL.
            system_prompt (str, optional): A system prompt to use for processing the sent prompt (Default: None)
            context (List[str], optional): List of context strings to prepend to the prompt. Defaults to None.
            max_tokens (int): The maximum number of tokens to generate in the response. Defaults to 2000.
            temperature (float): Controls the randomness of the output. Higher values (e.g., 0.8) make the output more random, while lower values (e.g., 0.2) make it more focused and deterministic. Defaults to 0.7.

        Returns:
            str: The generated content from the LLM.

        Raises:
            Exception: If the API call to the LLM server fails.
        """
        self.logger.info(f"Generating with model {model}")
        
        try:
            client = self.get_openai_client()
            
            # Build messages with context
            messages = self._build_messages(prompt, system_prompt, context)
            
            
            self.logger.debug("-" * 20)
            self.logger.debug("Prompt:")
            self.logger.debug("")
            self.logger.debug(messages[-1]["content"])  # The user message content
            self.logger.debug("")
            self.logger.debug("-" * 20)
            self.logger.debug("")
                
            return self._stream_response(client, messages, model, max_tokens, temperature)
            
        except Exception as e:
            self.logger.error(f"Error calling LLM API at {self.api_endpoint}: {str(e)}", exc_info=True)
            raise

    def chat_completion(self, messages: List[dict], model: str = Constants.DEFAULT_MODEL, max_tokens: int = 2000, temperature: float = 0.7) -> str:
        """
        Sends a list of messages (conversation history) to the LLM server for chat completion.
        The response is streamed back, and performance metrics are calculated.

        Args:
            messages (List[dict]): A list of message dictionaries representing the conversation history.
                                   Each dictionary should have "role" (e.g., "user", "assistant")
                                   and "content" keys.
            model (str): The name of the model to use for chat completion. Defaults to Constants.DEFAULT_MODEL.
            max_tokens (int): The maximum number of tokens to generate in the response. Defaults to 2000.
            temperature (float): Controls the randomness of the output. Defaults to 0.7.

        Returns:
            str: The generated content from the LLM for the chat completion.

        Raises:
            Exception: If the API call to the LLM server fails.
        """
        self.logger.info(f"Generating chat completion with model {model}")

        try:
            client = self.get_openai_client()
            
            self.logger.debug("-" * 20)
            self.logger.debug("Messages:")
            for message in messages:
                self.logger.debug(f"  Role: {message['role']}, Content: {message['content'][:100]}...") # Print first 100 chars
            self.logger.debug("")
            self.logger.debug("-" * 20)
            self.logger.debug("")

            return self._stream_response(client, messages, model, max_tokens, temperature)
            
        except Exception as e:
            self.logger.error(f"Error calling LLM API at {self.api_endpoint}: {str(e)}", exc_info=True)
            raise

    def _build_messages(self, prompt: str, system_prompt: str = None, context: List[str] = None) -> List[dict]:
        """
        Builds the messages list for chat completion with optional context and system prompt.

        Args:
            prompt (str): The main text prompt to send to the LLM.
            system_prompt (str, optional): A system prompt to use for processing the sent prompt. Defaults to None.
            context (List[str], optional): List of context strings to prepend to the prompt. Defaults to None.

        Returns:
            List[dict]: A list of message dictionaries for chat completion.
        """
        # Combine context if provided
        if context:
            self.logger.info("Added provided context to the prompt")
            prompt = f"{self.combine_context(context)}\n{prompt}"
        
        # Build messages
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system", 
                "content": system_prompt
            })
            
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        return messages

    def _stream_response(self, client: OpenAI, messages: List[dict], model: str, max_tokens: int = 2000, temperature: float = 0.7) -> str:
        """
        Streams response from the LLM and calculates performance metrics.
        
        Args:
            client (OpenAI): The OpenAI client instance.
            messages (List[dict]): A list of message dictionaries for chat completion.
            model (str): The name of the model to use for generation.
            max_tokens (int): The maximum number of tokens to generate. Defaults to 2000.
            temperature (float): Controls the randomness of the output. Defaults to 0.7.
            
        Returns:
            str: The generated content from the LLM.
        """
        start_time = time.time()
        first_token_time = None
        self.logger.info("Streaming generation ...")
        
        response_content = ""
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True
        )
        
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                if first_token_time is None:
                    first_token_time = time.time()
                print(content, end="", flush=True)
                response_content += content

        end_time = time.time()
        
        self.logger.info(f"Done generating using model {model}")
        self.logger.info(f"Received response ({len(response_content)} characters)")
            
        if first_token_time is not None:
            duration_to_first = first_token_time - start_time
            duration_last_to_first = end_time - first_token_time
            total_duration = end_time - start_time
            self.logger.info(f"Time to first token: {duration_to_first:.4f}s")
            self.logger.info(f"Time between first and last token: {duration_last_to_first:.4f}s")
            self.logger.info(f"Total duration: {total_duration:.4f}s")
            
            tops = len(response_content) / duration_last_to_first
            self.logger.info(f"Tokens / second: {tops:.4f}")
            
        return response_content

    def combine_context(self, context: List[str]) -> str:
        """
        Combines a list of context strings into a single string,
        separated by a '---' delimiter.

        Args:
            context (List[str]): A list of context strings to combine.

        Returns:
            str: A single string containing the combined context.
        """
        return "\n---\n".join(context)