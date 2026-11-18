# Agent Action Reversibility Classification

## Purpose

This document defines a classification for AI agent actions based on how easily the action's outcome can be reversed once executed. It establishes four reversibility levels (R0 to R3), maps them against the agent autonomy levels (A0 to A4), and prescribes the minimum execution controls required at each intersection. R0 to R3 are this standard's own labels. FSI in the example columns means the financial services industry.

Reversibility is a design-time and deployment-time decision. The same action may be classified at different reversibility levels depending on how the surrounding system is built. For example, a database write is R1 (Fully Reversible) if the system implements soft-delete with recovery, but R3 (Irreversible) if the system performs hard-delete without backup.

Reversibility is assessed for the action together with its downstream consequences, even though the Agent Autonomy Levels classification treats the action itself as atomic.

The classification is intended for use during architecture review, pattern selection, and operational risk assessment for AI agent deployments.

---

## Reversibility Levels

| Level | Name | Definition | Recovery Characteristics | FSI Examples |
|:---|:---|:---|:---|:---|
| **R0** | Informational | The action produces output only. No system state is mutated. The agent reads, retrieves, summarises, or recommends, but does not act on any external system. | No recovery needed. Nothing changed. The human decides what to do with the output. | Summarising earnings transcripts. Retrieving a customer record for display. Generating a draft commentary for human review. |
| **R1** | Fully Reversible | The action mutates system state, but the mutation can be completely undone with no residual impact on downstream systems or stakeholders. The system provides a deterministic undo or rollback mechanism. | Full state restoration is possible. No downstream consumers have acted on the intermediate state. The undo mechanism is automated or requires minimal manual effort. Time window for reversal is defined and enforced. | Creating a draft document in a content management system. Writing to a staging database with no downstream subscribers. Updating an internal case status before any notification is sent. |
| **R2** | Partially Reversible | The action mutates system state and can be partially undone, but some downstream consequences cannot be fully retracted. Reversal requires compensating actions, and residual effects may persist. | Primary state can be restored, but secondary effects remain. Downstream systems or stakeholders may have consumed or acted on the original output. Compensating actions (corrections, amendments, follow-up communications) are required. | Sending an internal email (content delivered, but a correction can follow). Updating a customer record where downstream reporting has already captured the previous value. Publishing an internal report that has been read but can be retracted with a correction notice. |
| **R3** | Irreversible | The action produces consequences that cannot be undone once executed. The outcome has crossed an organisational, legal, or physical boundary from which there is no automated recovery path. | No technical undo exists. Legal, financial, or reputational consequences persist regardless of subsequent corrective action. External parties, regulators, or markets have received and may have acted on the output. | Executing a wire transfer to an external counterparty. Submitting a regulatory filing to a supervisory authority. Disclosing personally identifiable information to a third party. Deploying code to a production environment serving live clients. |

---

## Autonomy Level and Reversibility Matrix

This matrix defines the minimum required execution mode for each combination of autonomy level and reversibility level. The execution modes are defined in the Execution Modes section.

| Autonomy | R0 (Informational) | R1 (Fully Reversible) | R2 (Partially Reversible) | R3 (Irreversible) |
|:---|:---|:---|:---|:---|
| **A0** (No Agency) | Direct | N/A | N/A | N/A |
| **A1** (Tool-Calling) | Direct | Human approval per action | Human approval per action | Human approval per action |
| **A2** (Workflow) | Direct | Execute with audit trail | Checkpoint approval required | Escalate to human |
| **A3** (Goal-Directed) | Direct | Execute with audit trail | Staged commit with review window | Escalate with dual approval |
| **A4** (Self-Directing) | Direct | Execute with audit trail and anomaly detection | Staged commit with mandatory review window | Block, or escalate with dual approval and staged commit |

### Reading the Matrix

