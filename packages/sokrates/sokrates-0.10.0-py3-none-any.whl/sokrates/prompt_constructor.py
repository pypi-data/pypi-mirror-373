from typing import Dict, List, Any
from pathlib import Path
import re

from sokrates.file_helper import FileHelper

class PromptConstructor:

    @staticmethod
    def construct_prompt_from_template_file(template_file_path:str|Path, data:Dict[str,Any]) -> str:
        """
        This method allows using a template file from a local path and replace the placeholders 
        (marked in the template by `[[PLACEHOLDER_NAME]]` ) with the content from the provided data dictionary

        see for example in: src/sokrates/prompts/coding/analyze_repository.md
        """
        if type(template_file_path) == str:
            template_file_path = Path(template_file_path)

        if not data:
            raise ValueError(f"The provided data for filling out the template file: {template_file_path} is invalid")

        if not template_file_path.is_file():
            raise ValueError(f"The provided template file: {template_file_path} does not exist")
        template_content = FileHelper.read_file(str(template_file_path))

        filled_template = PromptConstructor._replace_placeholders(template_string=template_content, replacements=data)
        return filled_template

    @staticmethod
    def _replace_placeholders(template_string:str, replacements:Dict[str,List[Any]]):
        def replace_match(match):
            placeholder_name = match.group(1)
            # Return the replacement value or keep original if not found
            return str(replacements.get(placeholder_name, match.group(0)))
        
        # Handle empty/None replacements gracefully
        if not replacements:
            return template_string
        
        # Pattern to match [[PLACEHOLDER_NAME]] format
        pattern = r'\[\[([A-Z_]+)\]\]'
        
        try:
            result = re.sub(pattern, replace_match, template_string)
            return result
        except Exception as e:
            raise RuntimeError(f"Error processing placeholders: {e}")