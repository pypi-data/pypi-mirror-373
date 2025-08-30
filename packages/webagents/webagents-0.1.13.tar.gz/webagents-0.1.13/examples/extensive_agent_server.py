#!/usr/bin/env python3
"""
Extensive Agent Server Demo - Full Featured Example

This example demonstrates a more complete setup with multiple agents,
including a custom @app.agent decorated agent and configurable payments.
"""

import argparse
import os
import time
import httpx
import uvicorn
from webagents.server import RobutlerServer, pricing
from webagents.agent.agent import RobutlerAgent
from agents import function_tool


# Calculator Tools
@function_tool
@pricing(credits_per_call=2000)
async def calculate(expression: str) -> str:
    """Safely calculate a mathematical expression."""
    try:
        # Simple safe evaluation for basic math
        allowed_chars = set('0123456789+-*/().')
        if all(c in allowed_chars or c.isspace() for c in expression):
            result = eval(expression)
            return f"{expression} = {result}"
        else:
            return "Error: Only basic math operations are allowed"
    except Exception as e:
        return f"Error: {str(e)}"


# Image Generation Tools
@function_tool
@pricing(credits_per_call=10000)
async def generate_image(prompt: str, width: int = 1024, height: int = 1024, model: str = "Qubico/flux1-schnell") -> str:
    """Generate an image using PiAPI Flux API. Uses Qubico/flux1-schnell by default.
    
    Args:
        prompt: Text description of the image to generate
        width: Image width (default 1024, width*height cannot exceed 1048576)
        height: Image height (default 1024, width*height cannot exceed 1048576)
        model: Model to use (Qubico/flux1-dev, Qubico/flux1-schnell, or Qubico/flux1-dev-advanced)
    
    Returns:
        URL of the generated image or error message
    """
    print(f"\n🎨 Starting image generation...")
    print(f"  📝 Prompt: {prompt}")
    print(f"  📐 Dimensions: {width}x{height}")
    print(f"  🤖 Model: {model}")
    
    try:
        # Check if API key is available
        api_key = os.getenv("PIAPI_API_KEY")
        if not api_key:
            print("  ❌ Error: PIAPI_API_KEY environment variable not set")
            return "Error: PIAPI_API_KEY environment variable not set"
        
        print("  ✅ API key found")
        
        # Validate dimensions
        if width * height > 1048576:
            print(f"  ❌ Error: Dimensions too large ({width}x{height} = {width*height} > 1048576)")
            return "Error: width*height cannot exceed 1048576"
        
        print("  ✅ Dimensions validated")
        
        # Prepare the request
        url = "https://api.piapi.ai/api/v1/task"
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key
        }
        
        payload = {
            "model": model,
            "task_type": "txt2img",
            "input": {
                "prompt": prompt,
                "width": width,
                "height": height
            }
        }
        
        print("  📤 Submitting task to PiAPI...")
        
        # Submit the task
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("code") != 200:
                error_msg = f"Error: API returned code {result.get('code')}, message: {result.get('message')}"
                print(f"  ❌ {error_msg}")
                return error_msg
            
            data = result.get("data", {})
            task_id = data.get("task_id")
            
            if not task_id:
                print("  ❌ Error: No task ID returned from API")
                return "Error: No task ID returned from API"
            
            print(f"  ✅ Task submitted successfully! Task ID: {task_id}")
            
            # Poll for completion
            max_attempts = 60  # Maximum 5 minutes (60 * 5 seconds)
            attempt = 0
            
            print("  ⏳ Polling for completion...")
            
            while attempt < max_attempts:
                attempt += 1
                print(f"  🔄 Attempt {attempt}/{max_attempts} - Checking status...")
                
                # Check task status
                status_url = f"https://api.piapi.ai/api/v1/task/{task_id}"
                status_response = await client.get(status_url, headers=headers)
                status_response.raise_for_status()
                
                status_result = status_response.json()
                
                if status_result.get("code") != 200:
                    error_msg = f"Error checking status: API returned code {status_result.get('code')}, message: {status_result.get('message')}"
                    print(f"  ❌ {error_msg}")
                    return error_msg
                
                status_data = status_result.get("data", {})
                status = status_data.get("status")
                
                print(f"    📊 Status: {status}")
                
                if status == "Completed" or status == "completed":
                    print("  🎉 Image generation completed!")
                    output = status_data.get("output", {})
                    image_url = output.get("image_url")
                    if image_url:
                        print(f"  🖼️ Image URL: {image_url}")
                        return f"Image generated successfully: {image_url} \n If you can render images using the image_url, do it. If not show the image_url as markdown link and invite the user to click it."
                    else:
                        print("  ❌ Error: No image URL in completed response")
                        return "Error: No image URL in completed response"
                elif status == "Failed" or status == "failed":
                    error_info = status_data.get("error", {})
                    error_message = error_info.get("message", "Unknown error")
                    error_msg = f"Error: Image generation failed - {error_message}"
                    print(f"  ❌ {error_msg}")
                    return error_msg
                elif status in ["Processing", "Pending", "processing", "pending"]:
                    # Still processing, wait and try again
                    print(f"    ⏱️ Still {status.lower()}... waiting 5 seconds")
                    import asyncio
                    await asyncio.sleep(5)  # Wait 5 seconds before next check
                else:
                    error_msg = f"Error: Unknown status '{status}'"
                    print(f"  ❌ {error_msg}")
                    return error_msg
            
            timeout_msg = f"Error: Image generation timed out after {max_attempts * 5} seconds. Task ID: {task_id}"
            print(f"  ⏰ {timeout_msg}")
            return timeout_msg
            
    except httpx.exceptions.RequestException as e:
        error_msg = f"Error making request to PiAPI: {str(e)}"
        print(f"  ❌ {error_msg}")
        return error_msg
    except Exception as e:
        error_msg = f"Error generating image: {str(e)}"
        print(f"  ❌ {error_msg}")
        return error_msg


