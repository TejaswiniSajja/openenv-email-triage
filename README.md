# Email Triage Assistant - OpenEnv Environment

## Environment Description
A realistic customer support email triage environment where an AI agent must process, categorize, and respond to customer emails. Simulates real-world customer service automation.

## Motivation
Customer support automation is a billion-dollar industry. This environment helps train and evaluate agents on:
- Email categorization
- Appropriate response drafting
- Escalation decisions
- Customer satisfaction optimization

## Action Space
- **categorize**: Assign category (spam/legitimate/billing/technical/complaint)
- **draft_response**: Write a response email
- **escalate**: Escalate to manager with reason
- **mark_spam**: Mark as spam
- **request_info**: Request more information

## Observation Space
- current_email: Full email content (sender, subject, body, urgency)
- email_queue: Number of remaining emails
- time_step: Current step in episode
- previous_actions: History of recent actions

## Tasks

### Easy (0.8+ expected)
Categorize emails correctly (spam vs legitimate). Simple binary classification.

### Medium (0.6+ expected)
Draft appropriate responses with correct sentiment and professionalism.

### Hard (0.4+ expected)
Complex multi-step resolution requiring categorization, response drafting, and escalation decisions.

## Setup

1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set OpenAI API key: `export OPENAI_API_KEY="your-key"`
4. Run inference: `python inference.py`

## Docker Build
```bash
docker build -t email-triage-env .
docker run -e OPENAI_API_KEY="your-key" email-triage-env