- **Rows** represent the agent's autonomy level as defined in [Agent Autonomy Levels](../std_agent_autonomy/agent_autonomy_levels.md). The row labels use the short names of the autonomy levels.
- **Columns** represent the reversibility classification of the specific action being performed.
- **Cells** specify the minimum execution mode. An organisation may impose stricter controls but must not relax below the specified mode. The cells write each mode name in sentence case; the headings in the Execution Modes section give the same names in title case.
- **A0 is N/A for R1 through R3** because A0 agents produce output only and do not perform actions that mutate system state.

---

## Execution Modes

Each execution mode defines a set of controls that must be in place before the action takes effect.

### Direct

The agent executes the action without additional approval or staging. The action is logged for audit purposes. This mode applies only when the action has no side effects (R0) or when the autonomy level is sufficiently low that existing per-action human approval provides adequate control.

### Human Approval Per Action

A human must explicitly approve the action before execution. The approval must be recorded with the approver's identity, timestamp, and the action details that were presented for review. This is the default mode for A1 agents regardless of reversibility level, because A1 is defined as requiring human approval for every action.

### Execute with Audit Trail

The agent may execute the action without pre-approval, but the system must produce an immutable, timestamped audit record of the action, its inputs, its outputs, and the agent identity. The audit trail must support post-hoc review and incident investigation. This mode is appropriate only for fully reversible actions where the undo mechanism is verified and the reversal time window is defined.

### Checkpoint Approval Required

The agent operates within a defined workflow and does not require approval at every step. However, actions classified as R2 represent a checkpoint where the workflow must pause and obtain human approval before proceeding. The checkpoint must present the action details, the downstream systems that will be affected, and the compensating actions available if reversal is needed.

### Escalate to Human

The action is outside the scope that the agent is permitted to execute autonomously. The agent must present the proposed action to a designated human decision-maker, including full context, risk assessment, and the reason escalation was triggered. The agent must not execute the action until the human provides explicit approval. One approving human is sufficient for this mode; Escalate with Dual Approval is a separate mode.

### Staged Commit with Review Window

The action is separated into distinct phases: preparation, validation, commitment, and (if needed) compensation. The agent may complete preparation and validation autonomously, but the commitment phase, the final step that makes the action take effect, is held in a pending state for a defined review window. During this window, a human reviewer or an automated policy check may inspect the staged action and approve, modify, or reject it. If the review window expires without approval, the action does not proceed. Staging preserves the organisation's ability to inspect, reverse, or contain side effects while allowing the agent to make progress on reversible preparatory work. The matrix names the A4 variant "Staged commit with mandatory review window". The description in this section applies to both variants.

### Escalate with Dual Approval

The action requires explicit approval from two independent authorised individuals before execution (dual approval; NIST SP 800-53 Rev. 5 calls the same arrangement dual authorization or two-person control). This mode applies to irreversible actions initiated by goal-directed agents (A3), and to A4 agents where the matrix does not block the action, because the combination of high autonomy and permanent consequences demands additional assurance. The two approvers must be independent: they cannot be the same person, and neither can be the agent's deployer or the person who defined the agent's objective.

### Block

The action is not permitted at the specified autonomy level and reversibility combination. The agent must not execute the action under any circumstances. If the action is required, it must be performed by a human or by a lower-autonomy agent with appropriate human oversight. Where a matrix cell offers "Block, or" an alternative, either satisfies the minimum, and Block is the stricter option.

---

## Determining the Reversibility Level

The reversibility level of an action is not an inherent property of the action verb (write, delete, send). It is determined by the combination of the action, the target system, and the safeguards built into the execution environment. The following factors must be assessed:

