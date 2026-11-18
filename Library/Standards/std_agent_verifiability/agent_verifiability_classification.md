# Agent Verifiability Classification

## Purpose

This document defines a classification for the strength of evidence available to prove what an AI agent did, when, under whose authorisation, and that the record itself can be trusted. It establishes four verifiability tiers (V0 to V3) and maps them against the agent autonomy levels (A0 to A4). Verifiability is this standard's own term for the strength of the evidence available to confirm, after the fact, what an agent did (compare verification in ISO/IEC 22989:2022, 3.5.17: "confirmation, through the provision of objective evidence, that specified requirements have been fulfilled"). V0 to V3 and their names are this standard's own labels. FSI in the example columns means the financial services industry.

Verifiability answers a question distinct from the other three standards in this series. Autonomy asks how independently the agent decides ([Agent Autonomy Levels](../std_agent_autonomy/agent_autonomy_levels.md)). Access asks what the agent can reach ([Agent Read/Write Access Classification](../std_agent_read_write_access/agent_read_write_access_classification.md)). Reversibility asks whether, and how fully, the outcome can be undone if the agent is wrong ([Agent Action Reversibility Classification](../std_agent_reversibility/agent_action_reversibility_classification.md)). Verifiability asks whether, after the fact, an auditor, regulator, or investigator can establish what actually happened, independent of what the agent's own operator claims. An agent can be low-autonomy, read-only, and taking fully reversible actions, and still be unauditable if nothing ties a specific action to a specific agent identity at a specific time. Verifiability is the property that makes the other three classifications checkable rather than merely asserted.

This is consistent with how the NIST National Cybersecurity Center of Excellence (NCCoE) draft concept paper lists identification, authorisation, access delegation, and logging and transparency as focus areas [1].

The classification is intended for use during architecture review, audit and compliance design, and incident investigation readiness assessment for AI agent deployments.

---

## Verifiability Tiers

| Tier | Name | Definition | Evidentiary Characteristics | FSI Examples |
|:---|:---|:---|:---|:---|
| **V0** | Unverifiable | No record exists that binds a specific action to a specific agent identity, timestamp, and set of inputs/outputs. If a dispute or incident occurs, there is no way to reconstruct what happened. | No logging, or logging that does not capture a unique agent identity distinct from a shared service account or human user. | An early-stage prototype agent invoked through a shared API key with no per-agent logging, where actions cannot be distinguished from other automated processes using the same credential. |
| **V1** | Logged | Actions are recorded with agent identity, timestamp, inputs, and outputs, but the log is mutable, stored in a general-purpose application log, and not cryptographically or structurally protected against alteration after the fact. | Standard application logging. A record exists, but its integrity depends on trusting whoever has write access to the log store. | A tool-calling agent whose invocations are written to a standard database table that an administrator could edit without detection. |
| **V2** | Tamper-Evident | Logs are tamper-evident (e.g., append-only storage, hash-chained records) and bound to a verifiable agent identity distinct from any human user or shared credential. A reviewer can reconstruct, after the fact, what happened, when, and under whose authorisation, and can detect if the record has been altered. | Append-only or hash-chained audit storage; unique agent identity; retrospective reconstruction is possible and alteration is detectable, but verification happens after the action, not before it is permitted to proceed. | A workflow agent whose every action is written to a hash-chained log, allowing a post-incident investigator to confirm the record has not been altered. |
| **V3** | Attested | Beyond tamper-evident logging, the system can demonstrate, before the action becomes binding, that the required authority, policy, and evidence conditions were satisfied, and produces a non-repudiable evidence chain independently verifiable by a third party without relying on the operator's assertion. | Cryptographically signed, per-action attestations (e.g., digital signatures providing non-repudiation, consistent with the description of non-repudiation in FIPS 186-5 [2]); pre-action proof of authorisation rather than only post-action logging; verification does not depend on trusting the system that produced the record. | A self-directing agent whose every irreversible or administrative action produces a signed attestation binding the action, the policy basis, the authorising identity, and a hash of the prior attestation, verifiable independently by a regulator or auditor without access to the operator's internal systems. |

