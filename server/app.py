from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import sys
import os



# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.my_env_v4 import MyEnvV4Env, MyEnvV4Action

app = FastAPI(title="OpenEnv Email Triage")

env_instance = None

class StepRequest(BaseModel):
    action: str

@app.get("/")
def root():
    return {
        "name": "Email Triage Environment",
        "status": "running",
        "tasks": ["easy", "medium", "hard"]
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/reset")
def reset(task: str = "easy"):
    global env_instance
    env_instance = MyEnvV4Env(task=task)
    env_instance.reset()
    return {"status": "reset", "task": task}

@app.post("/step")
async def step(request: StepRequest):
    global env_instance
    if env_instance is None:
        return {"error": "Call /reset first", "reward": 0.0, "done": True}
    
    result = await env_instance.step(MyEnvV4Action(message=request.action))
    return {
        "reward": result.reward,
        "done": result.done,
        "observation": {
            "echoed_message": result.observation.echoed_message,
            "task": result.observation.task,
            "email_queue": result.observation.email_queue
        }
    }

@app.get("/state")
def state():
    global env_instance
    if env_instance is None:
        return {"status": "not_initialized"}
    return env_instance.state()

# ✅ FIX 1: Added main() function
def main():
    """Main entry point for the server"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# ✅ FIX 2: Added if __name__ == "__main__" block
if __name__ == "__main__":
    main()
