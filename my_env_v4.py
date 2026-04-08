# my_env_v4.py - Updated with varied decimal rewards
import random
import asyncio
from typing import Tuple, Dict, Any, Optional
from dataclasses import dataclass
from pydantic import BaseModel
import math

# ============ Models ============
class MyEnvV4Action(BaseModel):
    message: str

class EmailData(BaseModel):
    email_id: str
    sender: str
    subject: str
    body: str
    urgency: str
    category: Optional[str] = None

class MyEnvV4Observation(BaseModel):
    echoed_message: str
    current_email: Optional[EmailData] = None
    email_queue: int = 0
    time_step: int = 0
    last_reward: float = 0.0
    task: str = "easy"

class MyEnvV4StepResult(BaseModel):
    observation: MyEnvV4Observation
    reward: float
    done: bool
    info: Dict[str, Any] = {}

# ============ Environment ============
class MyEnvV4Env:
    
    EMAIL_TEMPLATES = {
        "easy": [
            {"id": "1", "sender": "lottery@winner.com", "subject": "YOU WIN $1,000,000!", "body": "Congratulations! You have won our lottery! Click here to claim.", "urgency": "low"},
            {"id": "2", "sender": "viagra@pharmacy.com", "subject": "Special offer", "body": "Get VIAGRA at discount prices!", "urgency": "low"},
            {"id": "3", "sender": "customer@example.com", "subject": "Product inquiry", "body": "I'm interested in your product. Can you send me pricing?", "urgency": "medium"},
            {"id": "4", "sender": "support@company.com", "subject": "Account question", "body": "How do I reset my password?", "urgency": "medium"},
        ],
        "medium": [
            {"id": "5", "sender": "angry@customer.com", "subject": "TERRIBLE SERVICE", "body": "I've been waiting for 3 days! This is completely unacceptable!", "urgency": "high"},
            {"id": "6", "sender": "confused@user.com", "subject": "Need help", "body": "I can't figure out how to use your product. The manual is confusing.", "urgency": "medium"},
            {"id": "7", "sender": "happy@customer.com", "subject": "Great service!", "body": "Just wanted to say thanks to your support team. They were very helpful!", "urgency": "low"},
        ],
        "hard": [
            {"id": "8", "sender": "billing@company.com", "subject": "URGENT: Incorrect charge", "body": "I was charged twice for last month's subscription ($99.99 each). Need refund ASAP. Order #12345.", "urgency": "high"},
            {"id": "9", "sender": "technical@client.com", "subject": "Critical system error", "body": "After the latest update, our production system crashes every hour. This is causing major losses.", "urgency": "high"},
            {"id": "10", "sender": "legal@partner.com", "subject": "Contract renewal", "body": "We need to discuss the Q2 contract renewal. Several clauses need revision.", "urgency": "medium"},
        ]
    }
    
    def __init__(self, task: str = "easy"):
        self.task = task
        self.current_email_index = 0
        self.email_queue = []
        self.time_step = 0
        self.total_reward = 0.0
        self.conversation_history = []
        self.reset()
    
    @classmethod
    async def from_docker_image(cls, image_name: str = None):
        task = "easy"
        if image_name:
            if "medium" in image_name:
                task = "medium"
            elif "hard" in image_name:
                task = "hard"
        return cls(task=task)
    
    def reset(self) -> MyEnvV4StepResult:
        self.time_step = 0
        self.total_reward = 0.0
        self.conversation_history = []
        
        if self.task in self.EMAIL_TEMPLATES:
            self.email_queue = self.EMAIL_TEMPLATES[self.task].copy()
        else:
            self.email_queue = self.EMAIL_TEMPLATES["easy"].copy()
        
        random.shuffle(self.email_queue)
        self.current_email_index = 0
        
        return MyEnvV4StepResult(
            observation=self._get_observation(),
            reward=0.0,
            done=False,
            info={"task": self.task, "step": 0}
        )
    
    async def step(self, action: MyEnvV4Action) -> MyEnvV4StepResult:
        reward = self._grade_action(action.message)
        self.total_reward += reward
        
        self.current_email_index += 1
        self.time_step += 1
        
        done = self.current_email_index >= len(self.email_queue) or self.time_step >= 50
        
        self.conversation_history.append({
            "step": self.time_step,
            "action": action.message,
            "reward": reward
        })
        
        return MyEnvV4StepResult(
            observation=self._get_observation(),
            reward=reward,
            done=done,
            info={
                "task": self.task,
                "step": self.time_step,
                "total_reward": self.total_reward,
                "emails_processed": self.current_email_index
            }
        )
    
    def _get_observation(self) -> MyEnvV4Observation:
        if self.current_email_index < len(self.email_queue):
            current_email = self.email_queue[self.current_email_index]
            email_obj = EmailData(
                email_id=current_email["id"],
                sender=current_email["sender"],
                subject=current_email["subject"],
                body=current_email["body"],
                urgency=current_email["urgency"]
            )
            echoed_message = f"Email {self.current_email_index + 1}: {email_obj.subject[:50]}"
        else:
            email_obj = None
            echoed_message = "No more emails"
        
        return MyEnvV4Observation(
            echoed_message=echoed_message,
            current_email=email_obj,
            email_queue=len(self.email_queue) - self.current_email_index,
            time_step=self.time_step,
            last_reward=self.total_reward,
            task=self.task
        )
    
    def _grade_action(self, message: str) -> float:
        """Returns varied decimal rewards (not just .0, .5, .8, etc.)"""
        
        if self.current_email_index >= len(self.email_queue):
            return 0.0
        
        current_email = self.email_queue[self.current_email_index]
        email_text = f"{current_email['subject']} {current_email['body']}".lower()
        message_lower = message.lower()
        
        # EASY TASK - Spam detection with varied scores
        if self.task == "easy":
            spam_keywords = ["lottery", "viagra", "click", "winner", "prize", "discount"]
            spam_count = sum(1 for word in spam_keywords if word in email_text)
            is_spam = spam_count >= 1
            
            if is_spam:
                if "spam" in message_lower or "mark" in message_lower:
                    # Perfect spam detection: 0.95-1.0 range
                    return 0.95 + (spam_count * 0.0125)  # Can be 0.9625, 0.975, etc.
                elif "legitimate" in message_lower:
                    return 0.15 + (random.random() * 0.1)  # 0.15-0.25
                else:
                    return 0.05 + (random.random() * 0.1)  # 0.05-0.15
            else:
                if "legitimate" in message_lower:
                    # Perfect legitimate detection: 0.85-0.95 range
                    return 0.85 + (random.random() * 0.1)
                elif "spam" in message_lower:
                    return 0.10 + (random.random() * 0.1)
                else:
                    return 0.30 + (random.random() * 0.15)
        
        # MEDIUM TASK - Response quality with fine-grained scoring
        elif self.task == "medium":
            # Check response quality metrics
            score = 0.0
            word_count = len(message.split())
            
            # Length score (optimal is 20-50 words)
            if 20 <= word_count <= 50:
                score += 0.35
            elif 10 <= word_count <= 100:
                score += 0.20 + (random.random() * 0.1)
            else:
                score += 0.05 + (random.random() * 0.1)
            
            # Professional tone
            professional_words = ["apologize", "sorry", "thank", "appreciate", "understand", "help", "resolve"]
            professional_count = sum(1 for word in professional_words if word in message_lower)
            score += min(0.35, professional_count * 0.07)
            
            # Actionable content
            action_words = ["will", "can", "please", "let", "investigate", "process", "refund", "escalate"]
            action_count = sum(1 for word in action_words if word in message_lower)
            score += min(0.30, action_count * 0.06)
            
            # Specific to complaint handling
            if "waiting" in email_text or "unacceptable" in email_text:
                if any(word in message_lower for word in ["apologize", "sorry"]):
                    score += 0.15
                if any(word in message_lower for word in ["immediately", "asap", "urgent"]):
                    score += 0.10
            
            # Specific to thank you emails
            elif "thank" in email_text:
                if any(word in message_lower for word in ["welcome", "glad", "happy", "pleasure"]):
                    score += 0.20
            
            return min(0.95, score + (random.random() * 0.05))
        
        # HARD TASK - Complex resolution with very fine-grained scoring
        else:
            score = 0.0
            step_num = len(self.conversation_history)
            
            # Step 1: Categorization (first interaction)
            if step_num == 0:
                if "billing" in email_text or "refund" in email_text:
                    if "billing" in message_lower:
                        score = 0.3125  # Specific decimal
                    elif "refund" in message_lower:
                        score = 0.4375
                    else:
                        score = 0.125
                elif "error" in email_text or "crash" in email_text:
                    if "technical" in message_lower:
                        score = 0.375
                    elif "error" in message_lower:
                        score = 0.3125
                    else:
                        score = 0.1875
                else:
                    score = 0.25
            
            # Step 2: Resolution action
            elif step_num == 1:
                if "billing" in email_text:
                    if "refund" in message_lower or "process" in message_lower:
                        score = 0.6875
                    elif "escalate" in message_lower:
                        score = 0.5625
                    else:
                        score = 0.375
                elif "error" in email_text:
                    if "fix" in message_lower or "resolve" in message_lower:
                        score = 0.625
                    elif "escalate" in message_lower:
                        score = 0.75
                    else:
                        score = 0.4375
                else:
                    score = 0.5
            
            # Step 3: Follow-up / Resolution
            else:
                if "resolved" in message_lower or "complete" in message_lower:
                    score = 0.9375
                elif "follow" in message_lower or "update" in message_lower:
                    score = 0.8125
                elif "investigate" in message_lower:
                    score = 0.6875
                else:
                    score = 0.5625
            
            # Add tiny random variation (0.001 to 0.009)
            score += random.randint(1, 9) / 1000
            
            return min(0.999, score)
    
    async def close(self):
        pass