---

## Autonomy Level and Required Verifiability

Unlike access and reversibility, which are evaluated per action and therefore justify a two-dimensional matrix crossing autonomy against the action's own classification, verifiability is a property of the deployment's evidentiary infrastructure: once an agent's identity and audit architecture is built to a given tier, every action it takes inherits that evidentiary strength. The table below therefore maps autonomy level directly to the minimum required verifiability tier. Verifiability tier is a property of the deployment, but a deployment that permits any action classified AC3 or R3 must provide V3 evidence for those actions; access level belongs to the credential, as the Read/Write Access Classification states. For any R3 or AC3 action the required tier is V3 at every autonomy level, and at A3 for R2 and AC2 actions as well, as stated in the next section.

| Autonomy | Minimum Verifiability Tier | Rationale |
|:---|:---|:---|
| **A0** (No Agency) | V1 at deployment | The human performs the action; the agent's role is limited to producing output. A basic log of the interaction is sufficient for compliance and quality review; there is no agent action to make non-repudiable. V0 is permitted only before deployment, during early prototyping, as the V0 requirements state. |
| **A1** (Tool-Calling) | V1, with V3 required for any action classified AC3 or R3 | Every action already requires explicit human approval before execution. The approval record itself is strong contemporaneous evidence, so standard logging of the approved action is sufficient at this tier, except that an action classified AC3 or R3 requires V3, as stated in the rule that follows this table. |
| **A2** (Workflow) | V2, with V3 required for any action classified AC3 or R3 | The agent executes multiple steps without per-step approval. Tamper-evident logging and verifiable agent identity are required so that a checkpoint failure or downstream dispute can be reconstructed with confidence the record has not been altered. An action classified AC3 or R3 still requires V3, as stated in the rule that follows this table. |
| **A3** (Goal-Directed) | V2, with V3 required for any R2, R3, AC2 or AC3 action taken | The agent decomposes goals and coordinates tool and agent use with only milestone-level human review. Routine actions require V2; any action that is also partially or fully irreversible (R2 or R3) or a scoped or full write (AC2 or AC3) requires V3, matching the escalated controls the Access and Reversibility Classifications already impose at A3 for such actions, which are Staged Commit with Review Window and Escalate with Dual Approval. |
| **A4** (Self-Directing) | V3 | The human is out of the loop during normal operation and is alerted only on exception. Verifiability at this autonomy level cannot rely on retrospective trust in the operator's logs; it must be independently provable, consistent with the tamper-proof, signed record requirement already specified for A4 in [Agent Autonomy Levels](../std_agent_autonomy/agent_autonomy_levels.md). |

---

## Combining Verifiability with Autonomy, Access, and Reversibility

Autonomy, access, reversibility, and verifiability are four independent axes evaluated together for any agent action. The first three determine how much control an action requires; verifiability determines whether that control, once applied, can actually be demonstrated to have occurred. A staged commit with a review window (required for an A3 agent taking an R2 or AC2 action) is only a meaningful control if the staging, the review, and the reviewer's identity are themselves recorded at a tier strong enough to survive a subsequent dispute about whether the review actually happened.

As a general rule, **verifiability tier must be sufficient to independently prove compliance with whatever the access and reversibility standards require for the same action.** An AC3 (Full Write / Administrative) action's design requirements already call for a pre-action approval record; that record must be at least tamper-evident (V2) to be trustworthy and, because AC3 and R3 actions also need pre-action proof, V3 is the mandatory tier for them, as stated below. The pre-action verification check required for R3 (Irreversible) actions in the Reversibility Classification is the same check that V3 provides evidence for: proof that all required conditions were satisfied before the action became binding. **V3 is therefore a mandatory prerequisite, not an independent option, for any action classified AC3 or R3, regardless of the autonomy level at which it occurs.** At A3 the same applies to R2 and AC2 actions, as the autonomy table states.

