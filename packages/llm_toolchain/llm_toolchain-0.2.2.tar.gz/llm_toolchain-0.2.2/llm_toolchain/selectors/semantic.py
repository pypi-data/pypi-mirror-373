# file: semantic.py

# First, install the required libraries:
# pip install sentence-transformers numpy
from .base import BaseSelector
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
from ..core import Tool # Assuming your Tool class is in core.py

class SemanticToolSelector(BaseSelector):
    """
    Selects the most relevant tools for a given prompt using semantic search.
    """
    def __init__(self, all_tools: List[Tool], model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initializes the selector and pre-computes embeddings for all tools.

        Args:
            all_tools: A list of all available Tool objects.
            model_name: The name of the sentence-transformer model to use.
        """
        self.all_tools = all_tools
        self.model = SentenceTransformer(model_name)
        
        # Pre-compute embeddings for all tool descriptions for efficiency
        print("Pre-computing tool embeddings...")
        tool_descriptions = [tool.description for tool in self.all_tools]
        self.tool_embeddings = self.model.encode(tool_descriptions, convert_to_tensor=False)
        print("Embeddings computed.")

    def select_tools(self, prompt: str, top_k: int = 3) -> set[Tool]:
        """
        Selects the top_k most relevant tools for a given prompt.

        Args:
            prompt: The user's input prompt.
            top_k: The number of top tools to return.

        Returns:
            A list of the most relevant Tool objects.
        """
        print(f"Selecting top {top_k} tools for prompt: '{prompt}'")
        if top_k <= 0:
            return []
            
        # 1. Generate the embedding for the incoming prompt
        prompt_embedding = self.model.encode(prompt, convert_to_tensor=False)

        # 2. Calculate cosine similarity between the prompt and all tool embeddings
        # The dot product of normalized vectors is the cosine similarity
        prompt_embedding_norm = prompt_embedding / np.linalg.norm(prompt_embedding)
        tool_embeddings_norm = self.tool_embeddings / np.linalg.norm(self.tool_embeddings, axis=1, keepdims=True)
        similarities = np.dot(tool_embeddings_norm, prompt_embedding_norm)

        # 3. Get the indices of the top_k most similar tools
        top_k_indices = np.argsort(similarities)[-top_k:][::-1]

        # 4. Return the corresponding Tool objects
        selected_tools = {self.all_tools[i] for i in top_k_indices}
        
        print(f"Selected tools for prompt: {[tool.name for tool in selected_tools]}")
        return selected_tools