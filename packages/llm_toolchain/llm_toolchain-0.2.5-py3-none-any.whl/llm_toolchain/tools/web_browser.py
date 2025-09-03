import requests
from bs4 import BeautifulSoup
from ..core import tool

@tool
def open_and_read_website(url: str):
    """
    Opens a website, extracts its main text content, and returns it.
    Use this to access real-time information from the internet or to read
    the content of a specific webpage.

    Args:
        url: The full URL of the website to read (e.g., 'https://www.example.com').
    """
    if not url.startswith(('http://', 'https://')):
        return {"error": "Invalid URL. Please provide a full URL starting with http:// or https://."}

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Use BeautifulSoup to parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        # Get text and clean it up
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = '\n'.join(chunk for chunk in chunks if chunk)

        # Return a summary or a snippet to avoid huge outputs
        max_length = 2000
        if len(clean_text) > max_length:
            return {"content_snippet": clean_text[:max_length] + "..."}
        else:
            return {"content": clean_text}

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to access URL: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