| Factor | Questions |
|:---|:---|
| **State mutation** | Does the action change the state of any external system? If no, classify as R0. |
| **Undo mechanism** | Does the target system provide a verified, automated mechanism to fully reverse the state change? If yes, and no downstream systems have consumed the intermediate state, classify as R1. |
| **Downstream propagation** | Has the output been consumed by downstream systems, stakeholders, or external parties before reversal can occur? If yes, but the primary state can still be restored, classify as R2. |
| **External boundary crossing** | Has the output crossed a legal, regulatory, organisational, or physical boundary from which there is no technical recovery? If yes, classify as R3. |
| **Time sensitivity** | Is there a defined time window within which reversal is feasible? Actions that are R1 within a time window may become R2 or R3 after the window closes. |

### Reversibility Can Change Over Time

An action's reversibility level is not static. A database write may be R1 at the moment of execution (soft-delete available, no downstream consumers yet) but degrade to R2 after a downstream ETL process ingests the data, and to R3 after a regulatory report incorporates the value. Systems must be designed to classify reversibility at the point of execution, not at the point of design.

---

## Design Requirements by Reversibility Level

Each reversibility level carries minimum design requirements for any system that permits AI agents to perform actions at that level.

### R0: Informational

- Log all queries and outputs for audit and compliance.
- Apply input validation and output filtering in line with the organisation's security controls.
- No additional reversibility-specific controls required.

### R1: Fully Reversible

- The target system must expose a verified undo or rollback API.
- The undo mechanism must be tested as part of the agent deployment validation.
- A maximum reversal time window must be defined and enforced (e.g., 15 minutes, 1 hour, 24 hours).
- The audit trail must capture both the original action and any subsequent reversal.
- Monitoring must alert if a reversal is not completed within the defined window when triggered.

### R2: Partially Reversible

- All R1 requirements apply.
- The system must identify and document all downstream consumers of the action's output.
- Compensating actions must be defined, documented, and tested for each downstream effect.
- Pre-action snapshots of affected state must be captured to support partial restoration.
- The checkpoint or staged commit mechanism must present the downstream impact assessment to the reviewer.

### R3: Irreversible

- All R2 requirements apply, except those that depend on a technical undo mechanism (the verified undo or rollback API, the undo test, the maximum reversal time window and the monitoring alert for a reversal not completed within that window), because no technical undo exists for an irreversible action.
- The system must verify, before the action crosses the point of no return (the point at which it can no longer be recalled), that all required authority, policy, evidence and control conditions are satisfied.
- Pre-action approval must be recorded and must include: the action details, the irreversibility classification, the downstream impact, the approver identity (or, where dual approval applies, both approver identities), and the timestamp.
- The approval record must be immutable and retained per the organisation's records management policy.
- A kill switch or circuit breaker must exist to halt the agent before the irreversible action executes, and the agent must not be able to disable or circumvent this mechanism.

---

## Related Frameworks and Sources

This section is informational and is not legal, regulatory or compliance advice. References to laws, standards and supervisory guidance describe related provisions only and do not establish that a system meets any legal or regulatory obligation. Which obligations apply, for example whether a system is high-risk under Regulation (EU) 2024/1689 (the EU AI Act), as amended by Regulation (EU) 2026/1744, is a determination for the adopting organisation and its legal advisers. Items marked as preprints, drafts or vendor or community specifications are not standards and have no regulatory standing.

The following frameworks, standards and publications address concerns related to this classification. This classification has not been assessed for conformity with any of them, and citing a source does not mean the source requires or endorses it.

