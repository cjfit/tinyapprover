# TinyApprover Static Actions
Not ready to leverage LLMs in your incident response discipline yet? No problem! 

TinyApprover can be configured for the basic function of triggering logic you write in the `TaskExecutorLambda` from incident comments.

## The Example of Todd

Let's say Todd is a security analyst who follows a runbook for common SOC alerts in PagerDuty.

He is looking for a way to automate actions he almost always has to take in response to a common alert. However, there is a 30% chance the action is a false positive and he shouldn't take action on it.

Todd isn't ready to go through the lengthy process of procuring a security vendor yet because of budgetary constraints and because business requirements aren't clear. He wants an open-source tool that can deploy a Lambda to his AWS account so he doesn't need to manually triage and run the commands on his laptop.

Open-source TinyApprover is the perfect solution for this problem. Todd can save valuable time on his SOC work and in nail down the requirements in a proposal to his org lead for procuring a vendor.


### The Runbook
![Runbook](/screenshots/runbook-example.png)

Ok, this runbook is a bit contrived but it's a good example of the common toil that a SOC responder would actually go through triaging an alert.

It's manual effort that could easily be offloaded by writing a Lambda to trigger the relevant actions and having it trigger via an incident comment.

## Putting it all together
### Setup
1. Define the action to take in `TaskExecutorLambda`: In this case starting a new build on the appropriate CircleCI pipeline with the IP param.
2. Configure the existing alert source to send a webhook to TinyApprover with the relevant IP as a body parameter.
3. Test that a new IP ban event creates a PD incident via TinyApprover.

### The new workflow
1. Your alert source bans an IP for suspected DoS and sends a webhook to TinyApprover with the IP in the body.
2. TinyApprover looks up the relevant saved action and creates a new PagerDuty incident.
![PD Example 1](/screenshots/pd-example-1.png)

3. Todd quickly looks up the IP and declares it a false positive. He comments "yes" on the incident.
![PD Example 1](/screenshots/pd-example-2.png)
4. The Lambda is triggered and the action of unbanning the IP is taken. The PagerDuty incident resolves.

### Conclusion

In conclusion, the task that would have taken Todd nearly 40 mins including the context switch has now been reduced to merely ~5 (the IP lookup). 

Todd can further enhance this by adding automatic logic to look up the IP in his SIEM and enriching the alert with this information.

If he wanted to take it a step further, he could even write an LLM agent app leveraging RAG to automatically triage the alert - covered in [LLM_APP.md](https://github.com/cjfit/tinyapprover/blob/main/examples/LLM_APP.md)

## Next Steps

This scenario highlights the basic functionality of TinyApprover - saving time by adding automatic actions to alerts. I hope this scenario helps convey the value of this open source framework. If you are a SOC responder with feedback, please reach out!