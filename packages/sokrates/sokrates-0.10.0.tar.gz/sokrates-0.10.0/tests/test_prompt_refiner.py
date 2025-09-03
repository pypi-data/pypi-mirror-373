import unittest
import re
from sokrates import PromptRefiner

class TestPromptRefiner(unittest.TestCase):
    def setUp(self):
        self.refiner = PromptRefiner(verbose=False)
        self.verbose_refiner = PromptRefiner(verbose=True)

    def test_combine_refinement_prompt(self):
        input_prompt = "This is my original prompt."
        refinement_prompt = "Please refine the following prompt:"
        expected_output = "Please refine the following prompt:\n <original_prompt>\nThis is my original prompt.\n</original_prompt>"
        refined = self.refiner.combine_refinement_prompt(input_prompt, refinement_prompt)
        self.assertTrue(input_prompt in refined)
        self.assertTrue(refinement_prompt in refined)

        with self.assertRaises(ValueError):
            self.refiner.combine_refinement_prompt("", refinement_prompt)

    def test_format_as_markdown(self):
        # Test case where content is already markdown
        markdown_content = "# Hello\n**World**"
        self.assertEqual(self.refiner.format_as_markdown(markdown_content), markdown_content)

        # Test case where content is plain text
        plain_text_content = "This is plain text."
        # markdownify converts plain text to markdown, typically by escaping special characters
        # and sometimes adding paragraph tags. We'll check if it's been processed.
        # The exact output of markdownify can vary slightly, so we'll check for a reasonable transformation.
        formatted_content = self.refiner.format_as_markdown(plain_text_content)
        self.assertIsInstance(formatted_content, str)
        self.assertEqual(formatted_content, plain_text_content) # Should not be transformed

    def test_clean_response(self):
        # Test removal of think blocks
        response_with_meta = "<think>This is a thought.</think>Actual content.<analysis>Some analysis.</analysis>"
        self.assertEqual(self.refiner.clean_response(response_with_meta), "Actual content.<analysis>Some analysis.</analysis>")

        # Test removal of common prefixes
        response_with_prefix = "Here's the refined prompt: My refined content."
        self.assertEqual(self.refiner.clean_response(response_with_prefix), "My refined content.")

        # Test removal of stray tags
        response_with_stray_tags = "Content with </think>stray<tool_code> tags."
        self.assertEqual(self.refiner.clean_response(response_with_stray_tags), "Content with stray tags.")
        
        # test removal of answer tags
        response_with_answer_tags = "<answer>My Answer</answer>"
        self.assertEqual(self.refiner.clean_response(response_with_answer_tags), "My Answer")
        
        response_with_answer_tags_2 = "<think> sagasgasg </think> \n <answer>My Answer</answer>"
        self.assertEqual(self.refiner.clean_response(response_with_answer_tags_2), "My Answer")
        
        # Test with multiple types of cleaning
        complex_response = """
        <thinking>Initial thoughts</thinking>
        Here's the refined prompt:

        This is the actual refined content.

        <meta>Some meta info</meta>
        And more content.
        </response>
        """
        refined = self.refiner.clean_response(complex_response)
        
        self.assertTrue(not ("<meta>" in refined))
        self.assertTrue(not ("</meta>" in refined))
        self.assertTrue(not ("Some meta info" in refined))
        self.assertTrue(not ("</response>" in refined))
        self.assertTrue(not ("<thinking>" in refined))
        self.assertTrue(not ("</thinking>" in refined))
        self.assertTrue(not ("Initial thoughts" in refined))
        self.assertTrue("This is the actual refined content." in refined)
        self.assertTrue("And more content." in refined)
        

        # Test with no cleaning needed
        clean_response_text = "This is a clean response."
        self.assertEqual(self.refiner.clean_response(clean_response_text), clean_response_text)

if __name__ == '__main__':
    unittest.main()