| Framework | Relevant Provisions |
|:---|:---|
| **EU AI Act** (Regulation (EU) 2024/1689, as amended by Regulation (EU) 2026/1744) | Article 14(4)(d) provides that persons assigned human oversight are enabled, as appropriate and proportionate, to "disregard, override or reverse the output" of high-risk AI systems. Article 7(2)(i) lists reversibility of outcomes among the criteria the Commission takes into account when deciding whether to add or modify use-cases in Annex III, applying them when assessing the condition under Article 7(1), point (b) (whether the risk is equivalent to or greater than that of systems already in Annex III), stating that outcomes having an adverse impact on health, safety or fundamental rights "shall not be considered to be easily corrigible or reversible." Under Regulation (EU) 2026/1744, Chapter III Sections 1 to 3 (which include these articles) apply to AI systems classified as high-risk pursuant to Article 6(2) and Annex III from 2 December 2027 and to those classified pursuant to Article 6(1) and Annex I from 2 August 2028 (Article 113, third paragraph, point (c), as amended). [1][5] |
| **NIST AI RMF 1.0** (voluntary framework) | MANAGE 2.4 calls for mechanisms to "supersede, disengage, or deactivate AI systems that demonstrate performance or outcomes inconsistent with intended use." MANAGE 4.1 describes post-deployment monitoring plans that include mechanisms for "appeal and override, decommissioning, incident response, recovery, and change management." [2] |
| **IMDA Model AI Governance Framework for Agentic AI (version 1.5)** | The IMDA model framework addresses related concerns: it lists reversibility among "non-exhaustive factors" that "affect the level of risk of an agentic use case", as the risk factor "Reversibility of agent's actions: If the agent can modify data and systems, whether such modifications are easily reversed." (section 2.1.1). Its Executive Summary mentions "significant checkpoints in the agentic workflow that require human approval, such as high-stakes or irreversible actions". It says "Organisations should define significant checkpoints or action boundaries that require human approval, especially before sensitive actions are executed." (section 2.2.2), and lists "Irreversible actions e.g. permanently deleting data, sending communications, making payments" among the items. It lists "Denying action by default when approval infrastructures fail" (section 2.2.2) and "Intervene in real-time: When potential failures are detected, stop agent workflow and escalate to a human supervisor" (section 2.3.3). [3] |
| **EU AI Act, further provisions** (Regulation (EU) 2024/1689) | The EU AI Act addresses related concerns for high-risk AI systems. Article 14(4)(e) says oversight persons are to be enabled "to intervene in the operation of the high-risk AI system or interrupt the system through a 'stop' button or a similar procedure that allows the system to come to a halt in a safe state." Article 15(4) says "The robustness of high-risk AI systems may be achieved through technical redundancy solutions, which may include backup or fail-safe plans." Article 14(5) addresses a narrow case only, remote biometric identification systems listed in Annex III point 1(a): it says "no action or decision is taken by the deployer on the basis of the identification resulting from the system unless that identification has been separately verified and confirmed by at least two natural persons". [1][5] |
| **OSFI Guideline E-23, Model Risk Management** (final, 11 September 2025; effective 1 May 2027) | OSFI Guideline E-23 addresses related concerns. Section A.4 says a model is "An application of theoretical, empirical, judgmental assumptions or statistical techniques, including AI/ML methods, which processes input data to generate results." Principle 3.6 says monitoring should include "determining contingency plans for model unavailability, deterioration in model performance, or outright failure along with the escalation procedures for addressing these" and that the decommissioning process includes "Retaining the retired model and documentation for a set period as a benchmark or fallback." Principle 3.5 says deployment should involve "clearly documented procedures that outline deployment steps, stakeholder responsibilities, approval hierarchies, change control, monitoring frameworks and exception handling including overlays". [6] |
| **OSFI Technology Risk Bulletin on generative and agentic AI** (July 2026; bulletin outlining sound practices that institutions can consider) | OSFI's July 2026 Technology Risk Bulletin addresses related concerns. It lists the practice "enforce approval checkpoints for high-risk actions to prevent unintended impacts" (Controlled software development and changes) and the practice "test AI failure and outage scenarios and establish manual fallbacks and continuity measures for AI-supported business processes, reducing operational disruption" (Increase resilience and manage third-party risk). [7] |
| **MAS Guidelines on Artificial Intelligence Risk Management** (final, 7 October 2026; supervisory expectations that take effect on 7 October 2027; FIs may meet Sections 5 and 6 by 7 October 2028 (paragraph 1.8)) | The Monetary Authority of Singapore Guidelines address related concerns. Paragraph 5.23(b) says "For high risk materiality AI, consider implementing 'kill switches' or override mechanisms to rapidly deactivate the AI system if it exceeds risk tolerances." Paragraph 5.3 says "For AI with 'kill switches', clear contingency activation protocols should be in place and tested regularly." Paragraph 5.25(b) says version control may "support traceability, auditability, and the ability to roll back to previous versions." [8] |
| **US interagency model risk management guidance, SR 26-2** (supervisory guidance, 17 April 2026) | US interagency model risk management guidance addresses related concerns only by stating its scope: it says "Generative AI and agentic AI models are novel and rapidly evolving. As such, they are not within the scope of this guidance." (Attachment, Section II, footnote 3). The attachment says it "does not set forth enforceable standards or prescriptive requirements" (Section I). [9] |
| **NIST AI 600-1, Generative AI Profile** (July 2024) | NIST AI 600-1 addresses related concerns for generative AI systems: suggested action MG-2.4-002 is to "Establish and maintain procedures for escalating GAI system incidents to the organizational risk management authority when specific criteria for deactivation or disengagement is met for a particular context of use or for the GAI system as a whole." [10] |
| **OWASP Top 10 for LLM Applications 2025** (LLM06:2025 Excessive Agency) | OWASP addresses related concerns: its mitigation says "Require user approval: Utilise human-in-the-loop control to require a human to approve high-impact actions before they are taken." [11] |