---

## Determining the Verifiability Tier

The verifiability tier of a deployment is a property of its identity, logging, and attestation infrastructure, assessed independently of any single action:

| Factor | Questions |
|:---|:---|
| **Identity binding** | Does every action carry a unique agent identity distinct from any human user or shared service credential? If no, classify as V0. |
| **Record existence** | Is there a log capturing the action, its inputs and outputs, the agent identity, and a timestamp? If yes, but the log is mutable and not structurally protected, classify as V1. |
| **Tamper-evidence** | Is the log append-only, hash-chained, or otherwise structured so that alteration or deletion is detectable? If yes, and the unique agent identity is independently verifiable, classify as V2. |
| **Pre-action proof** | Can the system demonstrate, before the action executes, that the required authority and policy conditions are satisfied, rather than only recording that the action occurred afterward? |
| **Independent verifiability** | Can a third party (auditor, regulator, counterparty) verify the evidence chain's integrity without depending on the operator's own systems or assertions, for example via a cryptographic signature? If both pre-action proof and independent verifiability are present, classify as V3. |

---

## Design Requirements by Verifiability Tier

### V0: Unverifiable

- Not an acceptable end state for any agent that performs actions (A1 and above). An A0 agent producing output only may operate at V0 during early prototyping, but this must not be the deployed state.
- If discovered during architecture review, the finding is a control gap requiring remediation to at least V1 before deployment.

### V1: Logged

- Every action must record: agent identity, timestamp, inputs, outputs, and (for A1) the identity of the human approver.
- Agent identity must be unique per agent instance, not a shared API key or service account, consistent with the identity requirements referenced in the Read/Write Access Classification [3].
- Logs must be retained per the organisation's records management policy and be available for compliance and quality review.

### V2: Tamper-Evident

- All V1 requirements apply.
- Log storage must be append-only or hash-chained such that any alteration or deletion after the fact is detectable (see the glossary entry for hash chain).
- Agent identity must be cryptographically or structurally bound to the log entries it produces, not merely asserted in a log field that any writer could set.
- The organisation must be able to reconstruct, for any given action, the full sequence of events leading to it, sufficient to support post-incident investigation. NIST AI RMF MEASURE 2.8 calls for examining and documenting risks associated with transparency and accountability, and GOVERN 2.1 for documented, clear roles and responsibilities [4].
- Tamper-evident logging at this tier can support the automatic event-recording capability that Article 12 requires of high-risk AI systems, provided the logging captures events relevant to risk identification, post-market monitoring, and operational monitoring as specified in Article 12(2) [5]. Conformity depends on the system's legal classification and is outside the scope of this document.

### V3: Attested

- All V2 requirements apply.
- Each action classified R3 (Irreversible) or AC3 (Full Write / Administrative) must produce a signed, per-action attestation binding the action, the policy basis under which it was authorised, the authorising identity, and a reference to the prior attestation in the chain, consistent with the description of non-repudiation in FIPS 186-5 [2].
- Each action classified R2 or AC2 and taken by an A3 agent must also produce a signed, per-action attestation as described above.
- The attestation must be produced and verifiable independent of the agent's own operator: a party without access to the operator's internal systems must be able to validate the signature chain and confirm it has not been altered.
- The attestation must satisfy the pre-action verification requirement already specified for R3 actions in the Reversibility Classification: proof that authority, policy, evidence, and control conditions were satisfied before the action became binding, not only a record that it occurred.
- Loss or compromise of the signing infrastructure itself must be treated as a critical incident, since it invalidates the non-repudiation property of every attestation it has produced.

---

## Related Frameworks and Sources

