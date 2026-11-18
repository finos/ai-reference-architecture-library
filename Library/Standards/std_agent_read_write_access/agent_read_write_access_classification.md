# Agent Read/Write Access Classification

## Purpose

This document defines a classification for the data and system access granted to an AI agent, independent of how autonomously the agent decides to act ([Agent Autonomy Levels](../std_agent_autonomy/agent_autonomy_levels.md)) and independent of how easily an action can be undone ([Agent Action Reversibility Classification](../std_agent_reversibility/agent_action_reversibility_classification.md)). It establishes four access levels (AC0 to AC3), maps them against the agent autonomy levels (A0 to A4), and prescribes the minimum controls required at each intersection. AC0 to AC3 are this standard's own labels and are not NIST SP 800-53 AC controls. FSI in the example columns means the financial services industry.

Access level answers a different question than autonomy or reversibility. Autonomy asks how independently the agent decides. Reversibility asks whether, and how fully, the outcome can be undone if the agent is wrong. Access asks what the agent can *reach* in the first place, regardless of how it decides to reach it or how recoverable the outcome is. A low-autonomy agent with broad write access to a production database is not made safe by its low autonomy; an agent given only read access cannot cause an irreversible write no matter how autonomous it is. Treating access as its own axis, rather than folding it into autonomy, is consistent with how OWASP separates "excessive permissions" from "excessive autonomy" as distinct root causes of the same failure category [1].

The classification is intended for use during architecture review, pattern selection, credential provisioning, and operational risk assessment for AI agent deployments.

---

## Access Levels

