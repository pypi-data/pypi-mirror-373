# This script defines the `IdeaGenerationWorkflow` class, which orchestrates a
# multi-stage process for generating and refining prompts using Large Language Models (LLMs).
# It supports generating initial topics, creating detailed execution prompts based on templates,
# refining these prompts for clarity and effectiveness, executing them with an LLM,
# and managing the output. This workflow is designed to automate and enhance
# the prompt engineering process.

from pathlib import Path
from sokrates import LLMApi
from sokrates import PromptRefiner
from sokrates import Colors
from sokrates import FileHelper
from sokrates import Constants
from sokrates import Utils
from sokrates import OutputPrinter
import os
import json
import time

class IdeaGenerationWorkflow:
    """
    Orchestrates a multi-step workflow for generating, refining, and executing LLM prompts.
    This class manages the flow from initial topic generation to final output,
    leveraging different LLM models for various stages of the process.
    """
    DEFAULT_TOPIC_GENERATOR_PATH = Path("prompt_generators/topic-generator.md")
    DEFAULT_PROMPT_GENERATOR_PATH = Path("prompt_generators/prompt-generator-v1.md")
    DEFAULT_REFINEMENT_FILENAME = "refine-prompt.md"
    MAXIMUM_CATEGORIES_TO_PICK = 5
  
    def __init__(self, api_endpoint: str, api_key: str,
        topic_input_file: str = None,
        topic: str = None,
        refinement_prompt_file: str = None,
        prompt_generator_file: str = None,
        output_directory: str = None,
        generator_llm_model: str = None,
        refinement_llm_model: str = None,
        execution_llm_model: str = None,
        topic_generation_llm_model: str = None,
        idea_count: int = 2,
        max_tokens: int = 20000, temperature: float = 0.7, verbose: bool = False):
        """
        Initializes the IdeaGenerationWorkflow.

        Args:
            api_endpoint (str): The API endpoint for the LLM server.
            api_key (str): The API key for the LLM server.
            topic (str, optional): A Topic provided as string. 
                                                If None , a topic will be generated. Defaults to None.
            topic_input_file (str, optional): Path to a file containing the initial topic.
                                                If None, a topic will be generated. Defaults to None.
            refinement_prompt_file (str, optional): Path to the prompt template for refining generated prompts. Defaults to None.
            prompt_generator_file (str, optional): Path to the prompt template for generating execution prompts. Defaults to None.
            output_directory (str, optional): Directory where generated outputs will be saved. Defaults to None.
            generator_llm_model (str, optional): The LLM model to use for generating execution prompts.
                                                 Defaults to Constants.DEFAULT_MODEL.
            refinement_llm_model (str, optional): The LLM model to use for refining prompts.
                                                  Defaults to Constants.DEFAULT_MODEL.
            execution_llm_model (str, optional): The LLM model to use for executing the final prompts.
                                                 Defaults to Constants.DEFAULT_MODEL.
            meta_llm_model (str, optional): The LLM model to use for generating the initial topic (meta-prompt).
                                            Defaults to Constants.DEFAULT_MODEL.
            max_tokens (int): Maximum tokens for LLM responses. Defaults to 20000.
            temperature (float): Temperature for LLM responses. Defaults to 0.7.
            verbose (bool): If True, enables verbose output. Defaults to False.
        """
        if topic_input_file is not None and topic is not None:
            raise Exception("A topic input file and a topic was provided. Only provide one of both. Failing workflow.")
        
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.llm_api = LLMApi(api_endpoint=api_endpoint,
                               api_key=api_key)
        self.prompt_refiner = PromptRefiner(verbose=verbose)
        self.topic = topic
        self.topic_input_file = topic_input_file
        
        topic_generation_instructions_file = str((Path(Constants.DEFAULT_PROMPTS_DIRECTORY) / self.DEFAULT_TOPIC_GENERATOR_PATH ).resolve() )
        OutputPrinter.print_info(f"No topic_generator_file, topic_input_file or topic specified. Using the default topic generation instructions in {topic_generation_instructions_file}", Colors.BRIGHT_MAGENTA)
        self.topic_generator_file = topic_generation_instructions_file
        
        self.refinement_prompt_file = refinement_prompt_file
        if self.refinement_prompt_file is None:
            full_refinement_filepath = str((Path(Constants.DEFAULT_PROMPTS_DIRECTORY) / self.DEFAULT_REFINEMENT_FILENAME ).resolve() )
            OutputPrinter.print_info(f"No refinement_prompt_file specified. Using the default refinement prompt instructions in {full_refinement_filepath}", Colors.BRIGHT_MAGENTA)
            self.refinement_prompt_file = full_refinement_filepath
        
        self.prompt_generator_file = prompt_generator_file
        if self.prompt_generator_file is None:
            full_pg_filepath = str((Path(Constants.DEFAULT_PROMPTS_DIRECTORY) / self.DEFAULT_PROMPT_GENERATOR_PATH ).resolve())
            OutputPrinter.print_info(f"No prompt_generator_file specified. Using the default prompt generator instructions in {full_pg_filepath}", Colors.BRIGHT_MAGENTA)
            self.prompt_generator_file = full_pg_filepath
        
        self.output_directory = output_directory
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.verbose = verbose
        
        self.idea_count = idea_count
        
        self.generator_llm_model = generator_llm_model if generator_llm_model else Constants.DEFAULT_MODEL
        self.refinement_llm_model = refinement_llm_model if refinement_llm_model else Constants.DEFAULT_MODEL
        self.execution_llm_model = execution_llm_model if execution_llm_model else Constants.DEFAULT_MODEL
        self.topic_generation_llm_model = topic_generation_llm_model if topic_generation_llm_model else Constants.DEFAULT_MODEL
    
    def pick_topic_categories_from_json(self) -> list:
        """
        Selects a random number of thematic categories from a JSON file.

        This method reads topic categories from a predefined JSON file and randomly
        selects between 1 and MAXIMUM_CATEGORIES_TO_PICK categories to use for 
        topic generation.

        Returns:
            list: A list of randomly selected topic categories.
        """
        topic_categories_json_path = str(Path(f"{Constants.DEFAULT_PROMPTS_DIRECTORY}/context/topic_categories.json").resolve())
        categories_object = FileHelper.read_json_file(topic_categories_json_path, self.verbose)
        all_categories = categories_object["topic_categories"]
        number_of_categories_to_pick = Utils.generate_random_int(min_value=1, max_value=self.MAXIMUM_CATEGORIES_TO_PICK)
        categories = []
        while True:
            if len(categories) >= number_of_categories_to_pick:
                break
            picked_index = Utils.generate_random_int(0,len(all_categories)-1)
            categories.append(all_categories[picked_index])
            categories = list(set(categories))
        return categories
        
    def generate_topic_generation_prompt(self, topic_generation_instructions) -> str:
        """
        Generates a prompt for topic generation by incorporating thematic categories.

        This method takes the base topic generation instructions and appends 
        information about thematic categories to guide topic creation.

        Args:
            topic_generation_instructions (str): The base instructions for generating a topic.

        Returns:
            str: A complete prompt combining the original instructions with category information.
        """
        ret = topic_generation_instructions
        
        categories = self.pick_topic_categories_from_json()
        if self.verbose:
            OutputPrinter.print_info("Random categories picked:", categories)    
        
        if len(categories) == 1:
            return f"{topic_generation_instructions}\n\n# Thematic field to use for topic generation\nGenerate a topic from the thematic field of {categories[0]}"

        category_definitions="# Thematic fields to combine for topic generation\n"
        category_definitions=f"{category_definitions}Combine the following thematic fields for generating a topic:\n"
        for cat in categories:
            category_definitions=f"- {cat}\n"
        
        return f"{topic_generation_instructions}\n\n{category_definitions}"
        
    def generate_or_set_topic(self) -> str:
        """
        Generates an initial topic using a meta-prompt or reads it from a file.

        Returns:
            str: The generated or read topic content.
        """
        if self.topic:
            return self.topic
        
        if self.topic_input_file:
            return FileHelper.read_file(self.topic_input_file, self.verbose)
            
        else:
            topic_generation_instructions = FileHelper.read_file(self.topic_generator_file, self.verbose)
            topic_generation_prompt = self.generate_topic_generation_prompt(topic_generation_instructions)

            response = self.llm_api.send(
                prompt=topic_generation_prompt,
                model=self.topic_generation_llm_model,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            cleaned_response = self.prompt_refiner.clean_response(response)
            OutputPrinter.print_info("Generated Topic", cleaned_response, Colors.BRIGHT_MAGENTA, Colors.GREEN)
            return cleaned_response
    
    def execute_prompt_generation(self) -> list[str]:
        """
        Generates a list of execution prompts based on a template and the initial topic.
        The generated prompts are expected to be in JSON format and are saved to a file.

        Returns:
            list[str]: A list of generated prompts.
        """
        prompt_generator_template = FileHelper.read_file(self.prompt_generator_file, self.verbose)
        prompt_count_additional_instruction = f"# Number of prompts to generate\nGenerate a total of {self.idea_count} prompts"
        combined_prompt = f"{prompt_generator_template}\n{self.topic}\n---\n{prompt_count_additional_instruction}"
        
        json_response = self.llm_api.send(
            prompt=combined_prompt,
            model=self.generator_llm_model,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        
        cleaned_json = self.prompt_refiner.clean_json_response(json_response)
        cleaned_json = self.prompt_refiner.clean_response_from_markdown(cleaned_json)
        
        if self.output_directory:
            json_path = os.path.join(self.output_directory, "generated_prompts.json")
            FileHelper.write_to_file(json_path, cleaned_json, self.verbose)
            OutputPrinter.print_file_created(json_path)
        
        OutputPrinter.print_info("Generated prompts", cleaned_json, Colors.BRIGHT_MAGENTA, Colors.GREEN)
        return json.loads(cleaned_json)["prompts"]
    
    def refine_and_execute_prompt(self, execution_prompt: str, index: int) -> str:
        """
        Refines a given execution prompt and then executes it using an LLM.

        Args:
            execution_prompt (str): The prompt to be refined and executed.
            index (int): The index of the prompt (used for logging or naming).

        Returns:
            str: The final output from the LLM after executing the refined prompt.
        """
        combined_refinement = self.prompt_refiner.combine_refinement_prompt(
            execution_prompt,
            FileHelper.read_file(self.refinement_prompt_file, self.verbose)
        )
        
        refined_prompt = self.llm_api.send(
            combined_refinement,
            model=self.refinement_llm_model,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        cleaned_refined = self.prompt_refiner.clean_response(refined_prompt)
        
        final_output = self.llm_api.send(
            cleaned_refined,
            model=self.execution_llm_model,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        cleaned_response = self.prompt_refiner.clean_response(final_output)
        return cleaned_response
    
    def run(self) -> list[str]:
        """
        Executes the full idea generation workflow. This includes:
        1. Generating or setting the initial topic.
        2. Generating a set of execution prompts.
        3. Iterating through each generated prompt, refining it, and executing it with an LLM.
        4. Saving the final outputs to files in a timestamped directory.
        5. Reporting the total execution time.
        """
        if self.output_directory:
            self.output_directory = FileHelper.generate_postfixed_sub_directory_name(self.output_directory)
        start_time = time.time()
        
        OutputPrinter.print_header("🚀 Idea Generator 🚀", Colors.BRIGHT_CYAN, 60)
        
        self.topic = self.generate_or_set_topic()
        
        execution_prompts = self.execute_prompt_generation()
        
        created_files = []
        created_ideas = []
        for idx, prompt in enumerate(execution_prompts):
            try:
                result = self.refine_and_execute_prompt(prompt, idx+1)
                created_ideas.append(result)
                
                if self.output_directory:
                    output_filename = os.path.join(
                        self.output_directory,
                        FileHelper.clean_name(f"output_{idx+1}_{self.execution_llm_model}.md")
                    )
                    FileHelper.write_to_file(output_filename, result, self.verbose)
                    created_files.append(output_filename)
            except Exception as e:
                OutputPrinter.print_error(f"Issue processing prompt {idx}: {str(e)}")
        
        end_time = time.time()
        total_seconds = round(end_time - start_time, 2)
        OutputPrinter.print_header("🎉 Workflow Completed! 🎉", Colors.BRIGHT_GREEN, 60)
        OutputPrinter.print_info("Total execution time", f"{total_seconds} seconds", Colors.BRIGHT_MAGENTA, Colors.GREEN)
        
        for f in created_files:
            OutputPrinter.print_file_created(f)
        return created_ideas