This section is informational and is not legal, regulatory or compliance advice. References to laws, standards and supervisory guidance describe related provisions only and do not establish that a system meets any legal or regulatory obligation. Which obligations apply, for example whether a system is high-risk under Regulation (EU) 2024/1689 (the EU AI Act), as amended by Regulation (EU) 2026/1744, is a determination for the adopting organisation and its legal advisers. Items marked as preprints, drafts or vendor or community specifications are not standards and have no regulatory standing.

The following frameworks, standards and publications address concerns related to this classification. This classification has not been assessed for conformity with any of them, and citing a source does not mean the source requires or endorses it.

| Framework | Relevant Provisions |
|:---|:---|
| **EU AI Act** (Regulation (EU) 2024/1689, as amended by Regulation (EU) 2026/1744) | Article 12(1) says that high-risk AI systems "shall technically allow for the automatic recording of events (logs) over the lifetime of the system." Article 12(2) says logging capabilities are to enable traceability appropriate to the intended purpose of the system [5][8]. Article 19(1) addresses related concerns for providers of high-risk AI systems: it says "the logs shall be kept for a period appropriate to the intended purpose of the high-risk AI system, of at least six months". For providers that are financial institutions, Article 19(2) says they "shall maintain the logs automatically generated by their high-risk AI systems as part of the documentation kept under the relevant financial services law." Article 26(6), second subparagraph, says that deployers that are financial institutions "shall maintain the logs as part of the documentation kept pursuant to the relevant Union financial service law." Under Regulation (EU) 2026/1744, Chapter III Sections 1 to 3 (which include these articles) apply to AI systems classified as high-risk pursuant to Article 6(2) and Annex III from 2 December 2027 and to those classified pursuant to Article 6(1) and Annex I from 2 August 2028 (Article 113, third paragraph, point (c), as amended). [5][8] |
| **NIST AI RMF 1.0** (voluntary framework) | MEASURE 2.8 calls for examining and documenting risks associated with transparency and accountability, and GOVERN 2.1 for documented, clear roles and responsibilities [4]. |
| **NIST NCCoE, Agent Identity and Authorization** (draft concept paper, *Accelerating the Adoption of Software and Artificial Intelligence Agent Identity and Authorization*, Feb. 2026) | Lists identification, authorisation, access delegation, and logging and transparency as focus areas for agent identity and authorisation [1]. |
| **IMDA Model AI Governance Framework for Agentic AI (version 1.5)** | The IMDA model framework recommends that each agent have a unique, cryptographically verifiable identity, and that the capacity in which it acts be recorded for auditability. It also addresses related concerns: it says organisations "should continuously monitor and log agent behaviour post-deployment", that "Logging and tracing each step of an agent workflow and agent-to-agent interactions help to identify points of failure." and "Ensure log immutability: Maintain complete audit trails by ensuring that problematic agent trajectories and failures cannot be deleted, preserving them for analysis and compliance purposes." (section 2.3.3). [6] |
| **OSFI Guideline E-23, Model Risk Management** (final, 11 September 2025; effective 1 May 2027) | OSFI Guideline E-23 addresses related concerns. Principle 3.6 says its decommissioning process includes "Retaining the retired model and documentation for a set period as a benchmark or fallback." Principle 3.5 says deployment should involve "clearly documented procedures that outline deployment steps, stakeholder responsibilities, approval hierarchies, change control, monitoring frameworks and exception handling including overlays". [9] |
| **OSFI Technology Risk Bulletin on generative and agentic AI** (July 2026; bulletin outlining sound practices that institutions can consider) | OSFI's July 2026 Technology Risk Bulletin addresses related concerns. It lists the practice "log and review agent activity and tool usage along with periodic access recertification to improve detection of anomalies and maintain ongoing access integrity" (Control AI agent autonomy and access) and the practice "ensure human oversight with accountability for material or high-impact decisions, with clear and auditable documentation to demonstrate how AI outputs inform analysis and final outcomes" (Maintain information and decision integrity). [10] |
| **OSFI Guideline B-13, Technology and Cyber Risk Management** (final, 31 July 2022; a general technology guideline, not specific to AI) | OSFI Guideline B-13 addresses related concerns for technology assets generally and does not mention AI agents: section 3.3.1 says "FRFIs should ensure continuous security logging for technology assets and different layers of defence tools." [11] |
| **MAS Guidelines on Artificial Intelligence Risk Management** (final, 7 October 2026; supervisory expectations that take effect on 7 October 2027; FIs may meet Sections 5 and 6 by 7 October 2028 (paragraph 1.8)) | The Monetary Authority of Singapore Guidelines address related concerns. Paragraph 5.9(d) refers to "processes to document logs and other records generated through development, deployment, operation, monitoring and incident management activities". Paragraph 5.23(a) says "reasoning processes, actions taken, tools used should also be monitored." Paragraph 5.23(d) says "Enhanced documentation for Generative AI or AI agents could also be considered where relevant, such as logging prompts and model responses, together with applicable model versions and reasoning processes used." Paragraph 5.25(b) says version control may "support traceability, auditability, and the ability to roll back to previous versions." [12] |