| Level | Name | Definition | Representative Scope | FSI Examples |
|:---|:---|:---|:---|:---|
| **AC0** | No Access | The agent has no credential, token, or connection to the system or data class in question. Any information it produces about that system came from context provided in the prompt, not from a live connection. | No tool binding, no API credential, no data-store connection exists for this system. | A drafting assistant reasoning about a hypothetical trade based only on figures pasted into the conversation, with no market data feed connection. |
| **AC1** | Read-Only | The agent can query, retrieve, or subscribe to data or system state, but has no mechanism, credential, or tool that can mutate that system. Read access still carries risk: it is a primary path for data exfiltration and for a compromised or manipulated agent to disclose information beyond its intended audience. | Read-scoped API tokens or database roles (e.g., `SELECT`-only credentials, a read-only OAuth scope such as `files:read` [2]). No `INSERT`, `UPDATE`, `DELETE`, or state-changing endpoint is reachable. | A know-your-customer (KYC) assistant that retrieves a customer record for display but cannot amend it. A trade research agent that pulls live market data but cannot place an order. |
| **AC2** | Scoped Write | The agent can mutate state, but only within an explicitly enumerated, narrow set of fields, records, or actions defined in advance. The scope excludes destructive operations (deletion, overwrite of another party's data), schema or permission changes, and any action outside the enumerated set. This is the technical expression of least privilege: the agent's write capability is reduced to the minimum necessary for its function [3]. | Field-level or row-level write permissions; a fixed, allow-listed set of API write endpoints; write-scoped OAuth tokens bound to a specific resource (e.g., `files:write` against one named resource, not a wildcard; this is this document's own guidance). | A reconciliation agent that may update the status field of a break it has already matched, but cannot alter the underlying ledger entry. An onboarding agent that may write to its own case record but not to the core customer master. |
| **AC3** | Full Write / Administrative | The agent can perform unrestricted or broadly-scoped write operations: schema changes, permission or credential changes, bulk or destructive operations, or write access to systems outside its immediate task boundary. This is the access profile OWASP describes as excessive permissions or excessive functionality when granted beyond what the agent's task requires [1]. | Administrative database roles, credential-issuing or permission-granting APIs, infrastructure-as-code execution, bulk delete or overwrite operations. | An agent with `DROP TABLE` or schema-migration capability. An agent that can create or modify other agents' credentials. An agent with unscoped write access to a shared production data store. |

---

## Autonomy Level and Access Matrix

This matrix defines the minimum required control for each combination of autonomy level and access level. Execution modes (Direct, Human Approval Per Action, Execute with Audit Trail, Checkpoint Approval Required, Escalate to Human, Staged Commit with Review Window, Escalate with Dual Approval, Block) are the same modes defined in section Execution Modes of the [Agent Action Reversibility Classification](../std_agent_reversibility/agent_action_reversibility_classification.md#execution-modes), reused here deliberately so that an architect evaluating one axis is already fluent in the vocabulary of the other.

| Autonomy | AC0 (No Access) | AC1 (Read-Only) | AC2 (Scoped Write) | AC3 (Full Write / Admin) |
|:---|:---|:---|:---|:---|
| **A0** (No Agency) | Direct | N/A | N/A | N/A |
| **A1** (Tool-Calling) | Direct | Human approval per action | Human approval per action | Human approval per action |
| **A2** (Workflow) | Direct | Execute with audit trail | Checkpoint approval required | Escalate to human |
| **A3** (Goal-Directed) | Direct | Execute with audit trail | Staged commit with review window | Escalate with dual approval |
| **A4** (Self-Directing) | Direct | Execute with audit trail and anomaly detection | Staged commit with mandatory review window | Block, or escalate with dual approval and staged commit |

### Reading the Matrix

- **Rows** represent the agent's autonomy level as defined in [Agent Autonomy Levels](../std_agent_autonomy/agent_autonomy_levels.md). The row labels use the short names of the autonomy levels.
- **Columns** represent the access level of the credential or connection the agent has been granted, not the specific action it happens to take in a given instance.
- **Cells** specify the minimum control. An organisation may impose stricter controls but must not relax below the specified mode. The cells write each mode name in sentence case; the Agent Action Reversibility Classification gives the same names in title case.
- **A0 is N/A for AC1 through AC3** because A0 agents have no ability to access tools, APIs, or external systems by definition; granting any live access to an A0 agent reclassifies it as A1 or above.
- **At A1, every action that uses access requires human approval per action** (AC1 to AC3), as in the Reversibility Classification, because Agent Autonomy Levels defines A1 as an agent that cannot carry out any action without a human approving it first.
- This matrix intentionally mirrors the structure of the Autonomy-Reversibility matrix in [Agent Action Reversibility Classification](../std_agent_reversibility/agent_action_reversibility_classification.md), because access and reversibility are both risk-scaling axes evaluated against the same autonomy levels. They are not the same axis: an AC1 (read-only) action is always R0 by definition (nothing is mutated, so nothing needs to be reversed), but an AC2 or AC3 action's reversibility must be assessed independently using the Reversibility Classification. See "Combining Access with Reversibility" below.

---

## Combining Access with Reversibility

Access level and reversibility level are independent axes evaluated together for any action that mutates state. Access answers "was the agent permitted to reach this system at all, and how broadly." Reversibility answers "if this specific write goes wrong, can it be undone." The same AC2 (Scoped Write) credential can produce an R1 action one day (a reversible status update) and an R2 action the next (the same field, but a downstream report has already consumed it).

When an action's access level and reversibility level prescribe different minimum controls, **the stricter of the two governs**. An action that is both AC2 and R3 (a narrowly-scoped write that happens to be irreversible, such as a scoped credential that can trigger a one-time external notification) must meet the R3 requirements in the Reversibility Classification (the pre-action verification check, the kill switch or circuit breaker, and the immutable approval record) in addition to the AC2 requirements below, not instead of them. Neither classification alone is sufficient to evaluate a write action; both must be assessed, and the design must satisfy whichever is more restrictive. For example, an AC3 credential used for an R1 action at A3 takes Escalate with Dual Approval and verifiability tier V3, because the stricter control governs.

This two-axis (or, with autonomy, three-axis) evaluation model keeps access and reversibility as separate questions rather than forming one composite judgement. Keeping them separate lets each be assessed and verified on its own; this is this standard's own position.

---

## Determining the Access Level

The access level of an agent is a property of its provisioned credentials and connections, not of any single action it takes. The following factors must be assessed at provisioning time and re-assessed whenever a credential, tool binding, or scope is changed:

| Factor | Questions |
|:---|:---|
| **Connection existence** | Does the agent hold any live credential, token, or tool binding to the system or data class in question? If no, classify as AC0. |
| **Mutation capability** | Can any credential, tool, or API binding the agent holds change state in the target system? If no, and only retrieval is possible, classify as AC1. |
| **Scope enumeration** | Is the set of fields, records, or actions the agent can write to explicitly enumerated and bounded, with destructive and administrative operations excluded? If yes, classify as AC2. |
| **Administrative or destructive capability** | Can the agent perform schema changes, permission changes, bulk operations, deletions, or writes outside an enumerated scope? If yes, classify as AC3 regardless of how narrow the agent's typical usage pattern is. Access level reflects what the credential *permits*, not what the agent has done so far. |
| **Blast radius beyond the immediate task** | Does the credential grant access to systems or data outside what the agent's specific task requires? Excess reach here is what OWASP terms excessive permissions, and it elevates the classification even if the agent has not yet exercised that reach [1]. |

### Access Level Reflects the Credential, Not Observed Behaviour

An agent that has only ever performed read operations, but holds a credential capable of writes, is AC2 or AC3, not AC1. Classification is based on what the provisioned access permits; this document's position is that least privilege must be enforced by the system, not by the agent's demonstrated restraint. A credential audit that finds an agent has broader access than its classification implies is itself a finding requiring remediation, independent of whether that excess access has been misused.

---

## Design Requirements by Access Level

### AC0: No Access

- No credential provisioning is required.
- If the agent's output references the system or data class in question, the output must be labelled as unverified against a live source.

### AC1: Read-Only

- Credentials must be provisioned as read-only at the infrastructure or API layer (e.g., a database role with no `INSERT`/`UPDATE`/`DELETE` grants, an OAuth scope limited to `read` or equivalent), not enforced only by agent instruction or prompt.
- Query and retrieval activity must be logged, including the query, the data returned, and the agent identity, consistent with the audit requirements in the Reversibility Classification's R0 (Informational) level.
- Read access to sensitive or regulated data classes must be scoped to the minimum fields required for the agent's task, not the full record.
- Unique agent identity must be attached to every read credential so that access can be attributed to a specific agent instance, not a shared service account, as the framework of the Singapore Infocomm Media Development Authority (IMDA) suggests [4].

### AC2: Scoped Write

- All AC1 requirements apply.
- The enumerated write scope must be documented and reviewed at deployment and on any change: which fields, records, or endpoints the agent may write to, and which it explicitly may not.
- Destructive operations (delete, overwrite of another party's data) must not be included in an AC2 scope; a credential that permits deletion is AC3 regardless of how it is otherwise restricted.
- Write credentials must be distinct from, and narrower than, any read credentials the agent also holds; a single broad credential used for both is a control gap.
- The tool or API layer, not the agent's own judgement, must reject any write request outside the enumerated scope.

### AC3: Full Write / Administrative

- All AC2 requirements apply.
- Administrative or destructive credentials must require a documented business justification and time-bound provisioning rather than standing access (this document's own guidance).
- A pre-action approval record must capture the credential used, the specific administrative or destructive operation, the approver identity or identities, and the timestamp, mirroring the R3 approval record requirement in the Reversibility Classification.
- Administrative credentials granted to an agent must be excluded from the agent's own ability to modify, extend, or re-grant, preventing privilege self-escalation (the agent-performed form of privilege escalation, MITRE CAPEC-233).
- Access reviews for AC3 credentials must occur at a defined cadence independent of whether the agent has exercised the access, since any administrative capability that remains provisioned between uses is itself the risk being managed.

---

## Related Frameworks and Sources

This section is informational and is not legal, regulatory or compliance advice. References to laws, standards and supervisory guidance describe related provisions only and do not establish that a system meets any legal or regulatory obligation. Which obligations apply, for example whether a system is high-risk under Regulation (EU) 2024/1689 (the EU AI Act), as amended by Regulation (EU) 2026/1744, is a determination for the adopting organisation and its legal advisers. Items marked as preprints, drafts or vendor or community specifications are not standards and have no regulatory standing.

The following frameworks, standards and publications address concerns related to this classification. This classification has not been assessed for conformity with any of them, and citing a source does not mean the source requires or endorses it.

| Framework | Relevant Provisions |
|:---|:---|
| **OWASP Top 10 for LLM Applications (2025)** | LLM06:2025, Excessive Agency, lists excessive functionality, excessive permissions and excessive autonomy among the typical root causes of excessive agency, and lists limiting extensions, functionality and permissions among its prevention strategies. AC2 and AC3 exist specifically to give architects a way to name and bound that excess before deployment [1]. |
| **NIST SP 800-53 Rev. 5, AC-6 (Least Privilege)** | AC-6 states: "Employ the principle of least privilege, allowing only authorized accesses for users (or processes acting on behalf of users) that are necessary to accomplish assigned organizational tasks." SP 800-53 is a federal control set whose controls are applied by selection [3]. |
| **EU AI Act** (Regulation (EU) 2024/1689, as amended by Regulation (EU) 2026/1744) | Article 15 requires high-risk AI systems to achieve an appropriate level of cybersecurity and resilience against unauthorised third parties exploiting system vulnerabilities. Article 15 does not prescribe access levels. Under Regulation (EU) 2026/1744, Chapter III Sections 1 to 3 (which include these articles) apply to AI systems classified as high-risk pursuant to Article 6(2) and Annex III from 2 December 2027 and to those classified pursuant to Article 6(1) and Annex I from 2 August 2028 (Article 113, third paragraph, point (c), as amended). [6][7] |
| **IMDA Model AI Governance Framework for Agentic AI (version 1.5)** | The IMDA model framework recommends that each agent have a unique, cryptographically verifiable identity, and that the capacity in which it acts be recorded for auditability. It also addresses related concerns: it lists as a risk factor the "Scope of agent's actions: Whether an agent can only read from or can also modify the data and systems it has access to." (section 2.1.1); it says organisations should consider "Define least-privilege policies that give agents only the minimum tools and data access needed for it to complete its task." (section 2.1.2); and it says "Authorisations should generally be scoped, time- or session-bound, non-transferable, and follow the principle of least privilege by default, with explicit escalation paths for elevated permissions." (section 2.1.2, Agent identity). [4] |
| **ISO/IEC 42001, Annex A** | Annex A provides AI-system controls an organisation may select; consult the standard for controls on data and system resources [5]. |
| **Model Context Protocol, Authorization Specification (2025-11-25)** | Defines an optional authorisation flow for HTTP-based transports, based on OAuth 2.1 (draft), in which an MCP server can indicate the scopes required to access a protected resource. Its own worked examples use `files:read` and `files:write`; scope names are only examples [2]. |
| **OSFI Guideline E-23, Model Risk Management** (final, 11 September 2025; effective 1 May 2027) | OSFI Guideline E-23 addresses related concerns: Principle 2.3 lists, as something the model risk rating should determine, "limits or constraints on model usage (for example, limiting the model's scope, implementing additional safeguards, or even pursuing a different modeling approach)". [8] |
| **OSFI Technology Risk Bulletin on generative and agentic AI** (July 2026; bulletin outlining sound practices that institutions can consider) | OSFI's July 2026 Technology Risk Bulletin addresses related concerns. Under Control AI agent autonomy and access it lists the practice "assign unique non-human identities, enforce least privilege, apply scoped permissions, and use just-in-time access with short-lived credentials to reduce unauthorized access and limit compromised agents" and the practice "log and review agent activity and tool usage along with periodic access recertification to improve detection of anomalies and maintain ongoing access integrity". [9] |
| **OSFI Guideline B-13, Technology and Cyber Risk Management** (final, 31 July 2022; a general technology guideline, not specific to AI) | OSFI Guideline B-13 addresses related concerns for technology assets generally and does not mention AI agents: section 3.2.7 says that, "Where feasible", FRFIs should consider "Enforcing the principles of least privilege, conducting regular attestation of access" and "Logging and monitoring account activity as part of continuous security monitoring". [10] |
| **MAS Guidelines on Artificial Intelligence Risk Management** (final, 7 October 2026; supervisory expectations that take effect on 7 October 2027; FIs may meet Sections 5 and 6 by 7 October 2028 (paragraph 1.8)) | The Monetary Authority of Singapore Guidelines address related concerns. Paragraph 1.11 says "an AI agent with access to tools could autonomously execute unauthorised or erroneous actions that are not aligned with an FI's business objectives or in a customer's best interests". Paragraph 5.22(a) refers to "access controls based on the principle of least privilege". Paragraph 5.23(d) says "Access to AI systems or models, training data, pipelines, and configuration files should be strictly controlled and logged." [11] |

---

## Summary

| Level | Name | Can It Mutate State? | Principal Required Safeguards (at A2 and above) |
|:---|:---|:---|:---|
| **AC0** | No Access | No | None; label unverified references |
| **AC1** | Read-Only | No | Infrastructure-enforced read-only credential, logged retrieval, minimum-necessary field scope |
| **AC2** | Scoped Write | Yes, within an enumerated, non-destructive scope | Documented and reviewed write scope, distinct write credential, server-enforced scope rejection |
| **AC3** | Full Write / Administrative | Yes, without a bounded scope, or destructively | Time-bound provisioning, pre-action approval record, no privilege self-escalation, independent access review cadence |

---

## Glossary

**Access level**  
A property of the credentials, tokens, and tool bindings provisioned to an agent, describing the maximum data and system reach those credentials permit, independent of the agent's autonomy or of any specific action's reversibility. This standard's own term.

**Blast radius**  
The set of systems, data, or stakeholders an agent's provisioned access could affect, including systems the agent has not yet interacted with but is credentialed to reach. This standard uses the term as stated here.

**Least privilege**  
"The principle that a security architecture is designed so that each entity is granted the minimum system resources and authorizations that the entity needs to perform its function." Source: [NIST CSRC glossary](https://csrc.nist.gov/glossary/term/least_privilege), from NIST SP 800-53 Rev. 5 [3].

**Privilege self-escalation**  
A condition in which an agent can modify, extend, or re-grant its own access permissions, independent of whether it has done so. It is an instance of privilege escalation, which MITRE CAPEC-233 defines as "An adversary exploits a weakness enabling them to elevate their privilege and perform an action that they are not supposed to be authorized to perform." Source: [MITRE CAPEC-233](https://capec.mitre.org/data/definitions/233.html). AC3 design requirements explicitly prohibit it.

**Scope**  
The explicitly enumerated set of fields, records, actions, or endpoints a credential permits. Distinguished from a permission, which is the authorisation decision governing whether a given scope should be exercised in a specific instance.

**Tamper-evident**  
"A process which makes alterations to the data easily detectable." Source: [NIST CSRC glossary](https://csrc.nist.gov/glossary/term/tamper_evident), from NISTIR 8202. Distinguished from tamper-resistant, defined in the same source as "A process which makes alterations to the data difficult (hard to perform), costly (expensive to perform), or both."

**Unique agent identity**  
A digital identity that belongs to one agent instance and not to a shared service account or a human user, so that access and actions can be attributed to that agent. NIST defines digital identity as "An attribute or set of attributes that uniquely describes a subject within a given context" ([NIST CSRC glossary](https://csrc.nist.gov/glossary/term/digital_identity), from NIST SP 800-63-4). Consistent with the identity practice suggested in the Singapore Model AI Governance Framework for Agentic AI [4].

---

## References

1. OWASP Foundation. [*OWASP Top 10 for LLM Applications 2025*, LLM06:2025 Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/).
2. Model Context Protocol. [*Authorization Specification*, version 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization).
3. National Institute of Standards and Technology. [*Security and Privacy Controls for Information Systems and Organizations*, SP 800-53 Revision 5, Control AC-6: Least Privilege](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final).
4. Infocomm Media Development Authority. [*Model AI Governance Framework for Agentic AI*, version 1.5](https://www.imda.gov.sg/-/media/imda/files/about/emerging-tech-and-research/artificial-intelligence/mgf-for-agentic-ai.pdf). Singapore. Version 1.5, published 20 May 2026 (updated 5 June 2026).
5. International Organization for Standardization. *ISO/IEC 42001:2023, Information technology — Artificial intelligence — Management system*, Annex A.
6. European Parliament and Council. Regulation (EU) 2024/1689 (the EU AI Act), as amended by Regulation (EU) 2026/1744. [Article 15: Accuracy, Robustness and Cybersecurity](https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng). Official Journal L, 12 July 2024.
7. European Union. [Regulation (EU) 2026/1744 of 8 July 2026 amending Regulations (EU) 2024/1689, (EU) 2018/1139 and (EU) 2023/1230 as regards the simplification of the implementation of harmonised rules on artificial intelligence (Digital Omnibus on AI)](https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng). Official Journal L, 2026/1744, 24 July 2026. In force; it entered into force on the third day following its publication (27 July 2026).
8. Office of the Superintendent of Financial Institutions (Canada). [Guideline E-23 Model Risk Management (2027)](https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/guideline-e-23-model-risk-management-2027). Final guideline, 11 September 2025; effective 1 May 2027.
9. Office of the Superintendent of Financial Institutions (Canada). [Technology Risk Bulletin, Generative and Agentic Artificial Intelligence: Implications for Technology, Cyber Security, and Operational Resilience](https://www.osfi-bsif.gc.ca/en/risks/technology-cyber-risk-management/technology-risk-bulletin/generative-agentic-artificial-intelligence-implications-technology-cyber-security-operational). July 2026. Bulletin outlining sound practices that institutions can consider.
10. Office of the Superintendent of Financial Institutions (Canada). [Guideline B-13 Technology and Cyber Risk Management](https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/technology-cyber-risk-management). Final guideline, 31 July 2022. A general technology guideline, not specific to AI.
11. Monetary Authority of Singapore. [Guidelines on Artificial Intelligence Risk Management](https://www.mas.gov.sg/-/media/mas-media-library/regulation/guidelines/bd/guidelines-on-artificial-intelligence-risk-management-for-financial-institutions/guidelines-on-artificial-intelligence-risk-management.pdf). Final, 7 October 2026. Supervisory expectations; they take effect on 7 October 2027; FIs may meet Sections 5 and 6 by 7 October 2028 (paragraph 1.8).
