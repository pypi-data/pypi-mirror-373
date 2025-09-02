import logging
import os
import json
from typing import List, Dict, Any, Optional
import anthropic
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

logger = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

class SimpleLLMInterface:
    """
    Simplified LLM interface for the simple agent.
    """
    
    def __init__(self):
        self.model = "claude-sonnet-4-20250514"
        self.temperature = 0.3
        self.max_tokens = 4000
        
        # System messages for different purposes
        self.system_messages = {
            'breakdown': """You are an AI assistant that breaks down complex UI tasks into clear, executable steps. 
                Each step should be atomic and specific enough to be executed independently.
                Include success criteria for verification.""",
                
            'react': """You are an AI agent on a webpage. Analyze the current situation and generate UI actions to execute.
                Be precise and actionable in your decisions.""",
                
            'react_loop': """You are an AI agent on a webpage. Analyze the current situation and generate UI actions to execute.
                Be precise and actionable in your decisions.""",
                
            'observation': """You are an AI assistant that analyzes the results of UI actions.
                Determine if actions were successful and what should be done next."""
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_completion(self, 
                      messages: List[Dict[str, str]], 
                      purpose: str = 'general',
                      screenshot: str = None) -> str:
        """
        Gets completion from the language model with retry logic.
        """
        try:
            # Add appropriate system message based on purpose
            if purpose in self.system_messages:
                messages.insert(0, {
                    "role": "system",
                    "content": self.system_messages[purpose]
                })
            
            # Add screenshot if provided
            if screenshot:
                # Handle different screenshot formats
                if isinstance(screenshot, str):
                    # If it's already a string, clean it up
                    screenshot_data = screenshot
                    # Remove data URL prefix if present
                    if screenshot_data.startswith('data:image/'):
                        screenshot_data = screenshot_data.split(',', 1)[1]
                    # Remove any whitespace or newlines
                    screenshot_data = screenshot_data.strip()
                else:
                    # If it's bytes, encode to base64
                    import base64
                    screenshot_data = base64.b64encode(screenshot).decode('utf-8')
                
                # Validate base64 data
                try:
                    import base64
                    # Try to decode and re-encode to ensure it's valid
                    decoded = base64.b64decode(screenshot_data)
                    screenshot_data = base64.b64encode(decoded).decode('utf-8')
                except Exception as e:
                    logger.error(f"Invalid base64 data: {e}")
                    # Skip screenshot if invalid
                    screenshot = None
                
                if screenshot:
                    messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": screenshot_data
                                }
                            }
                        ]
                    })

            # Convert messages to Anthropic format
            anthropic_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    # Anthropic doesn't support system messages in the same way
                    # We'll prepend system messages to the first user message
                    continue
                elif msg["role"] == "user":
                    content = msg["content"]
                    if isinstance(content, list):
                        # Handle multimodal content
                        anthropic_messages.append({
                            "role": "user",
                            "content": content
                        })
                    else:
                        anthropic_messages.append({
                            "role": "user",
                            "content": content
                        })
                elif msg["role"] == "assistant":
                    anthropic_messages.append({
                        "role": "assistant",
                        "content": msg["content"]
                    })

            # Add system message to the first user message if present
            system_message = None
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                    break

            # Prepare the API call parameters
            api_params = {
                "model": self.model,
                "messages": anthropic_messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            # Only add system parameter if we have a system message
            if system_message:
                api_params["system"] = system_message

            response = client.messages.create(**api_params)

            logger.info(f"LLM response: {response.content[0].text}")
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Error in LLM call: {str(e)}")
            raise

    def get_structured_completion(self, 
                                messages: List[Dict[str, str]], 
                                output_format: Dict[str, Any],
                                purpose: str = 'general',
                                screenshot: str = None) -> Dict[str, Any]:
        """
        Gets completion and parses it into a structured format.
        """
        # Add format instructions
        format_instruction = f"""
        You must return ONLY a valid JSON object with EXACTLY these fields:
        {json.dumps(output_format, indent=2)}
        
        CRITICAL RULES:
        1. Return ONLY the JSON object - no other text, no explanations
        2. The response must be a valid JSON object starting with {{ and ending with }}
        3. The response must contain ONLY the fields shown above
        4. The response must not contain any markdown formatting, no ```json``` blocks
        5. The response must match the field types exactly
        6. Do not include any text before or after the JSON object
        """
        
        messages.append({
            "role": "system",
            "content": format_instruction
        })
        
        response = self.get_completion(messages, purpose, screenshot)
        
        try:
            # Clean the response - extract JSON from markdown or text
            cleaned_response = response.strip()
            
            # Try to find JSON block in markdown format
            if "```json" in cleaned_response:
                # Extract content between ```json and ```
                start_idx = cleaned_response.find("```json") + 7
                end_idx = cleaned_response.find("```", start_idx)
                if end_idx != -1:
                    cleaned_response = cleaned_response[start_idx:end_idx].strip()
            elif "```" in cleaned_response:
                # Extract content between ``` and ```
                start_idx = cleaned_response.find("```") + 3
                end_idx = cleaned_response.find("```", start_idx)
                if end_idx != -1:
                    cleaned_response = cleaned_response[start_idx:end_idx].strip()
            else:
                # Try to find JSON object in the text
                import re
                json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
                if json_match:
                    cleaned_response = json_match.group(0)
            
            # Parse the JSON response
            parsed = json.loads(cleaned_response)
            logger.info(f"Successfully parsed JSON: {parsed}")
            
            # Validate that ONLY the required fields are present
            if set(parsed.keys()) != set(output_format.keys()):
                raise ValueError(f"Response contains unexpected fields. Expected: {list(output_format.keys())}, Got: {list(parsed.keys())}")
            
            return parsed
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed. Error: {str(e)}")
            logger.error(f"Response that failed to parse: {response}")
            raise

# Create a global instance
llm_interface = SimpleLLMInterface()

def get_llm_response(prompt: str, 
                    purpose: str = 'general', 
                    output_format: Optional[Dict[str, Any]] = None,
                    screenshot: str = None) -> Any:
    """
    Utility function for getting LLM responses.
    """
    messages = [{"role": "user", "content": prompt}]
    
    if output_format:
        return llm_interface.get_structured_completion(
            messages, output_format, purpose, screenshot
        )
    else:
        return llm_interface.get_completion(messages, purpose, screenshot)
