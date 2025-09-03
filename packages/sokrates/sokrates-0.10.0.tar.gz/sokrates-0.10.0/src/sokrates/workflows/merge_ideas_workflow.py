from typing import List
from pathlib import Path
from sokrates.llm_api import LLMApi
from sokrates.prompt_refiner import PromptRefiner
from sokrates.colors import Colors
from sokrates.constants import Constants
from sokrates.file_helper import FileHelper

class MergeIdeasWorkflow:
    """
    A workflow class for merging multiple ideas or documents using LLM capabilities.
    
    This class provides functionality to combine multiple source documents into a
    coherent merged output using an LLM with a specialized prompt template.
    """
    
    DEFAULT_MAX_TOKENS = 50000
    DEFAULT_TEMPERATURE = 0.5

    def __init__(self, api_endpoint: str = Constants.DEFAULT_API_ENDPOINT,
        api_key: str = Constants.DEFAULT_API_KEY,
        model: str = Constants.DEFAULT_MODEL,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        verbose: bool = False) -> None:
      """
      Initialize the MergeIdeasWorkflow with configuration parameters.
      
      Args:
          api_endpoint (str): The API endpoint for the LLM service
          api_key (str): The API key for authentication
          model (str): The model identifier to use for merging
          max_tokens (int): Maximum tokens for the LLM response
          temperature (float): Sampling temperature for response generation
          verbose (bool): Enable verbose output for debugging
      """
      self.llm_api = LLMApi(api_endpoint=api_endpoint, api_key=api_key)
      self.refiner = PromptRefiner(verbose=verbose)
      self.model = model
      self.max_tokens = max_tokens
      self.temperature = temperature
      self.verbose = verbose
      # Path to the prompt template used for merging ideas
      self.idea_merger_prompt_file = str(Path(f"{Constants.DEFAULT_PROMPTS_DIRECTORY}/merge-ideas-v1.md").resolve())

    def merge_ideas(self, source_documents: dict) -> str:
      """
      Merge multiple source documents into a coherent output using LLM.
      
      Args:
          source_documents (dict): Dictionary containing documents with 'identifier' and 'content' keys
      Returns:
          str: The merged content formatted as markdown
      """
      # Load the specialized prompt template for merging ideas
      idea_merger_prompt = FileHelper.read_file(self.idea_merger_prompt_file, self.verbose)
      file_list_str = "# Source documents"
      
      # Format each document with XML-like tags for clear separation
      for doc in source_documents:
        doc_identifier = doc['identifier']
        doc_content = doc['content']
        file_list_str = f"{file_list_str}\n<document identifier=\"{doc_identifier}\">{doc_content}</document>\n"
      
      # Combine the prompt template with the formatted documents
      combined_prompt = f"{idea_merger_prompt}\n{file_list_str}\n"
      # Send the combined prompt to the LLM for processing
      response_content = self.llm_api.send(combined_prompt, model=self.model, max_tokens=self.max_tokens)
      # Clean and refine the LLM response
      processed_content = self.refiner.clean_response(response_content)

      # Format the processed content as markdown for better readability
      markdown_output = self.refiner.format_as_markdown(processed_content)
      if self.verbose:
        print(f"{Colors.MAGENTA}Processed response:\n{Colors.RESET}")
        print(f"{Colors.MAGENTA}{markdown_output}\n{Colors.RESET}")
      return markdown_output