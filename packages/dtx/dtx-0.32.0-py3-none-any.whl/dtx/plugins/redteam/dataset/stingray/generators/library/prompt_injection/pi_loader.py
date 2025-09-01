import random

from . import pi_data
from .prompting import build_prompts


class PIDataLoader(object):
    """
    PIDataLoader is responsible for loading and managing prompt injection data.

    Examples:
    =========
        from dtx.plugins.redteam.dataset.stingray.generators.prompt_injection import PIDataLoader
        pidata = PIDataLoader("hate-humans")
        len(pidata.get_prompts())
    """

    def __init__(
        self,
        rogue_string,
        max_prompts=None,
        seed: int | float | str | bytes | bytearray | None = None,
    ):
        """
        Initialize the PIDataLoader with the given rogue string, maximum prompts, and seed.

        Args:
            rogue_string (str): The rogue string to be used in the prompt injection.
            max_prompts (int, optional): The maximum number of prompts to load. Defaults to None.
            seed (int | float | str | bytes | bytearray | None, optional): The seed for random operations. Defaults to None.
        """
        self.prompts = []
        self._seed = seed
        self._pi_prompt_data = pi_data
        self._pi_build_prompts = build_prompts
        self._max_prompts = max_prompts
        self._rogue_string = rogue_string
        self._load_data_all_attacks()

    def get_prompts(self):
        """
        Get the list of prompts.

        Returns:
            list: The list of prompts.
        """
        return self.prompts

    def _load_data_all_attacks(self):
        """
        Load all attack data based on the configuration and populate the prompts.
        """
        # Define the configuration for the prompts
        prompt_config = {
            "base": {
                "text": self._pi_prompt_data.ALL_OPENAI_PLAYGROUND_PROMPTS,
            },
            "attack": {
                "text": (
                    self._pi_prompt_data.goal_hikacking_attacks["ignore-print"],
                    self._pi_prompt_data.goal_hikacking_attacks["ignore-say"],
                    self._pi_prompt_data.goal_hikacking_attacks["ignore-print-upper"],
                    self._pi_prompt_data.goal_hikacking_attacks["nevermind"],
                    self._pi_prompt_data.goal_hikacking_attacks["screaming-stop"],
                ),
                "rogue_string": self._pi_prompt_data.rogue_strings[self._rogue_string],
                "scoring": "match_rogue_to_output",
                "settings": {
                    "escape": self._pi_prompt_data.escape_chars["n"],
                    "delimiter": self._pi_prompt_data.delimiter_chars["dash"],
                    "escape_length": 10,
                    "escape_times": 2,
                },
            },
            "config": {
                "id": (0, 1, 2, 3),
            },
            "visualization": {"columns": ()},
        }

        # Clear any existing prompts
        self.prompts = []

        # Build the prompts based on the configuration
        self.pi_prompts = self._pi_build_prompts(prompt_config)

        # Append each prompt to the prompts list
        for pi_prompt in self.pi_prompts:
            self.prompts.append(pi_prompt["prompt"])

        # If a maximum number of prompts is specified, shuffle and limit the prompts
        if self._max_prompts:
            random.seed(self._seed)
            random.shuffle(self.prompts)
            self.prompts = self.prompts[-self._max_prompts :]
