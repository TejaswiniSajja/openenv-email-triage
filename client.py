from openenv.core import EnvClient
from typing import Optional, Dict, Any
from models import EmailTriageAction, EmailTriageObservation


class EmailTriageEnv(EnvClient[EmailTriageAction, EmailTriageObservation]):
    """
    Client for Email Triage Environment.
    
    This client connects to the email triage environment server
    and provides methods to interact with it.
    """
    
    def __init__(self, base_url: Optional[str] = None, task: str = "easy"):
        """
        Initialize the email triage environment client.
        
        Args:
            base_url: URL of the environment server (default: http://localhost:8000)
            task: Difficulty level - "easy", "medium", or "hard"
        """
        if base_url is None:
            base_url = "http://localhost:8000"
        super().__init__(base_url)
        self.task = task
    
    async def reset(self) -> EmailTriageObservation:
        """
        Reset the environment to start a new episode.
        
        Returns:
            Initial observation
        """
        response = await self._post("/reset", params={"task": self.task})
        return EmailTriageObservation(**response.get("observation", {}))
    
    async def step(self, action: EmailTriageAction) -> Dict[str, Any]:
        """
        Take an action in the environment.
        
        Args:
            action: Action to take (contains message/response)
            
        Returns:
            Dictionary with observation, reward, done, info
        """
        response = await self._post("/step", json={"action": action.message})
        return {
            "observation": EmailTriageObservation(**response.get("observation", {})),
            "reward": response.get("reward", 0.0),
            "done": response.get("done", False),
            "info": response.get("info", {})
        }
    
    async def get_state(self) -> Dict[str, Any]:
        """
        Get the current state of the environment.
        
        Returns:
            Current state dictionary
        """
        return await self._get("/state")