# Create RobutlerAgent instances
Calculator = RobutlerAgent(
    name="calculator", 
    instructions="You are a math assistant. You can perform calculations and solve mathematical problems.",
    credits_per_token=8,
    tools=[calculate],
    model="gpt-4o-mini"
)

ImageGenerator = RobutlerAgent(
    name="image-generator",
    instructions="You are an AI image generation assistant. You can create images from text descriptions using advanced AI models. When users request images, use the generate_image tool with detailed, creative prompts. When answering with an image link, make sure to tell to show the image to the user in the chat or UI.",
    credits_per_token=7,
    tools=[generate_image],
    model="gpt-4o-mini",
    intents=["generates images based on a text prompt using the flux model"]
)


def create_server(enable_payments: bool = True):
    """Create the RobutlerServer with configurable payment settings."""
    
    # Create server with agents
    if enable_payments:
        app = RobutlerServer(agents=[Calculator, ImageGenerator], min_balance=5000, root_path="/agents")
    else:
        app = RobutlerServer(agents=[Calculator, ImageGenerator], min_balance=0, root_path="/agents")
        # Disable payment callbacks for demo purposes
        app.before_request_callbacks = []
    
    # Add custom agent using @app.agent decorator
    @app.agent("/robutler", intents=["provide help with robutler agents and the robutler platform"])
    @pricing(credits_per_token=10)
    async def robutler(request):
        """Robutler - Your comprehensive AI assistant that can help with various tasks."""
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI()
        
        try:
            # Call OpenAI API
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=request.messages,
                stream=request.stream if hasattr(request, 'stream') else False
            )
            
            if request.stream if hasattr(request, 'stream') else False:
                # Handle streaming response
                async def generate():
                    async for chunk in response:
                        if chunk.choices and chunk.choices[0].delta.content:
                            yield f"data: {chunk.model_dump_json()}\n\n"
                    yield "data: [DONE]\n\n"
                
                from fastapi.responses import StreamingResponse
                return StreamingResponse(generate(), media_type="text/plain")
            else:
                # Handle non-streaming response
                return response.model_dump()
                
        except Exception as e:
            return {
                "error": {
                    "message": f"Error calling OpenAI API: {str(e)}",
                    "type": "api_error"
                }
            }
    
    # Add logging to see usage
    @app.finalize_request
    def log_usage(request, response, context):
        """Log usage for all requests."""
        usage = context.get_usage()
        endpoint = request.url.path
        
        print(f"\n📊 Usage Report for {endpoint}:")
        print(f"  💰 Total Credits: {usage['total_credits']}")
        print(f"  🔤 Total Tokens: {usage['total_tokens']}")
        
        if usage['tool_usage']:
            print(f"  🔧 Tool Usage:")
            for tool_record in usage['tool_usage']:
                print(f"    - {tool_record['source']}: {tool_record['credits']} credits")
        
        if usage['server_usage']:
            print(f"  🤖 Agent Usage:")
            for server_record in usage['server_usage']:
                print(f"    - {server_record['source']}: {server_record['credits']} credits")
    
    return app