---

## Summary

| Level | Name | Can It Be Undone? | Principal Required Safeguards (at A2 and above) |
|:---|:---|:---|:---|
| **R0** | Informational | Nothing to undo | Standard input/output controls |
| **R1** | Fully Reversible | Yes, completely, within a defined time window | Audit trail, verified undo mechanism |
| **R2** | Partially Reversible | Partially, with compensating actions | Staged commit or checkpoint approval, pre-action snapshot, downstream impact assessment |
| **R3** | Irreversible | No | Pre-action verification check, dual approval for A3 and above, kill switch or circuit breaker, immutable approval record |

---

## Glossary

**Action**  
One tool invocation that produces one externally observable side effect. Consistent with the definition in [Agent Autonomy Levels](../std_agent_autonomy/agent_autonomy_levels.md) (reference 4).

**Audit trail**  
"A chronological record that reconstructs and examines the sequence of activities surrounding or leading to a specific operation, procedure, or event in a security-relevant transaction from inception to result." Source: [NIST CSRC glossary](https://csrc.nist.gov/glossary/term/audit_trail), from NIST SP 800-53 Rev. 5 and NIST SP 800-37 Rev. 2.

**Compensating action**  
A subsequent action designed to mitigate or partially reverse the effects of a prior action when full reversal is not possible. Examples include correction notices, amended filings, and refund transactions.

**Downstream propagation**  
The process by which the output of an action is consumed, transformed, or acted upon by systems, processes, or stakeholders beyond the immediate target of the original action. This standard's own term.

**External boundary**  
A legal, regulatory, organisational, or physical threshold beyond which the originating system can no longer recall the effects of an action. Examples include transmission to an external counterparty, submission to a regulator, or physical actuation. This standard's own term.

**Kill switch**  
A mechanism that can halt an agent's execution immediately and that the agent itself cannot disable, bypass, or circumvent. Compare the "stop" button in Article 14(4)(e) of Regulation (EU) 2024/1689 (reference 1) and the controllability property in ISO/IEC 22989:2022, 3.5.6: "property of an AI system (3.1.4) that allows a human or another external agent to intervene in the system's functioning". The comparison is for orientation only; neither source defines the term kill switch.

**Reversal time window**  
The defined period after an action executes during which it can still be fully reversed. After this window closes, the action's reversibility level may degrade (for example from R1 to R2 or R3). This standard's own term.

**Separation of duties**  
Separation of Duty (SOD), in the words of the NIST CSRC glossary, "refers to the principle that no user should be given enough privileges to misuse the system on their own." Source: [NIST CSRC glossary](https://csrc.nist.gov/glossary/term/separation_of_duty), from NIST SP 800-192.

**Staged commit**  
An execution pattern that separates an action into distinct phases (preparation, validation, commitment, compensation) so that the commitment phase can be held pending review while preparatory work proceeds. This standard uses the term as stated here.

**System state mutation**  
Any change made to an external system as a direct or indirect result of an agent's action. Consistent with the definition in [Agent Autonomy Levels](../std_agent_autonomy/agent_autonomy_levels.md).

**Tamper-evident**  
"A process which makes alterations to the data easily detectable." Source: [NIST CSRC glossary](https://csrc.nist.gov/glossary/term/tamper_evident), from NISTIR 8202. Distinguished from tamper-resistant, defined in the same source as "A process which makes alterations to the data difficult (hard to perform), costly (expensive to perform), or both."

---

## References

1. European Parliament and Council. Regulation (EU) 2024/1689 (the EU AI Act), as amended by Regulation (EU) 2026/1744, Articles 7, 14 and 15. [EUR-Lex](https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng). Official Journal L, 12 July 2024.
2. National Institute of Standards and Technology. [AI Risk Management Framework (AI RMF 1.0)](https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf), NIST AI 100-1. January 2023.
3. Infocomm Media Development Authority. [Model AI Governance Framework for Agentic AI, version 1.5](https://www.imda.gov.sg/-/media/imda/files/about/emerging-tech-and-research/artificial-intelligence/mgf-for-agentic-ai.pdf). Singapore. Version 1.5, published 20 May 2026 (updated 5 June 2026).
4. FINOS AI Reference Architecture Library. [Agent Autonomy Levels](../std_agent_autonomy/agent_autonomy_levels.md).
5. European Union. [Regulation (EU) 2026/1744 of 8 July 2026 amending Regulations (EU) 2024/1689, (EU) 2018/1139 and (EU) 2023/1230 as regards the simplification of the implementation of harmonised rules on artificial intelligence (Digital Omnibus on AI)](https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng). Official Journal L, 2026/1744, 24 July 2026. In force; it entered into force on the third day following its publication (27 July 2026).
6. Office of the Superintendent of Financial Institutions (Canada). [Guideline E-23 Model Risk Management (2027)](https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/guideline-e-23-model-risk-management-2027). Final guideline, 11 September 2025; effective 1 May 2027.
7. Office of the Superintendent of Financial Institutions (Canada). [Technology Risk Bulletin, Generative and Agentic Artificial Intelligence: Implications for Technology, Cyber Security, and Operational Resilience](https://www.osfi-bsif.gc.ca/en/risks/technology-cyber-risk-management/technology-risk-bulletin/generative-agentic-artificial-intelligence-implications-technology-cyber-security-operational). July 2026. Bulletin outlining sound practices that institutions can consider.
8. Monetary Authority of Singapore. [Guidelines on Artificial Intelligence Risk Management](https://www.mas.gov.sg/-/media/mas-media-library/regulation/guidelines/bd/guidelines-on-artificial-intelligence-risk-management-for-financial-institutions/guidelines-on-artificial-intelligence-risk-management.pdf). Final, 7 October 2026. Supervisory expectations; they take effect on 7 October 2027; FIs may meet Sections 5 and 6 by 7 October 2028 (paragraph 1.8).
9. Board of Governors of the Federal Reserve System, Federal Deposit Insurance Corporation and Office of the Comptroller of the Currency. [Supervisory Guidance on Model Risk Management, SR 26-2 Attachment](https://www.federalreserve.gov/supervisionreg/srletters/SR2602a1.pdf). Supervisory guidance, 17 April 2026.
10. National Institute of Standards and Technology. [NIST AI 600-1, Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf). Final, July 2024.
11. OWASP Foundation. [OWASP Top 10 for LLM Applications 2025, LLM06:2025 Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/). 2025.
