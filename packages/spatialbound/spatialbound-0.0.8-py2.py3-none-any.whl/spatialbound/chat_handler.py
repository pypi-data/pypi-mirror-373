# spatialbound/chat_handler.py
import logging
import urllib.parse

logger = logging.getLogger(__name__)

class ChatHandler:
    """
    Handler for LLM triage chat API operations.
    """
    def __init__(self, api_handler):
        """
        Initialize the chat handler with the API handler.
        
        Args:
            api_handler: The API handler for making authorized requests.
        """
        self.api_handler = api_handler
    
    def chat(self, query):
        """
        Send a query to the LLM triage chat API.
        
        Args:
            query (str): The user's query or message.
            
        Returns:
            dict: The chat response.
        """
        # URL encode the query parameter and append it to the endpoint
        encoded_query = urllib.parse.quote(query)
        endpoint = f"/api/chat?query={encoded_query}"
        
        try:
            # Call the API handler with the existing method parameters it accepts
            response = self.api_handler.make_authorised_request(endpoint, method='GET')
            return response
        except Exception as e:
            logger.error(f"Failed to get chat response: {e}")
            return {'error': str(e)}