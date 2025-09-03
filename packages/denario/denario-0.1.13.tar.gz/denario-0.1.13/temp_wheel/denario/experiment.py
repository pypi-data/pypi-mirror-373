from typing import List
import os
import re
import cmbagent

from .key_manager import KeyManager
from .prompts.experiment import experiment_planner_prompt, experiment_engineer_prompt, experiment_researcher_prompt

class Experiment:
    """
    This class is used to perform the experiment.
    TODO: improve docstring
    """

    def __init__(self,
                 research_idea: str,
                 methodology: str,
                 keys: KeyManager,
                 involved_agents: List[str] = ['engineer', 'researcher'],
                 engineer_model: str = "claude-3-7-sonnet-20250219",
                 researcher_model: str = "o3-mini-2025-01-31",
                 work_dir = None,
                 restart_at_step: int = -1):
        
        self.engineer_model = engineer_model
        self.researcher_model = researcher_model
        self.restart_at_step = restart_at_step
        
        if work_dir is None:
            raise ValueError("workdir must be provided")

        self.api_keys = keys

        self.experiment_dir = os.path.join(work_dir, "experiment_generation_output")
        # Create directory if it doesn't exist
        os.makedirs(self.experiment_dir, exist_ok=True)

        involved_agents_str = ', '.join(involved_agents)

        # Set prompts
        self.planner_append_instructions = experiment_planner_prompt.format(
            research_idea = research_idea,
            methodology = methodology,
            involved_agents_str = involved_agents_str
        )
        self.engineer_append_instructions = experiment_engineer_prompt.format(
            research_idea = research_idea,
            methodology = methodology,
        )
        self.researcher_append_instructions = experiment_researcher_prompt.format(
            research_idea = research_idea,
            methodology = methodology,
        )

    def run_experiment(self, data_description: str, **kwargs):
        """
        Run the experiment.
        TODO: improve docstring
        """

        print(f"Engineer model: {self.engineer_model}")
        print(f"Researcher model: {self.researcher_model}")
        
        results = cmbagent.planning_and_control_context_carryover(data_description,
                            n_plan_reviews = 1,
                            max_n_attempts = 10,
                            max_plan_steps = 6,
                            max_rounds_control = 500,
                            engineer_model = self.engineer_model,
                            researcher_model = self.researcher_model,
                            plan_instructions=self.planner_append_instructions,
                            researcher_instructions=self.researcher_append_instructions,
                            engineer_instructions=self.engineer_append_instructions,
                            work_dir = self.experiment_dir,
                            api_keys = self.api_keys,
                            restart_at_step = self.restart_at_step
                            )
        chat_history = results['chat_history']
        final_context = results['final_context']
        
        try:
            for obj in chat_history[::-1]:
                if obj['name'] == 'researcher_response_formatter':
                    result = obj['content']
                    break
            task_result = result
        except:
            task_result = None
            
        MD_CODE_BLOCK_PATTERN = r"```[ \t]*(?:markdown)[ \t]*\r?\n(.*)\r?\n[ \t]*```"
        extracted_results = re.findall(MD_CODE_BLOCK_PATTERN, task_result, flags=re.DOTALL)[0]
        clean_results = re.sub(r'^<!--.*?-->\s*\n', '', extracted_results)
        self.results = clean_results
        self.plot_paths = final_context['displayed_images']

        return None


