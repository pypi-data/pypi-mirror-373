import asyncio
import json
import sys
import os
from typing import Dict, Any, List
import logging

from cesail.dom_parser.src.dom_parser import DOMParser as BaseDOMParser
from cesail.dom_parser.src.py.types import Action as UIAction
try:
    from .llm_interface import get_llm_response
except ImportError:
    # Fallback for when running the file directly
    try:
        from llm_interface import get_llm_response
    except ImportError:
        # Add the parent directory to sys.path for imports
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from simple_agent.llm_interface import get_llm_response

logger = logging.getLogger(__name__)

class SimpleAgent:
    def __init__(self):
        self.dom_parser = None
        self.context = {
            'execution_history': [],
            'observations_history': [],
            'current_state': None,
            'current_action': None
        }
    
    async def initialize(self, url: str = None):
        """Initialize the agent with a target URL"""
        if url is None:
            url = input("Enter the URL you want to navigate to (or press Enter for default): ").strip()
            if not url:
                url = "https://www.google.com/travel/flights"
        
        self.dom_parser = BaseDOMParser()
        await self.dom_parser.__aenter__()

        action = UIAction(
                type="navigate",
                description=f"Navigate to {url}",
                confidence=1.0,
                metadata={"url": url}
        )
        
        await self.dom_parser.execute_action(action, wait_for_idle=True, translate_element_id=True)
        print(f"Initialized agent and navigated to {url}")
    
    async def execute_action(self, ui_action: Dict[str, Any]) -> tuple:
        """Execute a UI action and return results"""
        try:
            # Create UIAction object
            action = UIAction.from_json(ui_action)
            
            # Execute the action
            result = await self.dom_parser.execute_action(action, wait_for_idle=True, translate_element_id=True)
            
            # # Simulate side effects (in real implementation, this would be actual side effects)
            # side_effects = []
            
            return result
        except Exception as e:
            logger.error(f"Error executing action: {str(e)}")
            return {"error": str(e)}, []
    
    async def planner_react_loop(self, user_input: str) -> Dict[str, Any]:
        """React loop that implements think-plan-execute pattern using real LLM"""
        max_iterations = 20
        iteration = 0
        last_observation = None

        input("Press Enter to continue...")
        
        current_action = user_input
        observation_response = await self.observation_handler(None, None, current_action, "Initial start")
        last_observation = observation_response
        
        while iteration < max_iterations:
            print(f"\n--- Iteration {iteration + 1} ---")
            
            # Get current state
            parsed_dom = await self.dom_parser.analyze_page()
            site_actions = parsed_dom.actions if hasattr(parsed_dom, 'actions') else []
            
            # Find current sub-action
            current_sub_action = None
            next_sub_action = None
            current_index = -1
            
            
            # Use real LLM for react loop logic
            react_prompt = f"""
You are an agent on a webpage. Based on the previous observation, current action and sub-action, generate a UI action to execute. The observation is the result of the previous action.
It's very important that you consider the observation when generating the UI action.

Last Observation: {json.dumps(last_observation, indent=2) if last_observation else "None"}

Current Action: {current_action}
Current Sub-Action: {last_observation['next_sub_action']}

Extracted Actions:
{site_actions.to_json()}

Screenshot: Screenshot is attached. It draws bounding boxes around the actionable elements.
            The center of the bounding box has a number. The number is the element id and corresponds to the selector.

Available Actions:
{json.dumps(self.dom_parser.get_available_actions(), indent=2)}

Recent History:
{json.dumps(self.context.get('execution_history', [])[-5:], indent=2)}

Based on this information:
1. Analyze what has been done so far
2. Determine what needs to be done next
4. Identify potential challenges or risks
5. Generate a UI action to accomplish the next step

Return a JSON response with:
- reasoning: Your analysis of the situation
- ui_action: {{
      "type": "action type from site",
      "description": "why this action is needed",
      "confidence": 0.0,
      "element_id": "element identifier taken from the selector",
      "text_to_type": "text to input/select",
      "value": "value to set"
    }}

Rules for UI Action:
1. Only fill in the fields that are relevant to the action using the available actions
   required_params and optional_params are available in the available actions
2. The type must be from the Site provided above
3. The selector must be a valid CSS selector from the Site. The selector is the element id.
4. The text must be valid for the element
5. The success criteria must be verifiable
6. If a selector or what you need to do is not visible, scroll it into view (SCROLL_TO, SCROLL_DOWN_VIEWPORT, SCROLL_HALF_VIEWPORT, SCROLL_BY).
   Scroll half viewport is preferred since it's more human-friendly.

"""
            
            output_format = {
                "reasoning": "string",
                "ui_action": {
                    "type": "string",
                    "description": "string", 
                    "confidence": "number",
                    "element_id": "string",
                    "text_to_type": "string",
                    "value": "any"
                }
            }
            
            try:
                # Get screenshot for react analysis
                screenshot = await self.dom_parser.take_screenshot(
                            filepath="/tmp/screenshot4.png",
                            quality=None,
                            format="png",
                            full_page=False,
                            return_base64=True
                        )

                react_response = get_llm_response(
                    prompt=react_prompt,
                    purpose='react',
                    output_format=output_format,
                    screenshot=screenshot
                )
            

                print("PROMPT ", json.dumps(react_prompt, indent=2));
                input("Press Enter to continue...")
                print("REACT RESPONSE ", json.dumps(react_response, indent=2));
                input("Press Enter to continue...")
            except Exception as e:
                print(f"Error in LLM react loop: {e}")
                # Fallback to simple response
                react_response = {
                    'reasoning': f'Executing step: {last_observation['next_sub_action']}',
                    'ui_action': {
                        'type': 'click',
                        'description': f'Click to proceed with {last_observation['next_sub_action']}',
                        'confidence': 0.8,
                        'element_id': '1',
                        'text_to_type': '',
                        'value': None
                    }
                }
            
            print(f"Reasoning: {react_response['reasoning']}")

            ui_action = react_response['ui_action']
            
            try:
                execution_result = await self.execute_action(ui_action)

                observation_response = await self.observation_handler(
                        ui_action, execution_result, current_action, last_observation['next_sub_action']
                    )
                
                last_observation = observation_response

                self.context['execution_history'].append({
                        'action': ui_action,
                        'result': execution_result,
                        'observation': observation_response,
                        'timestamp': asyncio.get_event_loop().time()
                })

            except Exception as e:
                print(f"Error executing action: {str(e)}")
                return {
                    'status': 'error',
                    'message': f"Failed to execute action: {str(e)}",
                    'action': ui_action
                }

            iteration += 1
            
        return {
            'status': 'timeout',
            'message': f'React loop reached maximum iterations ({max_iterations})'
        }
        
    async def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """Main method to process user input through breakdown and planning"""
        print(f"\n=== Processing User Input: {user_input} ===")

        # Step 1: Expand user input into detailed task description
        print("\n1. Expanding user input into detailed task...")
        
        # Get screenshot for task expansion
        try:
            screenshot = await self.dom_parser.take_screenshot(
                filepath="/tmp/screenshot_task_expansion.png",
                quality=None,
                format="png",
                full_page=False,
                return_base64=True
            )
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            screenshot = None
        
        task_expansion_prompt = f"""
You are an AI assistant that helps expand user requests into detailed, actionable task descriptions.

User Request: {user_input}

Current webpage screenshot is attached. Based on the current page and the user's request, please expand this into a detailed task description (about 4 sentences) that:
1. Clarifies what the user wants to accomplish
2. Provides context about what needs to be done
3. Mentions any important details or requirements
4. Makes it clear for an executor to understand the goal

Keep it concise but informative. Focus on the what and why, not the how.
"""
        
        try:
            detailed_task = get_llm_response(
                prompt=task_expansion_prompt,
                purpose='general',
                screenshot=screenshot
            )
            print(f"Detailed Task: {detailed_task}")
        except Exception as e:
            print(f"Error expanding task: {e}")
            detailed_task = user_input

        # # Step 1: Breakdown
        # print("\n1. Breaking down action...")
        # breakdown = await self.breakdown_handler(user_input)
        # print(f"Breakdown complete: {breakdown['main_action']['name']}")
        # print(f"Sub-actions: {len(breakdown['sub_actions'])}")

        print(f"Detailed Task: {detailed_task}")
        input("Press Enter to continue...")
        

        # Step 2: Planning and Execution
        print("\n2. Starting react loop...")
        result = await self.planner_react_loop(detailed_task)
        
        return {
            'user_input': user_input,
            'result': result
        }
    
    async def observation_handler(self, ui_action: Dict[str, Any], execution_result: Dict[str, Any], 
                            current_action: str, current_sub_action: str) -> Dict[str, Any]:
        
        input("Start observation_handler...")

        if ui_action is None:
            ui_action = {
                'type': 'initial_start',
                'description': 'Initial start',
                'confidence': 1.0,
                'element_id': '1',
            }
        if execution_result is None:
            execution_result = {
                'success': True,
                'error': None,
                'side_effects': None,
                'data': None
            }
        if current_action is None:
            current_action = {
                'name': 'Initial start',
                'text': 'Initial start'
            }
        if current_sub_action is None:
            current_sub_action = 'Initial start'

        """Analyze the results of an executed action"""
        
        # Get the last 5 observations for context
        last_5_observations = self.context.get('observations_history', [])[-5:]
        
        observation_prompt = f"""
        Analyze the execution results and determine how we should proceed. Try to see if you can progress further with what you see. If not, you may have to scroll or click or move to a different view.

        Executed Action: {json.dumps(ui_action, indent=2)}
        Execution Result: {json.dumps(execution_result, indent=2)}

        Current Action: {current_action}
        Current Sub-Action: {current_sub_action}

        Previous Observations (Last 5):
        {json.dumps(last_5_observations, indent=2)}

        Screenshot: Screenshot after the action is executed is attached.

        Return a JSON response with:
        - success: true/false
        - observation: Analysis of the results. We want to know how to proceed. What should the executor know about the next step?
        - next_sub_action: Based on the observation, what should the next sub-action be? This should be granular enough that
          a human can do in one step based on the actions available. Make it a sentence and provide details to the executor.
        """

        output_format = {
            'success': 'bool',
            'observation': 'str',
            'next_sub_action': 'str',
        }
        
        try:
            # Get screenshot for observation analysis
            screenshot = await self.dom_parser.take_screenshot(
                            filepath="/tmp/screenshot3.png",
                            quality=None,
                            format="png",
                            full_page=False,
                            return_base64=True
                        )
            
            result = get_llm_response(
                prompt=observation_prompt,
                purpose='observation',
                output_format=output_format,
                screenshot=screenshot
            )

            print(" OBSERVATION PROMPT ", json.dumps(observation_prompt, indent=2));
            input("Press Enter to continue...")

            print("OBSERVATION RESULT ", json.dumps(result, indent=2));
            input("Press Enter to continue...")
            
            # Store the observation result in history
            self.context['observations_history'].append(result)
            
            # Keep only the last 20 observations to prevent memory bloat
            if len(self.context['observations_history']) > 20:
                self.context['observations_history'] = self.context['observations_history'][-20:]
            
            return result
        except Exception as e:
            logger.error(f"Error in observation analysis: {e}")
            # Fallback response indicating failure
            fallback_result = {
                'success': False,
                'observation': f"Error in observation analysis: {str(e)}. Action executed: {ui_action.get('type', 'unknown')}",
                'next_sub_action': 'retry or continue with caution'
            }
            
            # Store the fallback observation in history too
            self.context['observations_history'].append(fallback_result)
            
            # Keep only the last 20 observations to prevent memory bloat
            if len(self.context['observations_history']) > 20:
                self.context['observations_history'] = self.context['observations_history'][-20:]
            
            return fallback_result

    async def cleanup(self):
        """Clean up resources"""
        if self.dom_parser:
            await self.dom_parser.__aexit__(None, None, None)

async def main():
    """Main function to run the simple agent"""
    agent = SimpleAgent()
    
    try:
        # Initialize the agent
        await agent.initialize()
        
        # Interactive mode - ask user for input
        print("\n=== Simple Agent Ready ===")
        print("The agent is ready to help you with web tasks!")
        print("Type 'quit' or 'exit' to stop the agent.")
        print("=" * 50)
        
        while True:
            # Get user input
            user_input = input("\nWhat would you like me to do? (e.g., 'Find and click on the men's shoes section'): ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            # Skip empty input
            if not user_input:
                print("Please enter a task to perform.")
                continue
            
            # Process user input
            result = await agent.process_user_input(user_input)
            
            print(f"\n=== Task Result ===")
            print(json.dumps(result, indent=2))
            
            # Ask if user wants to continue
            continue_input = input("\nWould you like to perform another task? (y/n): ").strip().lower()
            if continue_input not in ['y', 'yes']:
                print("Goodbye!")
                break
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 