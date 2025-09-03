from abc import ABC, abstractmethod




class BaseSelector(ABC):
    """
    An abstract base class for tool selectors. Subclasses must implement the
    select_tools method to define their selection strategy.
    """
    @abstractmethod
    def select_tools(self, prompt: str, top_k: int = 3) -> set:
        """
        Selects the most relevant tools for a given prompt.

        Args:
            prompt: The user's input prompt.
            top_k: The number of top tools to return.

        Returns:
            A set of the most relevant Tool objects.
        """
        pass