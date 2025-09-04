import os
import warnings
import logging
from typing import List, Dict, Any, Optional, Union
import requests
from dataclasses import dataclass

try:
    from weavium import __version__
except ImportError:
    __version__ = "unknown"


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LLMMessage:
    """Represents a message in a conversation"""
    role: str
    content: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {"role": self.role, "content": self.content}


@dataclass
class CompressionResult:
    """Result of a compression operation"""
    result: Union[str, List[LLMMessage], None]  # The compressed content - string if input was string, List[LLMMessage] if input was messages, None if failed
    compression_rate: str  # Achieved compression rate as percentage (e.g., "20%")
    original_tokens: int  # Number of tokens in the original input before compression
    compressed_tokens: int  # Number of tokens in the compressed output
    api_call_id: Optional[int] = None  # Unique identifier for this API call, used for preview the compression result on the weavium platform
    
    @classmethod
    def from_response(cls, response: requests.Response, original_messages: List[LLMMessage], input_was_string: bool = False) -> 'CompressionResult':
        """Create CompressionResult from API response"""
        data = response.json()
        
        # Extract compressed messages from response
        compressed_messages = [
            LLMMessage(role=msg["role"], content=msg["content"])
            for msg in data["messages"]
        ]
        
        if input_was_string:
            user_messages = [msg for msg in compressed_messages if msg.role == "user"]
            result = user_messages[-1].content if user_messages else ""
        else:
            result = compressed_messages
        
        return cls(
            result=result,
            compression_rate=response.headers.get("X-Compression-Rate", "unknown"),
            original_tokens=int(response.headers.get("X-Compression-Original-Tokens", 0)),
            compressed_tokens=int(response.headers.get("X-Compression-Compressed-Tokens", 0)),
            api_call_id=int(response.headers.get("X-API-Call-ID")) if response.headers.get("X-API-Call-ID") else None,
        )


@dataclass
class InjectResult:
    """Result of an inject operation"""
    dataset_id: str
    dataset_name: str
    items_created: int
    system_prompt_hash: str
    
    @classmethod
    def from_response(cls, response: requests.Response) -> 'InjectResult':
        """Create InjectResult from API response"""
        data = response.json()
        return cls(
            dataset_id=data["dataset_id"],
            dataset_name=data["dataset_name"],
            items_created=data["items_created"],
            system_prompt_hash=data["system_prompt_hash"]
        )