def main():
    parser = argparse.ArgumentParser(description="Extensive Agent Server Demo")
    parser.add_argument(
        "--no-payments", 
        action="store_true", 
        help="Disable payment system for demo/testing purposes"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=2225, 
        help="Port to run the server on (default: 2224)"
    )
    
    args = parser.parse_args()
    
    # Create server with payment settings
    enable_payments = not args.no_payments
    app = create_server(enable_payments=enable_payments)
    
    print("🚀 Extensive Agent Server Demo")
    print(f"💰 Payments: {'ENABLED' if enable_payments else 'DISABLED'}")
    
    print("\n✨ Available endpoints:")
    print("  POST /agents/calculator/chat/completions     - Math assistant (8 credits/token)")
    print("  GET  /agents/calculator                      - Calculator info")
    print("  POST /agents/image-generator/chat/completions - Image generation assistant (7 credits/token)")
    print("  GET  /agents/image-generator                 - Image generator info")
    print("  POST /agents/robutler/chat/completions       - Robutler general assistant (10 credits/token)")
    print("  GET  /agents/robutler                        - Robutler info")
    
    print("\n💡 Example requests:")
    print("  # Calculate math")
    print(f"  curl -X POST http://localhost:{args.port}/agents/calculator/chat/completions \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"model\": \"gpt-4o-mini\", \"messages\": [{\"role\": \"user\", \"content\": \"What is 15 * 23?\"}]}'")
    
    print("\n  # Generate image")
    print(f"  curl -X POST http://localhost:{args.port}/agents/image-generator/chat/completions \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"model\": \"gpt-4o-mini\", \"messages\": [{\"role\": \"user\", \"content\": \"Generate an image of a cute cat sitting in a garden\"}]}'")
    
    print("\n  # Ask Robutler")
    print(f"  curl -X POST http://localhost:{args.port}/agents/robutler/chat/completions \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"model\": \"gpt-4o-mini\", \"messages\": [{\"role\": \"user\", \"content\": \"Tell me about artificial intelligence\"}]}'")
    
    print(f"\n🌐 Starting server on http://localhost:{args.port}")
    if enable_payments:
        print("💳 Minimum balance required: 5000 credits")
    
    # Only show warnings for missing environment variables
    if not os.getenv("PIAPI_API_KEY"):
        print("⚠️  Note: Set PIAPI_API_KEY environment variable for image generation to work")
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Note: Set OPENAI_API_KEY environment variable for Robutler agent to work")
    
    if not enable_payments:
        print("\n🔓 Running without payment system - perfect for testing!")
    
    uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main() 