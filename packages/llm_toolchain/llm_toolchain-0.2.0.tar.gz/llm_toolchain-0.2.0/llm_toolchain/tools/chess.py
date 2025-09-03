# file: chess_tools.py (API Version)

import requests
from ..core import tool # Assuming 'tool' decorator is in ..core

# The Lichess analysis API endpoint
LICHESS_API_URL = "https://lichess.org/api/cloud-eval"

@tool
def analyse_position_with_api(fen: str):
    """
    Analyzes a chess position from a FEN string using the Lichess cloud evaluation API.
    This provides the engine's evaluation, the best move, and the principal variation.
    
    Args:
        fen: The Forsyth-Edwards Notation (FEN) string representing the chess position.
    """
    params = {"fen": fen}
    try:
        # Make a GET request to the Lichess API
        response = requests.get(LICHESS_API_URL, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        data = response.json()

        # Check if Lichess returned an error (e.g., for an invalid FEN)
        if "error" in data:
            return {"error": f"Lichess API error: {data['error']}"}

        # Extract the principal variation (the sequence of best moves)
        pv_string = data.get("pvs", [{}])[0].get("moves", "")
        principal_variation = pv_string.split()
        best_move = principal_variation[0] if principal_variation else "N/A"

        # Extract the evaluation in centipawns
        centipawns = data.get("pvs", [{}])[0].get("cp", "N/A")
        
        evaluation_text = "Position is roughly equal."
        if isinstance(centipawns, int):
            side = "White" if centipawns > 0 else "Black"
            advantage = abs(centipawns) / 100.0
            evaluation_text = f"{side} has an advantage of {advantage:.2f} pawns."
        # Lichess also provides mate scores
        elif "mate" in data.get("pvs", [{}])[0]:
            mate_in = data["pvs"][0]["mate"]
            side = "White" if mate_in > 0 else "Black"
            evaluation_text = f"{side} has a forced mate in {abs(mate_in)} moves."

        return {
            "fen": fen,
            "evaluation_text": evaluation_text,
            "best_move": best_move,
            "principal_variation": principal_variation,
            "centipawns": centipawns
        }

    except requests.exceptions.HTTPError as http_err:
        return {"error": f"HTTP error occurred: {http_err}"}
    except requests.exceptions.RequestException as req_err:
        return {"error": f"A network error occurred: {req_err}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}