class WeaviumClient:
    """
    Python client for the Weavium API.
    
    Provides methods to compress prompts and inject data into datasets.
    """
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        base_url: str = "https://api.weavium.ai",
        timeout: int = 30
    ):
        """
        Initialize the Weavium client.
        
        Args:
            api_key: Weavium API key. If not provided, will look for WEAVIUM_API_KEY environment variable.
            base_url: Base URL for the Weavium API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
        self.api_key = api_key or os.getenv('WEAVIUM_API_KEY')
        
        if not self.api_key:
            warnings.warn(
                "No API key provided. Set WEAVIUM_API_KEY environment variable or pass api_key parameter.",
                UserWarning
            )
            logger.warning("No API key provided. API calls will fail without proper authentication.")
        else:
            logger.info(f"[Weavium] Configured")
        
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                'x-weavium-api-key': self.api_key,
                'Content-Type': 'application/json',
                'x-weavium-client-version': __version__
            })
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> requests.Response:
        """
        Make a request to the Weavium API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            data: Request data
            headers: Additional headers
            
        Returns:
            Response object
            
        Raises:
            requests.RequestException: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        # Merge additional headers
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                headers=request_headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response
        except requests.exceptions.ConnectionError as e:
            # Check if it's a max retries error
            if "Max retries exceeded" in str(e):
                error_msg = f"[Weavium] Connection failed: Unable to reach Weavium API at {self.base_url}. Please try again."
                logger.error(error_msg)
                raise requests.RequestException(error_msg) from e
            else:
                logger.error(f"Connection error: {e}")
                raise
        except requests.exceptions.Timeout as e:
            error_msg = f"[Weavium] Request timed out after {self.timeout} seconds. Please try again later."
            logger.error(error_msg)
            raise requests.RequestException(error_msg) from e
        except requests.exceptions.HTTPError as e:
            error_msg = f"[Weavium] HTTP error {e.response.status_code}: {e.response.reason}"
            if e.response.status_code == 401:
                error_msg += " - Please check your API key"
            elif e.response.status_code == 429:
                error_msg += " - Rate limit exceeded, please try again later"
            elif e.response.status_code >= 500:
                error_msg += " - Server error, please try again later"
            logger.error(error_msg)
            raise requests.RequestException(error_msg) from e
        except requests.RequestException as e:
            logger.error(f"[Weavium] Request failed: {e}")
            raise
    
    def compress(
        self,
        input: Union[List[Union[LLMMessage, Dict[str, str]]], str],
        compression_rate: float = 0.2,
        system_prompt: Optional[str] = None,
    ) -> CompressionResult:
        """
        Compress prompt using the Weavium compression model.
        
        Args:
            input: Either a openai compatible list of messages in the conversation (each message should have 'role' and 'content') 
                   or a single string to compress as user message. The last user message is compressed.
            compression_rate: Target compression rate between 0.1 to 0.7 (0.1 will remove 10% of the tokens). Defaults to 0.2.
            system_prompt: Optional system prompt to consider when compressing. The system prompt is left as is.
            
        Returns:
            CompressionResult: A dataclass containing the compression results and metadata:
            
            - result (Union[str, List[LLMMessage], None]): The compressed content
              * str: If input was a string, contains the compressed text
              * List[LLMMessage]: If input was a message list, contains compressed messages
              * None: If compression failed or returned empty result
            - compression_rate (str): Achieved compression rate as percentage (e.g., "20%")
            - original_tokens (int): Number of tokens in the original input before compression
            - compressed_tokens (int): Number of tokens in the compressed output
            - api_call_id (Optional[int]): Unique identifier for this API call, used for preview the compression result on the weavium platform
            
            Note: If input was a string, 'result' field contains the compressed string.
                  If input was a list, 'result' field contains the compressed messages list with the last user message compressed.
            
        Raises:
            ValueError: If input is invalid
            requests.RequestException: If the API request fails
        """
        # Track if input was a string for return format
        input_was_string = isinstance(input, str)
        
        # Handle string input
        if isinstance(input, str):
            llm_messages = []
            if system_prompt:
                llm_messages.append(LLMMessage(role="system", content=system_prompt))
            llm_messages.append(LLMMessage(role="user", content=input))
        else:
            # Handle list input (existing logic)
            if not input:
                raise ValueError("Input list cannot be empty")
            
            # Convert dict messages to LLMMessage objects
            llm_messages = []
            for msg in input:
                if isinstance(msg, dict):
                    if 'role' not in msg or 'content' not in msg:
                        raise ValueError("Each message must have 'role' and 'content' keys")
                    llm_messages.append(LLMMessage(role=msg['role'], content=msg['content']))
                elif isinstance(msg, LLMMessage):
                    llm_messages.append(msg)
                else:
                    raise ValueError(f"Invalid message type: {type(msg)}")
        
        # Prepare request data
        request_data = {
            "messages": [msg.to_dict() for msg in llm_messages]
        }
        
        # Prepare headers with compression parameters
        headers = {
            "X-Compression-Target-Rate": str(compression_rate),
        }
        
        # Make API request
        response = self._make_request(
            method="POST",
            endpoint="/api/compress",
            data=request_data,
            headers=headers
        )
        
        return CompressionResult.from_response(response, llm_messages, input_was_string=input_was_string)
    
    def inject(
        self,
        messages: List[Union[LLMMessage, Dict[str, str]]],
        dataset_id: Optional[str] = None
    ) -> InjectResult:
        """
        Inject messages into a Weavium dataset.
        
        Args:
            messages: List of messages to inject. Must include at least one system message.
            dataset_id: Optional dataset ID. If not provided, creates dataset based on system prompt.
            
        Returns:
            InjectResult with dataset information and injection results
            
        Raises:
            ValueError: If messages are invalid
            requests.RequestException: If the API request fails
        """
        if not messages:
            raise ValueError("Messages list cannot be empty")
        
        llm_messages = []
        for msg in messages:
            if isinstance(msg, dict):
                if 'role' not in msg or 'content' not in msg:
                    raise ValueError("Each message must have 'role' and 'content' keys")
                llm_messages.append(LLMMessage(role=msg['role'], content=msg['content']))
            elif isinstance(msg, LLMMessage):
                llm_messages.append(msg)
            else:
                raise ValueError(f"Invalid message type: {type(msg)}")
        
        user_messages = [msg for msg in llm_messages if msg.role == "user"]
        system_messages = [msg for msg in llm_messages if msg.role == "system"]
        
        if not user_messages:
            raise ValueError("At least one user message is required")
        
        if not system_messages and not dataset_id:
            raise ValueError("System message is required when dataset_id is not provided")
        
        request_data = {
            "messages": [msg.to_dict() for msg in llm_messages]
        }
        
        headers = {}
        if dataset_id:
            headers["x-weavium-dataset-id"] = dataset_id
        
        # Make API request
        response = self._make_request(
            method="POST",
            endpoint="/api/inject",
            data=request_data,
            headers=headers
        )
        
        return InjectResult.from_response(response)