---

## Summary

| Tier | Name | Can a Dispute Be Resolved? | Required Safeguard |
|:---|:---|:---|:---|
| **V0** | Unverifiable | No | Not acceptable beyond early prototyping; remediate before deployment |
| **V1** | Logged | Only if the log's integrity is not itself in question | Unique agent identity, complete action record, retention per policy |
| **V2** | Tamper-Evident | Yes, retrospectively, with alteration detectable | Tamper-evident storage, cryptographic or structural identity binding, full reconstructability |
| **V3** | Attested | Yes, independently of the operator's own assertions, and provably before the action occurred | Signed per-action attestation, hash-chained evidence, independent third-party verifiability |

---

## Glossary

**Attestation**  
"The issue of a statement, based on a decision, that fulfillment of specified requirements has been demonstrated." Source: [NIST CSRC glossary](https://csrc.nist.gov/glossary/term/attestation), quoting ISO/IEC 17000:2020 as used in the Software Supply Chain Security Guidance (EO 14028). In this standard, a signed attestation is a signed, timestamped record asserting that a specific agent identity performed a specific action under specific authorisation, and that for that action the required authority, policy and evidence conditions were satisfied. It binds the action, the policy basis, the authorising identity and a reference to the prior attestation, so that a third party can verify it without trusting the system that produced it. The V3 tier is named for it: signed per-action attestations are required from V3.

**Hash chain**  
"An append-only data structure where data is bundled into data blocks that include a hash of the previous data block's data within the newest data block. This data structure provides evidence of tampering because any modification to a data block will change the hash digest recorded by the following data block." Source: [NIST CSRC glossary](https://csrc.nist.gov/glossary/term/hash_chain), from NISTIR 8202.

**Non-repudiation**  
In plain terms, the property that prevents a party from credibly denying that they authorised or performed a specific action. The NIST CSRC glossary defines it as "A service that is used to provide assurance of the integrity and origin of data in such a way that the integrity and origin can be verified and validated by a third party as having originated from a specific entity in possession of the private key (i.e., the signatory)." Source: [NIST CSRC glossary](https://csrc.nist.gov/glossary/term/non_repudiation), from FIPS 186-5 [2]. It is typically achieved through digital signatures, consistent with FIPS 186-5 [2]. This is a technical property. It does not by itself establish legal non-repudiation (RFC 4949 [7]).

**Runtime truth**  
The actual, verifiable record of what an agent did inside a connected system, as distinct from a static configuration or policy document describing what it was permitted to do. This is this standard's own term (also referred to as the runtime record); it is not taken from NIST or from the NCCoE draft concept paper.

**Tamper-evident**  
"A process which makes alterations to the data easily detectable." Source: [NIST CSRC glossary](https://csrc.nist.gov/glossary/term/tamper_evident), from NISTIR 8202. Distinguished from tamper-resistant, defined in the same source as "A process which makes alterations to the data difficult (hard to perform), costly (expensive to perform), or both."

**Tamper-proof**  
In this standard, a property of a record store such that alteration is prevented entirely, which is stronger than tamper-evident. The Agent Autonomy Levels standard requires tamper-proof, signed records at A4.

---

## References

1. Booth, H., Fisher, W., Galluzzo, R., Roberts, J. (NIST, National Cybersecurity Center of Excellence). [*Accelerating the Adoption of Software and Artificial Intelligence Agent Identity and Authorization*](https://csrc.nist.gov/pubs/other/2026/02/05/accelerating-the-adoption-of-software-and-ai-agent/ipd), draft concept paper. 5 February 2026.
2. National Institute of Standards and Technology. [*Digital Signature Standard (DSS)*, FIPS PUB 186-5](https://csrc.nist.gov/pubs/fips/186-5/final). February 2023.
3. FINOS AI Reference Architecture Library. [Agent Read/Write Access Classification](../std_agent_read_write_access/agent_read_write_access_classification.md).
4. National Institute of Standards and Technology. [*AI Risk Management Framework (AI RMF 1.0)*, NIST AI 100-1](https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf), MEASURE 2.8 and GOVERN 2.1. January 2023.
5. European Parliament and Council. Regulation (EU) 2024/1689 (the EU AI Act), as amended by Regulation (EU) 2026/1744. [Articles 12, 19 and 26](https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng). Official Journal L, 12 July 2024.
6. Infocomm Media Development Authority. [*Model AI Governance Framework for Agentic AI*, version 1.5](https://www.imda.gov.sg/-/media/imda/files/about/emerging-tech-and-research/artificial-intelligence/mgf-for-agentic-ai.pdf). Singapore. Version 1.5, published 20 May 2026 (updated 5 June 2026).
7. Shirey, R. [Internet Security Glossary, Version 2](https://www.rfc-editor.org/info/rfc4949), RFC 4949. August 2007.
8. European Union. [Regulation (EU) 2026/1744 of 8 July 2026 amending Regulations (EU) 2024/1689, (EU) 2018/1139 and (EU) 2023/1230 as regards the simplification of the implementation of harmonised rules on artificial intelligence (Digital Omnibus on AI)](https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng). Official Journal L, 2026/1744, 24 July 2026. In force; it entered into force on the third day following its publication (27 July 2026).
9. Office of the Superintendent of Financial Institutions (Canada). [Guideline E-23 Model Risk Management (2027)](https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/guideline-e-23-model-risk-management-2027). Final guideline, 11 September 2025; effective 1 May 2027.
10. Office of the Superintendent of Financial Institutions (Canada). [Technology Risk Bulletin, Generative and Agentic Artificial Intelligence: Implications for Technology, Cyber Security, and Operational Resilience](https://www.osfi-bsif.gc.ca/en/risks/technology-cyber-risk-management/technology-risk-bulletin/generative-agentic-artificial-intelligence-implications-technology-cyber-security-operational). July 2026. Bulletin outlining sound practices that institutions can consider.
11. Office of the Superintendent of Financial Institutions (Canada). [Guideline B-13 Technology and Cyber Risk Management](https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/technology-cyber-risk-management). Final guideline, 31 July 2022. A general technology guideline, not specific to AI.
12. Monetary Authority of Singapore. [Guidelines on Artificial Intelligence Risk Management](https://www.mas.gov.sg/-/media/mas-media-library/regulation/guidelines/bd/guidelines-on-artificial-intelligence-risk-management-for-financial-institutions/guidelines-on-artificial-intelligence-risk-management.pdf). Final, 7 October 2026. Supervisory expectations; they take effect on 7 October 2027; FIs may meet Sections 5 and 6 by 7 October 2028 (paragraph 1.8).
