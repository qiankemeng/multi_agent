"""
Debug test to check what the API is actually returning
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import MLLMClient, MLLMClientConfig
from experiments import MLLMRequest, AnalysisTask, Frame

def test_api_response():
    """Check what the API returns"""
    print("\n" + "="*60)
    print("API Response Debug Test")
    print("="*60)

    # Check if frame exists
    frames_dir = Path("data/temp/frames")
    if not frames_dir.exists():
        print("✗ No frames directory")
        return

    frame_files = list(frames_dir.glob("*.jpg"))
    if not frame_files:
        print("✗ No frame files")
        return

    # Create client
    client = MLLMClient(MLLMClientConfig(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        default_model=os.getenv("OPENAI_DEFAULT_MODEL", "gpt-5")
    ))

    # Test 1: Simple text question
    print("\n--- Test 1: Simple text ---")
    request1 = MLLMRequest(
        request_id="debug_1",
        model_name=os.getenv("OPENAI_DEFAULT_MODEL", "gpt-5"),
        api_endpoint=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        prompt="What is 2+2? Answer with just the number.",
        temperature=0.0,
        max_tokens=50,
        task=AnalysisTask.OTHER
    )

    response1 = client.call(request1)
    print(f"Success: {response1.success}")
    print(f"Text: '{response1.text}'")
    print(f"Text length: {len(response1.text)}")
    print(f"Text repr: {repr(response1.text)}")
    print(f"Tokens: {response1.total_tokens}")

    # Test 2: Image with question
    print("\n--- Test 2: Image with question ---")
    test_frame = frame_files[0]
    request2 = MLLMRequest(
        request_id="debug_2",
        model_name=os.getenv("OPENAI_DEFAULT_MODEL", "gpt-5"),
        api_endpoint=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        prompt="What do you see in this image? Describe it in one sentence.",
        images=[str(test_frame)],
        temperature=0.7,
        max_tokens=100,
        task=AnalysisTask.CAPTION
    )

    response2 = client.call(request2)
    print(f"Success: {response2.success}")
    print(f"Text: '{response2.text}'")
    print(f"Text length: {len(response2.text)}")
    print(f"Text repr: {repr(response2.text)}")
    print(f"Tokens: {response2.total_tokens}")

    # Check response structure
    print("\n--- Response object inspection ---")
    print(f"Response type: {type(response2)}")
    print(f"Response attributes: {vars(response2)}")

if __name__ == "__main__":
    test_api_response()
