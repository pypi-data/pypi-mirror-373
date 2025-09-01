import requests
from typing import Any, Dict, List, Union

class XplainDBClient:
    """
    A client for interacting with a XplainDBClient server.
    It is recommended to create a client instance using the XplainDBClient.create_db() classmethod when to create a database.
    
    Args:
        base_url (str): The base URL of the XplainDB server.
        db_name (str): The name of the database to connect to.
        api_key (str): The admin API key for the database.
    """
    def __init__(self, base_url: str, db_name: str, api_key: str):
        if not api_key:
            raise ValueError("An API key is required to initialize the client.")
        
        self.base_url = base_url.rstrip('/')
        self.db_name = db_name
        self.api_key = api_key
        self._rest_url = f"{self.base_url}/{self.db_name}/query"
        self._graphql_url = f"{self.base_url}/{self.db_name}/graphql"
        
        # Use a session object for connection pooling and efficiency
        self._session = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json",
            "X-API-Key": self.api_key
        })

    @classmethod
    def create_db(cls, base_url: str, db_name: str):
        """
        Connects to a XplainDB database.
        If the database is new, it will be created, and its root admin key will be retrieved.
        
        Returns:
            An authenticated XplainDBClient instance.
        """
        print(f"--- Bootstrapping database '{db_name}' and getting admin key...")
        bootstrap_url = f"{base_url.rstrip('/')}/{db_name}/bootstrap"
        try:
            response = requests.get(bootstrap_url, timeout=10)
            response.raise_for_status()
            key = response.json().get("admin_key")
            if not key:
                raise ValueError("Admin key not found in bootstrap response.")
            print("✅ Success: Retrieved admin key.")
            # Create and return a new instance of the class
            return cls(base_url=base_url, db_name=db_name, api_key=key)
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Could not connect to the XplainDB server at {base_url}. Is it running?") from e

    def _make_request(self, payload: Dict[str, Any], endpoint_url: str) -> Dict[str, Any]:
        """Internal helper to make authenticated requests using the session."""
        try:
            response = self._session.post(endpoint_url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            raise ConnectionError(f"API request failed: {e.response.status_code} {e.response.text}") from e

    def sql(self, query: str) -> List[Dict[str, Any]]:
        """Executes a raw SQL query."""
        response = self._make_request({"query": query}, self._rest_url)
        return response.get("result", [])

    def nosql(self, command: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Executes a NoSQL command."""
        response = self._make_request({"query": command}, self._rest_url)
        return response.get("result", [])

    def graph(self, command: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Executes a Graph command."""
        response = self._make_request({"query": command}, self._rest_url)
        return response.get("result", [])

    def vector(self, command: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Executes a Vector command."""
        response = self._make_request({"query": command}, self._rest_url)
        return response.get("result", [])

    def graphql(self, query: str) -> Dict[str, Any]:
        """Executes a GraphQL query."""
        response = self._make_request({"query": query}, self._graphql_url)
        return response.get("data", {})

    def create_api_key(self, permissions: str = "readonly") -> Dict[str, str]:
        """Creates a new API key (requires admin privileges)."""
        command = {"type": "create_key", "permissions": permissions}
        result = self.nosql(command)
        return result[0] if result else {}