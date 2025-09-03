import networkx as nx
import matplotlib.pyplot as plt
import io
import base64
from ..core import tool

@tool
def visualize_graph(nodes: list[str], edges: list[tuple[str, str]]):
    """
    Creates a visual graph from a list of nodes and edges and returns it
    as a base64 encoded image data URL.

    Args:
        nodes: A list of node names (e.g., ['A', 'B', 'C']).
        edges: A list of tuples representing connections between nodes (e.g., [('A', 'B'), ('B', 'C')]).
    """
    try:
        G = nx.Graph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)

        # Create a plot of the graph
        plt.figure(figsize=(8, 6))
        nx.draw(G, with_labels=True, node_color='skyblue', node_size=2000, edge_color='gray', font_size=12, font_weight='bold')
        plt.title("Graph Visualization")

        # Save the plot to an in-memory buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        
        # Encode the image in base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Close the plot to free up memory
        plt.close()

        # Return a data URL that can be rendered in a browser or markdown
        return {"image_data_url": f"data:image/png;base64,{image_base64}"}

    except Exception as e:
        return {"error": f"Failed to create graph: {e}"}

