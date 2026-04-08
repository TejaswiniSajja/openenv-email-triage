from openenv.core import EnvClient
from models import EmailTriageAction, EmailTriageObservation

class EmailTriageEnv(EnvClient[EmailTriageAction, EmailTriageObservation]):
    def __init__(self, base_url: str = None, task: str = "easy"):
        super().__init__(base_url)
        self.task = task
    
    async def reset(self):
        return await super().reset(params={"task": self.task})