# FINOS Multi-Agent Reference Architecture — CALM Model & Atomized Controls

This directory provides the machine-readable **[CALM (Common Architecture Language Model)](https://github.com/finos/architecture-as-code)** representation of the [FINOS Multi-Agent Reference Architecture](../ra/ma_ref_arch_jan_2026.md) and its companion [Threat Model (`tm_ma_ref_arch_apr_2026.md`)](../tm/tm_ma_ref_arch_apr_2026.md), together with atomized CALM JSON Schema 2020-12 control requirements for the core agentic mitigations in the [FINOS AI Governance Framework (AIGF)](https://github.com/finos/ai-governance-framework) (`MI-18`, `MI-19`, `MI-20`, `MI-21`).

---

## Contents

| Path | Description |
|---|---|
| [`multi_agent_reference_architecture.calm.json`](./multi_agent_reference_architecture.calm.json) | Canonical CALM v1.2 architecture modeling all 8 layers, 26 nodes, 22 zero-trust relationships, 36 Threat Model controls (`C1`–`C36`), all 58 threats (`T-UIL-01`..`T-XL-04`), and 5 atomized AIGF control links |
| [`controls/requirements/`](./controls/requirements/) | Atomized CALM JSON Schema 2020-12 control requirement schemas (`FINOS-PREV-018-001`, `FINOS-PREV-018-002`, `FINOS-PREV-019-001`, `FINOS-DET-020-001`, `FINOS-AUD-021-001`) |
| [`controls/configurations/`](./controls/configurations/) | Reference compliant control configurations validated against each `.requirement.json` schema |
| [`validate_multi_agent_calm.py`](./validate_multi_agent_calm.py) | Zero-dependency validator CLI enforcing CALM structural integrity, zero-trust gateway choke points, 100% `C1`–`C36` / 58-threat parity, and a 14-scenario adversarial self-test (`--self-test`) |

---

## 1. Architectural Layers Modeled in CALM

Every layer and component from [`ma_ref_arch_jan_2026.md`](../ra/ma_ref_arch_jan_2026.md) is represented as a typed CALM node with explicit zero-trust relationship boundaries:

1. **User Interaction Layer**: `user-actor`, `application-surface`
2. **Agent Gateway Layer**: `agent-registry` (storing signed [FSI Agent Cards](../../agent_card/README.md)), `agent-gateway`, `agent-gateway-guardrails`
3. **Agent Layer**: `supervisor-agent`, `worker-agent-pool`, `unified-agent-runtime`, `secure-execution-sandbox`, `workspace-filesystem`, `adaptive-learning-component`, `mcp-client-bridge`, `short-term-memory`, `long-term-memory`
4. **Knowledge Layer**: `source-bases`, `vector-db`
5. **LLM Layer**: `model-registry`, `llm-gateway`, `llm-guardrails`
6. **MCP Layer**: `mcp-server-registry`, `mcp-gateway`, `mcp-guardrails`
7. **Evaluation Layer**: `feedback-engine`, `human-supervision-gate`, `runtime-protection-circuit-breaker`
8. **Observability Layer**: `observability-telemetry-hub` (WORM logs, signed trace spans, metrics, events, IETF SCITT `RFC 9162` decision receipts, anomaly detection, and correlation engine)

### Zero-Trust Choke-Point Invariants Enforced

- **No Agent Gateway Bypass (`T-AGL-02`)**: `application-surface` connects exclusively to `agent-gateway` (`mTLS-SPIFFE-A2A`), never directly to `supervisor-agent`, `worker-agent-pool`, or `unified-agent-runtime`.
- **No MCP Gateway Bypass (`T-MCP-03`)**: `mcp-client-bridge` connects exclusively to `mcp-gateway` (`mTLS-SPIFFE-MCP`), never bypassing `mcp-guardrails` or `mcp-server-registry`.
- **No LLM Gateway Bypass (`T-LLM-05`)**: `unified-agent-runtime` routes model inference exclusively through `llm-gateway` (`mTLS-HTTPS`).

---

## 2. Atomized AIGF Agentic Controls (`MI-18` – `MI-21`)

| Control ID | AIGF Mitigation | Title | Key Enforced Invariants |
|---|---|---|---|
| `FINOS-PREV-018-001` | `MI-18` (Agent Authority Least Privilege) | Commitment-Time Mandate Scope and Freshness Verification | Verifies mandate scope, value ceiling, and revocation freshness (`<= 300s`) at the point of commitment; enforces `hold-and-reconcile` or `fail-closed-escalate` on uncertain prior outcomes to prevent duplicate settlement |
| `FINOS-PREV-018-002` | `MI-18` (Agent Authority Least Privilege) | Atomic Shared-Limit Reservation and Monotonic Delegation Attenuation | Enforces two-phase atomic limit reservation across concurrent agents, strict-subset scope/budget attenuation (`max-delegation-depth <= 5`), and cryptographic cross-institutional mandate verification |
| `FINOS-PREV-019-001` | `MI-19` (Tool Chain Validation & Sanitization) | Ensuring Appropriate Authorization Level | Enforces `min(user,agent)` pre-execution authorization boundaries with unique decision inputs (`user-id`, `agent-id`, `transaction-id`, `requested-tool`, `requested-action`) |
| `FINOS-DET-020-001` | `MI-20` (Real-Time Monitoring & Circuit Breakers) | Deterministic Runtime and Collective-Exposure Circuit Breakers (`ST-01..ST-05`) | Enforces 5 mandatory triggers including `ST-05-collective-systemic-exposure-breach` across concurrent agent fleets, deterministic rollback of uncommitted reservations, and dual-control human reset (`auto-reset-permitted: false`) |
| `FINOS-AUD-021-001` | `MI-21` (Agent Decision Audit & Explainability) | Independently Verifiable `COSE_Sign1` and IETF SCITT (`RFC 9162`) Decision Receipts | Emits append-only cryptographic audit receipts binding `mandate-id`, `policy-digest`, `inputs-hash`, `execution-environment-attestation-digest`, `decision-verdict`, and `monotonic-sequence-number` with `>= 2555` days (7-year) retention |

---

## 3. Open Source Policy Configuration vs. Hardware-Attested Execution Verification

The CALM schemas and validator in this directory verify **architectural topology and declared control conformance** in CI/CD. In regulated financial institutions and Digital Financial Market Infrastructures (`D-FMI`), static configuration validation pairs with runtime cryptographic enforcement:

- **Open Cryptographic Audit Receipts**: **IETF SCITT (`RFC 9162`)** / `COSE_Sign1` transparency logs provide vendor-neutral, offline-verifiable inclusion proofs for every agent mandate evaluation and tool invocation (`FINOS-AUD-021-001`).
- **Hardware-Attested Execution & Non-Custodial D-FMI Verification**: Institutional clearing and execution platforms bind CALM control evaluations, two-phase atomic mandate reservations (`FINOS-PREV-018-002`), and collective-exposure circuit breakers (`FINOS-DET-020-001`) directly to hardware-attested isolated execution environments and IETF SCITT (`RFC 9162`) audit receipts.

---

## 4. Running the Validator & Adversarial Self-Test Battery

The validator requires **Python 3.8+** with **zero third-party package dependencies**:

```bash
python3 Library/reference_architecture/agentic_ai/multi_agent/calm/validate_multi_agent_calm.py --self-test
```
