# TinyApprover for LLM
### Mitigate LLM Agent risk with human-in-the-loop (HITL) orchestration.

## Background
Many organizations are exploring deploying agentic LLM applications, which take actions based on inputs. Depending on the privileged nature of these actions, they may be considered risky.

TinyApprover can be used for a guardrail for any type of automatic action your LLM app wants to take by requiring explicit approval first in your incident response platform.

## Requirements
- TinyApprover fully configured (see SETUP.md)
- A Python LLM app that you want to add human-in-the-loop approval to.


## Benefits
- Improved organization AI security posture
- Ensure auditability of LLM agent decisions/approval chain
     - OWASP Top 10 for LLM #8 (Excessive Agency)
     - OWASP Top 10 for LLM #9 (Overreliance)
- Introduce new agent features with less false positives for improved customer experience
- Improve model responses with input/output pair data logging (reinforcement learning)
- Be prepared for potential future AI compliance regulations

## FAQ
### Why does this matter? I just want to deploy my agent to production and not worry about it.
Hallucinations are still an unsolved piece of the puzzle in in operating LLMs safely. This problem can be compounded by using untuned commercial models for tasks requiring special context. Depending on the scope of the privileged actions you want to take, this could be a small hiccup or affect your business reputation.
