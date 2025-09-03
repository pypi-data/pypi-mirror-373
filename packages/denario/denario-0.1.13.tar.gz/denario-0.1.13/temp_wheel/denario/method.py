import os
import re
import cmbagent

from .key_manager import KeyManager
from .prompts.method import method_planner_prompt, method_researcher_prompt

class Method:
    """
    This class is used to develop a research project methodology based on the data of interest and the project idea.

    Args:
        work_dir: working directory.
    """

    def __init__(self,
                 research_idea: str,
                 keys: KeyManager,
                 researcher_model = "gpt-4.1-2025-04-14",
                 work_dir = None):
        
        self.researcher_model = researcher_model

        self.api_keys = keys

        if work_dir is None:
            raise ValueError("workdir must be provided")

        self.method_dir = os.path.join(work_dir, "method_generation_output")
        # Create directory if it doesn't exist
        os.makedirs(self.method_dir, exist_ok=True)

        # Set prompts
        self.planner_append_instructions = method_planner_prompt.format(research_idea=research_idea)
        self.researcher_append_instructions = method_researcher_prompt.format(research_idea=research_idea)

    def develop_method(self, data_description: str):
        """
        Develops the methods based on the data description.

        Args:
            data_description: description of the data and tools to be used.
        """

        results = cmbagent.planning_and_control_context_carryover(data_description,
                              n_plan_reviews = 1,
                              max_n_attempts = 4,
                              max_plan_steps = 4,
                              researcher_model = self.researcher_model,
                              plan_instructions = self.planner_append_instructions,
                              researcher_instructions = self.researcher_append_instructions,
                              work_dir = self.method_dir,
                              api_keys = self.api_keys
                             )
        
        chat_history = results['chat_history']
        
        try:
            for obj in chat_history[::-1]:
                if obj['name'] == 'researcher_response_formatter':
                    result = obj['content']
                    break
            task_result = result
        except:
            task_result = None
        MD_CODE_BLOCK_PATTERN = r"```[ \t]*(?:markdown)[ \t]*\r?\n(.*)\r?\n[ \t]*```"
        extracted_methodology = re.findall(MD_CODE_BLOCK_PATTERN, task_result, flags=re.DOTALL)[0]
        clean_methodology = re.sub(r'^<!--.*?-->\s*\n', '', extracted_methodology)
        return clean_methodology
