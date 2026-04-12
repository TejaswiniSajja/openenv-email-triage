from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from parent directory
from my_env_v4 import MyEnvV4Env, MyEnvV4Action

# This MUST be named 'app' for openenv.yaml
app = FastAPI(title="Email Triage Environment")

# Store environment instances
environments: Dict[str, MyEnvV4Env] = {}

class ResetRequest(BaseModel):
    task: Optional[str] = "easy"

class StepRequest(BaseModel):
    action: str

@app.get("/")
def home():
    return {"message": "Email Triage Environment Server", "status": "running"}

@app.post("/reset")
async def reset_environment(request: ResetRequest = None):
    """Reset the environment"""
    task = request.task if request else "easy"
    env_id = f"env_{task}"
    
    env = MyEnvV4Env(task=task)
    result = env.reset()
    environments[env_id] = env
    
    return {
        "observation": result.observation.dict(),
        "info": result.info
    }

@app.post("/step")
async def step_environment(request: StepRequest, env_id: str = "env_easy"):
    """Take a step in the environment"""
    if env_id not in environments:
        raise HTTPException(status_code=404, detail="Environment not found. Call /reset first.")
    
    env = environments[env_id]
    action = MyEnvV4Action(message=request.action)
    result = await env.step(action)
    
    return {
        "observation": result.observation.dict(),
        "reward": result.reward,
        "done": result.done,
        "info": result.info
    }

@app.get("/state")
async def get_state(env_id: str = "env_easy"):
    """Get current state"""
    if env_id not in environments:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    env = environments[env_id]
    obs = env._get_observation()
    
    return {
        "observation": obs.dict(),
        "time_step": env.time_step,
        "total_reward": env.total_reward,
        "emails_processed": env.current_email_index,
        "queue_size": len(env.email_queue)
    }

# This is for local running
def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()