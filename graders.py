from typing import Dict, Any, List, Optional
from environment.models import EmailData, Action

class TaskGrader:
    """Base grader for all tasks"""
    
    def grade(self, email: EmailData, action: Action, response: str = None, 
              conversation_history: List = None) -> tuple:
        raise NotImplementedError

class EasyTaskGrader(TaskGrader):
    """Easy: Categorize emails correctly (spam vs non-spam)"""
    
    def grade(self, email: EmailData, action: Action, response: str = None,
              conversation_history: List = None) -> tuple:
        score = 0.0
        breakdown = {}
        
        # Correct categorization
        if action.action_type == "categorize":
            category = action.parameters.get("category", "")
            
            # Determine expected category based on email content
            email_lower = f"{email.subject} {email.body}".lower()
            if "lottery" in email_lower or "viagra" in email_lower or "click here" in email_lower:
                expected_category = "spam"
            else:
                expected_category = "legitimate"
            
            if category.lower() == expected_category:
                score += 0.8
                breakdown["categorization"] = 0.8
            else:
                breakdown["categorization"] = 0.0
            
            # Bonus for marking spam appropriately
            if expected_category == "spam" and action.action_type == "mark_spam":
                score += 0.2
                breakdown["spam_handling"] = 0.2
        elif action.action_type == "mark_spam":
            # Check if it's actually spam
            email_lower = f"{email.subject} {email.body}".lower()
            if "lottery" in email_lower or "viagra" in email_lower:
                score = 1.0
                breakdown["correct_spam"] = 1.0
            else:
                score = 0.0
                breakdown["incorrect_spam"] = 0.0
        else:
            breakdown["categorization"] = 0.0
        
        return min(score, 1.0), breakdown

class MediumTaskGrader(TaskGrader):
    """Medium: Draft appropriate responses with correct sentiment"""
    
    def grade(self, email: EmailData, action: Action, response: str = None,
              conversation_history: List = None) -> tuple:
        score = 0.0
        breakdown = {}
        
        if action.action_type == "draft_response":
            if not response:
                return 0.0, {"error": "No response provided"}
            
            # Check response quality
            response_lower = response.lower()
            email_lower = f"{email.subject} {email.body}".lower()
            
            # Contains acknowledgement
            if any(word in response_lower for word in ["thank", "appreciate", "received", "sorry"]):
                score += 0.2
                breakdown["acknowledgement"] = 0.2
            
            # Addresses the issue (contains keywords from email)
            email_keywords = [word for word in email_lower.split() if len(word) > 4][:5]
            if any(keyword in response_lower for keyword in email_keywords):
                score += 0.3
                breakdown["relevance"] = 0.3
            
            # Professional tone (no caps lock, proper grammar)
            if not response.isupper() and len(response.split()) > 10:
                score += 0.2
                breakdown["professionalism"] = 0.2
            
            # Actionable next steps
            if any(word in response_lower for word in ["will", "can", "please", "let us know", "we'll", "we will"]):
                score += 0.2
                breakdown["actionable"] = 0.2
            
            # Length appropriateness
            word_count = len(response.split())
            if 20 < word_count < 200:
                score += 0.1
                breakdown["length"] = 0.1
            elif word_count >= 200:
                score += 0.05
                breakdown["length"] = 0.05
        
        elif action.action_type == "request_info":
            # Requesting info is partially correct
            score = 0.4
            breakdown["partial_progress"] = 0.4
        
        elif action.action_type == "categorize":
            # Categorization in medium task gives partial credit
            score = 0.3
            breakdown["categorized"] = 0.3
        
        return min(score, 1.0), breakdown

class HardTaskGrader(TaskGrader):
    """Hard: Complex multi-step resolution with customer satisfaction"""
    
    def grade(self, email: EmailData, action: Action, response: str = None,
              conversation_history: List = None) -> tuple:
        score = 0.0
        breakdown = {}
        
        # Step 1: Correct initial categorization
        if action.action_type == "categorize":
            category = action.parameters.get("category", "").lower()
            email_lower = f"{email.subject} {email.body}".lower()
            
            if "billing" in email_lower or "refund" in email_lower or "charge" in email_lower:
                if category == "billing":
                    score += 0.2
                    breakdown["correct_category"] = 0.2
            elif "technical" in email_lower or "error" in email_lower or "crash" in email_lower:
                if category == "technical":
                    score += 0.2
                    breakdown["correct_category"] = 0.2
            elif "contract" in email_lower or "legal" in email_lower:
                if category == "legal":
                    score += 0.2
                    breakdown["correct_category"] = 0.2
            else:
                if category == "general":
                    score += 0.1
                    breakdown["correct_category"] = 0.1
        
        # Step 2: Appropriate escalation or resolution
        if action.action_type == "escalate":
            reason = action.parameters.get("reason", "")
            if len(reason) > 20:  # Valid escalation reason
                score += 0.3
                breakdown["proper_escalation"] = 0.3
            elif len(reason) > 10:
                score += 0.15
                breakdown["proper_escalation"] = 0.15
        elif action.action_type == "draft_response":
            if response and len(response.split()) > 30:
                # Check for solution-oriented content
                response_lower = response.lower()
                if any(word in response_lower for word in ["solution", "fix", "resolve", "help", "refund", "investigate"]):
                    score += 0.3
                    breakdown["solution_oriented"] = 0.3
        
        # Step 3: Customer satisfaction simulation (based on conversation history)
        if conversation_history and len(conversation_history) > 1:
            # Check if the agent followed up appropriately
            last_actions = [h.get("action", "") for h in conversation_history[-3:]]
            if "request_info" in last_actions and "draft_response" in last_actions:
                score += 0.2
                breakdown["follow_up"] = 0.2
        
        # Step 4: Efficiency bonus (resolved in < 5 steps)
        if action.parameters.get("resolved", False):
            score += 0.3
            breakdown["resolved"] = 0.3
        
        # Bonus for combining good actions
        if score > 0.6:
            score += 0.1
            breakdown["bonus"] = 0.1
        
        return min(score, 1.0), breakdown