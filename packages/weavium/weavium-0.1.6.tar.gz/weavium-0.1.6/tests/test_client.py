import pytest
import vcr
from weavium.client import WeaviumClient, LLMMessage, CompressionResult


# Configure VCR to filter sensitive information
test_vcr = vcr.VCR(
    serializer='yaml',
    cassette_library_dir='tests/cassettes',
    record_mode='once',
    match_on=['method', 'scheme', 'host', 'port', 'path', 'query'],
    filter_headers=['x-weavium-api-key'],
)


@pytest.fixture
def client():
    """Create a WeaviumClient instance for testing"""
    return WeaviumClient(
        api_key="sk-wvm-rKppaf3rIubV8YpcnI5NlQRVAfWniGqW59TsivnmfpTdAtV_b1Z7lv2EEBGkHVi5NFbiJngQufM6UdDs1wHsZg",
        base_url="https://api.weavium.ai"
    )
    # return WeaviumClient(
    #     api_key="sk-wvm-XtmvgltzRgpeAHO7V0pH6CaIP2jD7-ey9MMpJBpa_Th-r5WU08WJe8aQr4zjVvqnMF51Y06WwJsTgCp7VPZ2Jw",
    #     base_url="http://localhost:8005"
    # )


# @test_vcr.use_cassette('compress_string_input.yaml')
def test_compress_string_input(client):
    """Test compressing a string input without system prompt"""
    result = client.compress(
        input="This is a test message to compress using Weavium API",
        compression_rate=0.3
    )
    
    # Verify result format for string input
    assert isinstance(result, CompressionResult)
    assert isinstance(result.result, str)
    assert result.result is not None
    assert len(result.result) > 0
    
    # Verify compression metadata
    assert result.compression_rate is not None
    assert result.original_tokens > 0
    assert result.compressed_tokens > 0


@test_vcr.use_cassette('compress_string_with_system_prompt.yaml')
def test_compress_string_input_with_system_prompt(client):
    """Test compressing a string input with system prompt"""
    result = client.compress(
        input="Explain quantum physics in simple terms",
        system_prompt="You are a physics teacher",
        compression_rate=0.2
    )
    
    # Verify result format for string input
    assert isinstance(result, CompressionResult)
    assert isinstance(result.result, str)
    assert result.result is not None
    assert len(result.result) > 0
    
    # Verify compression metadata
    assert result.compression_rate is not None
    assert result.original_tokens > 0
    assert result.compressed_tokens > 0


@test_vcr.use_cassette('compress_list_input.yaml')
def test_compress_list_input(client):
    """Test compressing a list of messages"""
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant"},
        {"role": "user", "content": "What is machine learning and how does it work?"}
    ]
    
    result = client.compress(
        input=messages,
        compression_rate=0.4
    )
    
    # Verify result format for list input
    assert isinstance(result, CompressionResult)
    assert isinstance(result.result, list)
    assert len(result.result) >= 1
    assert all(isinstance(msg, LLMMessage) for msg in result.result)
    
    # Verify compression metadata
    assert result.compression_rate is not None
    assert result.original_tokens > 0
    assert result.compressed_tokens > 0
    
    # Verify message structure
    user_messages = [msg for msg in result.result if msg.role == "user"]
    assert len(user_messages) >= 1