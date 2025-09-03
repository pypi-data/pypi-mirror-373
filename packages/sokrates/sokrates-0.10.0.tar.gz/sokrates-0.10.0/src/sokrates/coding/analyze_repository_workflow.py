from pathlib import Path
from typing import Dict, List, Any
import re
import logging

from sokrates.file_helper import FileHelper
from sokrates.llm_api import LLMApi
from sokrates.prompt_refiner import PromptRefiner
from sokrates.constants import Constants
from sokrates.prompt_constructor import PromptConstructor

class AnalyzeRepositoryWorkflow:
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_PROMPT_TEMPLATE_NAME = "analyze_repository.md"
    DEFAULT_MAX_TOKENS = 20000

    def __init__(self, api_endpoint: str, api_key: str) -> None:
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.llm_api = LLMApi(api_endpoint=api_endpoint, api_key=api_key)

    def analyze_repository(self, source_directory:str, model:str, temperature:float = DEFAULT_TEMPERATURE,  max_tokens:int = DEFAULT_MAX_TOKENS) -> str:
        self.logger.info(f"Started analysis for directory: {source_directory} ...")

        # TODO: think about parameterizing this
        exclude_patterns = [
            re.compile(r'\.venv'),
            re.compile(r'__pycache__'),
            re.compile(r'\.pytest_cache'),
            re.compile(r'.*\.egg-info.*'),
            re.compile(r'.*__cache__.*'),
            re.compile(r'.*site-packages.*')
        ]
        file_paths = FileHelper.directory_tree(directory=source_directory, exclude_patterns=exclude_patterns)

        # Search for readme files in file_paths
        readme_files = self._filter_readme_filepaths(file_paths=file_paths)

        # read readme contents
        readme_file_content = self._construct_readme_file_content(readme_files)
        
        # Search for markdown files in file_paths
        markdown_files = self._filter_non_readme_markdown_file_paths(file_paths=file_paths)

        # construct prompt using template
        prompt = self._construct_prompt_from_template(data={
            "ALL_FILE_PATHS": file_paths,
            "README_FILE_PATHS": readme_files,
            "MARKDOWN_FILE_PATHS": markdown_files,
            "README_FILES_CONTENT": readme_file_content
        })

        # send prompt and cleanup answer
        answer = self.llm_api.send(prompt=prompt, model=model, temperature=temperature, max_tokens=max_tokens)
        cleaned_answer = PromptRefiner().clean_response(answer)

        self.logger.info(f"Finished analysis for directory: {source_directory}")
        return cleaned_answer
        
    
    def _filter_readme_filepaths(self, file_paths:List[str]) -> List[str]:
        pattern = re.compile(r'.*README.*\.md$')
        return [path for path in file_paths if pattern.match(Path(path).name)]
    
    def _filter_non_readme_markdown_file_paths(self, file_paths:List[str]) -> List[str]:
        filtered_paths = []
        for path in file_paths:
            path_obj = Path(path)
            if path_obj.suffix == '.md' and 'README' not in path_obj.name:
                filtered_paths.append(path)
        return filtered_paths
    
    def _construct_prompt_from_template(self, data:Dict[str,Any], template_name:str = DEFAULT_PROMPT_TEMPLATE_NAME) -> str:
        template_full_path = (Constants.DEFAULT_CODING_PROMPTS_DIRECTORY / template_name).resolve()

        all_file_paths = "\n".join(f"- {path}" for path in data.get('ALL_FILE_PATHS', []))
        readme_file_paths = "\n".join(f"- {path}" for path in data.get('README_FILE_PATHS', []))
        markdown_file_paths = "\n".join(f"- {path}" for path in data.get('MARKDOWN_FILE_PATHS', []))
        readme_files_content= data.get('README_FILES_CONTENT')

        replacement_data = {
            "ALL_FILE_PATHS": all_file_paths,
            "README_FILE_PATHS": readme_file_paths,
            "MARKDOWN_FILE_PATHS": markdown_file_paths,
            "README_FILES_CONTENT": readme_files_content
        }
        return PromptConstructor.construct_prompt_from_template_file(template_file_path=template_full_path, data=replacement_data)
        
    def _construct_readme_file_content(self, readme_files:List[str]) -> str:
        readme_files_raw = FileHelper.read_multiple_files(readme_files)

        readme_file_content = ""
        for i in range(len(readme_files)):
            readme_file_content = f"{readme_file_content}<file path='{readme_files[i]}'>{readme_files_raw[i]}</file>\n\n"
        return readme_file_content