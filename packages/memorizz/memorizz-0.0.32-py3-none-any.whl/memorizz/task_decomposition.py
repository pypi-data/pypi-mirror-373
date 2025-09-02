from typing import List, Dict, Any, Optional, TYPE_CHECKING
import json
import logging

if TYPE_CHECKING:
    from .memagent import MemAgent

logger = logging.getLogger(__name__)

class SubTask:
    """Represents a decomposed sub-task for delegation."""
    
    def __init__(self, 
                 task_id: str,
                 description: str, 
                 assigned_agent_id: str, 
                 priority: int = 1,
                 dependencies: List[str] = None):
        self.task_id = task_id
        self.description = description
        self.assigned_agent_id = assigned_agent_id
        self.priority = priority
        self.dependencies = dependencies or []
        self.status = "pending"  # pending, in_progress, completed, failed
        self.result = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "assigned_agent_id": self.assigned_agent_id,
            "priority": self.priority,
            "dependencies": self.dependencies,
            "status": self.status,
            "result": self.result
        }

class TaskDecomposer:
    """Handles task decomposition for multi-agent coordination."""
    
    def __init__(self, root_agent: 'MemAgent'):
        self.root_agent = root_agent
        
    def analyze_delegate_capabilities(self, delegates: List['MemAgent']) -> Dict[str, Dict[str, Any]]:
        """
        Analyze the capabilities of delegate agents.
        
        Parameters:
            delegates (List[MemAgent]): List of delegate agents
            
        Returns:
            Dict[str, Dict[str, Any]]: Mapping of agent_id to capabilities
        """
        capabilities = {}
        
        for agent in delegates:
            agent_capabilities = {
                "agent_id": agent.agent_id,
                "instruction": agent.instruction,
                "persona": agent.persona.generate_system_prompt_input() if agent.persona else None,
                "tools": [],
                "application_mode": agent.application_mode.value
            }
            
            # Extract tool capabilities
            if agent.tools:
                if hasattr(agent.tools, 'list_tools'):  # Toolbox case
                    for tool in agent.tools.list_tools():
                        if "function" in tool:
                            agent_capabilities["tools"].append({
                                "name": tool["function"].get("name"),
                                "description": tool["function"].get("description")
                            })
                elif isinstance(agent.tools, list):  # List case
                    for tool in agent.tools:
                        agent_capabilities["tools"].append({
                            "name": tool.get("name"),
                            "description": tool.get("description")
                        })
            
            capabilities[agent.agent_id] = agent_capabilities
            
        return capabilities
    
    def decompose_task(self, 
                      user_query: str, 
                      delegates: List['MemAgent']) -> List[SubTask]:
        """
        Decompose a complex task into sub-tasks aligned with delegate capabilities.
        
        Parameters:
            user_query (str): The original user query/task
            delegates (List[MemAgent]): List of available delegate agents
            
        Returns:
            List[SubTask]: List of decomposed sub-tasks
        """
        try:
            logger.info(f"Starting task decomposition for query: {user_query}")
            logger.info(f"Number of delegates: {len(delegates)}")
            
            # Analyze delegate capabilities
            logger.info("Analyzing delegate capabilities...")
            capabilities = self.analyze_delegate_capabilities(delegates)
            logger.info(f"Analyzed capabilities for {len(capabilities)} agents")
            
            # Create decomposition prompt
            logger.info("Creating decomposition prompt...")
            decomposition_prompt = self._create_decomposition_prompt(user_query, capabilities)
            
            # Use the root agent's model to decompose the task
            messages = [
                {"role": "system", "content": decomposition_prompt},
                {"role": "user", "content": f"Please decompose this task: {user_query}"}
            ]
            
            logger.info("Calling LLM for task decomposition...")
            response = self.root_agent.model.client.responses.create(
                model="gpt-4.1",
                input=messages
            )
            
            logger.info(f"LLM response received: {response.output_text[:200]}..." if response.output_text else "No response text")
            
            # Parse the response to extract sub-tasks
            logger.info("Parsing decomposition response...")
            sub_tasks = self._parse_decomposition_response(response.output_text, capabilities)
            logger.info(f"Successfully parsed {len(sub_tasks)} sub-tasks")
            
            return sub_tasks
            
        except Exception as e:
            logger.error(f"Error decomposing task: {e}", exc_info=True)
            return []
    
    def _create_decomposition_prompt(self, 
                                   user_query: str, 
                                   capabilities: Dict[str, Dict[str, Any]]) -> str:
        """Create the system prompt for task decomposition."""
        
        prompt = """You are a task decomposition specialist for a multi-agent system. Your job is to analyze a complex user query and break it down into specific sub-tasks that can be assigned to different specialized agents.

AVAILABLE AGENTS AND THEIR CAPABILITIES:
"""
        
        for agent_id, caps in capabilities.items():
            prompt += f"\nAgent ID: {agent_id}\n"
            prompt += f"Specialization: {caps.get('instruction', 'General assistant')}\n"
            if caps.get('persona'):
                prompt += f"Persona: {caps['persona'][:200]}...\n"
            
            if caps.get('tools'):
                prompt += "Available Tools:\n"
                for tool in caps['tools']:
                    prompt += f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}\n"
            prompt += "\n"
        
        prompt += """
DECOMPOSITION RULES:
1. Break down the user query into specific, actionable sub-tasks
2. Assign each sub-task to the most appropriate agent based on their capabilities
3. Consider task dependencies and execution order
4. Each sub-task should be independent or have clear dependencies
5. Prioritize tasks (1=highest, 5=lowest)

RESPONSE FORMAT:
Respond with a JSON array of sub-tasks in this exact format:
[
    {
        "task_id": "task_1",
        "description": "Specific task description",
        "assigned_agent_id": "agent_id",
        "priority": 1,
        "dependencies": []
    }
]

Only respond with the JSON array, no additional text.
"""
        
        return prompt
    
    def _parse_decomposition_response(self, 
                                    response_text: str, 
                                    capabilities: Dict[str, Dict[str, Any]]) -> List[SubTask]:
        """Parse the decomposition response and create SubTask objects."""
        try:
            # Extract JSON from response
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            task_data = json.loads(response_text)
            
            sub_tasks = []
            for task in task_data:
                # Validate that assigned agent exists
                if task.get("assigned_agent_id") in capabilities:
                    sub_task = SubTask(
                        task_id=task.get("task_id"),
                        description=task.get("description"),
                        assigned_agent_id=task.get("assigned_agent_id"),
                        priority=task.get("priority", 1),
                        dependencies=task.get("dependencies", [])
                    )
                    sub_tasks.append(sub_task)
                else:
                    logger.warning(f"Invalid agent assignment in task: {task}")
            
            return sub_tasks
            
        except Exception as e:
            logger.error(f"Error parsing decomposition response: {e}")
            return []
    
    def create_consolidation_prompt(self, 
                                  original_query: str, 
                                  sub_task_results: List[Dict[str, Any]]) -> str:
        """Create a prompt for consolidating sub-task results."""
        
        prompt = f"""You are a result consolidation specialist. Your job is to take the results from multiple specialized agents and create a comprehensive, coherent response to the original user query.

ORIGINAL USER QUERY: {original_query}

SUB-TASK RESULTS:
"""
        
        for result in sub_task_results:
            prompt += f"\nTask: {result.get('description', 'Unknown task')}\n"
            prompt += f"Agent: {result.get('assigned_agent_id', 'Unknown agent')}\n"
            prompt += f"Status: {result.get('status', 'Unknown status')}\n"
            prompt += f"Result: {result.get('result', 'No result')}\n"
            prompt += "---\n"
        
        prompt += """
CONSOLIDATION INSTRUCTIONS:
1. Synthesize all sub-task results into a coherent response
2. Address the original user query comprehensively
3. Identify any gaps or missing information
4. If there are conflicting results, highlight them
5. Provide a clear, helpful final answer

If the objective is not fully met, specify what additional steps are needed.
"""
        
        return prompt 