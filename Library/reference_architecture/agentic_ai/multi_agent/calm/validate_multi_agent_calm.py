#!/usr/bin/env python3
"""
FINOS Multi-Agent Reference Architecture — CALM & Threat-Model Validator
Copyright (c) Contributors to the FINOS AI Reference Architecture Library.
SPDX-License-Identifier: Apache-2.0

Zero-dependency validator for:
  1. `multi_agent_reference_architecture.calm.json`:
     - Verifies all 8 architectural layers are represented
     - Verifies node uniqueness, interface definitions, and relationship referential integrity
     - Enforces zero-trust choke-point invariants (no Agent Gateway, MCP Gateway, or LLM Gateway bypass)
     - Verifies 100% coverage of all 36 Threat Model Controls (C1..C36) and all 58 Threats
       (T-UIL-01..T-XL-04) against `../tm/tm_ma_ref_arch_apr_2026.md`
  2. `controls/requirements/*.requirement.json` & `controls/configurations/*.json`:
     - Validates JSON Schema 2020-12 structure, canonical $id, HTTPS CALM meta-schema $ref,
       `additionalProperties: false`, `uniqueItems: true`, and configuration conformance
  3. `--self-test`:
     - Runs 14 adversarial red-team mutation scenarios proving fail-closed detection of
       gateway bypasses, missing threat controls, duplicate array bypasses, stale mandates,
       collective exposure omissions, and unattested audit receipts.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

CALM_DIR = Path(__file__).resolve().parent
CALM_ARCH_PATH = CALM_DIR / "multi_agent_reference_architecture.calm.json"
THREAT_MODEL_MD_PATH = CALM_DIR.parent / "tm" / "tm_ma_ref_arch_apr_2026.md"
CONTROLS_DIR = CALM_DIR / "controls"

CANONICAL_ID_PREFIX = (
    "https://finos.github.io/ai-reference-architecture-library/"
    "Library/reference_architecture/agentic_ai/multi_agent/calm/controls/requirements"
)
CALM_META_REF = "https://calm.finos.org/controls/2025-03/meta/control-requirement.json"
JSON_SCHEMA_2020_12 = "https://json-schema.org/draft/2020-12/schema"

EXPECTED_LAYERS = [
    "User Interaction Layer",
    "Agent Gateway Layer",
    "Agent Layer",
    "Knowledge Layer",
    "LLM Layer",
    "MCP Layer",
    "Evaluation Layer",
    "Observability Layer",
]


def is_valid_https_uri(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return parsed.scheme == "https" and bool(parsed.netloc)
    except Exception:
        return False


def validate_json_value(instance: object, schema: dict, path: str = "$") -> list[str]:
    """Deterministic zero-dependency JSON Schema 2020-12 subset validator."""
    errors: list[str] = []

    if "allOf" in schema:
        for idx, subschema in enumerate(schema["allOf"]):
            if "$ref" in subschema:
                continue
            errors.extend(validate_json_value(instance, subschema, f"{path}.allOf[{idx}]"))

    expected_type = schema.get("type")
    if expected_type == "object":
        if not isinstance(instance, dict):
            return [f"{path}: expected object, got {type(instance).__name__}"]
        for req_key in schema.get("required", []):
            if req_key not in instance:
                errors.append(f"{path}: missing required property '{req_key}'")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False and props:
            for key in instance:
                if key == "$schema":
                    continue
                if key not in props:
                    errors.append(f"{path}: unexpected additional property '{key}'")
        for key, val in instance.items():
            if key == "$schema":
                continue
            if key in props:
                errors.extend(validate_json_value(val, props[key], f"{path}.{key}"))

    elif expected_type == "array":
        if not isinstance(instance, list):
            return [f"{path}: expected array, got {type(instance).__name__}"]
        min_items = schema.get("minItems")
        if min_items is not None and len(instance) < min_items:
            errors.append(f"{path}: array length {len(instance)} is less than minItems {min_items}")
        if schema.get("uniqueItems") is True:
            serialized = [json.dumps(item, sort_keys=True) for item in instance]
            if len(serialized) != len(set(serialized)):
                errors.append(f"{path}: array contains duplicate items (violates uniqueItems: true)")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for idx, item in enumerate(instance):
                errors.extend(validate_json_value(item, item_schema, f"{path}[{idx}]"))

    elif expected_type == "string":
        if not isinstance(instance, str):
            return [f"{path}: expected string, got {type(instance).__name__}"]
        if schema.get("format") == "uri" and not is_valid_https_uri(instance):
            errors.append(f"{path}: value '{instance}' is not a valid HTTPS URI")

    elif expected_type == "integer":
        if isinstance(instance, bool) or not isinstance(instance, int):
            return [f"{path}: expected integer, got {type(instance).__name__}"]
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: integer {instance} is less than minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: integer {instance} exceeds maximum {schema['maximum']}")

    elif expected_type == "boolean":
        if not isinstance(instance, bool):
            return [f"{path}: expected boolean, got {type(instance).__name__}"]

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}, got {instance!r}")

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: value {instance!r} not in enum {schema['enum']}")

    return errors


def validate_requirement_schema_structure(schema: dict, req_filename: str) -> list[str]:
    errors: list[str] = []
    if schema.get("$schema") != JSON_SCHEMA_2020_12:
        errors.append(
            f"{req_filename}: $schema must be '{JSON_SCHEMA_2020_12}', got {schema.get('$schema')!r}"
        )

    expected_id = f"{CANONICAL_ID_PREFIX}/{req_filename}"
    if schema.get("$id") != expected_id:
        errors.append(
            f"{req_filename}: $id mismatch. Expected '{expected_id}', got {schema.get('$id')!r}"
        )

    all_of = schema.get("allOf")
    if not isinstance(all_of, list) or len(all_of) < 1:
        errors.append(f"{req_filename}: must contain an 'allOf' list referencing CALM meta-schema")
        return errors

    ref = all_of[0].get("$ref")
    if ref != CALM_META_REF:
        errors.append(
            f"{req_filename}: allOf[0].$ref must be '{CALM_META_REF}' (HTTPS required), got {ref!r}"
        )

    if schema.get("additionalProperties") is not False:
        errors.append(f"{req_filename}: top-level schema must set 'additionalProperties': false")

    props = schema.get("properties", {})
    for req_field in ("control-id", "name", "description"):
        if req_field not in props or "const" not in props[req_field]:
            errors.append(f"{req_filename}: properties.{req_field} must be pinned via 'const'")

    for key, prop_schema in props.items():
        if isinstance(prop_schema, dict) and prop_schema.get("type") == "array":
            items = prop_schema.get("items", {})
            if prop_schema.get("minItems", 0) > 1 and "enum" in items:
                if prop_schema.get("uniqueItems") is not True:
                    errors.append(
                        f"{req_filename}: properties.{key} has minItems > 1 over an enum and must set 'uniqueItems': true"
                    )

    return errors


def extract_markdown_threats_and_controls(md_text: str) -> tuple[set[str], dict[str, set[str]]]:
    """Parses C1..C36 and Threat -> Controls mappings directly from tm_ma_ref_arch_apr_2026.md."""
    controls_defined: set[str] = set()
    threat_controls: dict[str, set[str]] = {}

    for line in md_text.splitlines():
        ctrl_match = re.match(r"^\|\s*(C\d+)\s*\|", line)
        if ctrl_match:
            controls_defined.add(ctrl_match.group(1))
            continue

        threat_match = re.match(r"^\|\s*(T-[A-Z]+-\d+)\s*\|.*\|\s*([C0-9,\s]+)\s*\|\s*$", line)
        if threat_match:
            tid = threat_match.group(1)
            ctrls = {c.strip() for c in threat_match.group(2).split(",") if c.strip()}
            threat_controls[tid] = ctrls

    return controls_defined, threat_controls


def validate_calm_architecture(
    arch: dict, md_controls: set[str], md_threats: dict[str, set[str]]
) -> list[str]:
    errors: list[str] = []

    if arch.get("$schema") != "https://calm.finos.org/release/1.2/meta/calm.json":
        errors.append("CALM architecture must declare $schema 'https://calm.finos.org/release/1.2/meta/calm.json'")

    nodes = arch.get("nodes", [])
    if not isinstance(nodes, list) or len(nodes) < 20:
        errors.append("CALM architecture must define at least 20 architectural nodes")
        return errors

    node_ids: set[str] = set()
    layers_present: set[str] = set()
    interface_owner: dict[str, str] = {}
    controls_declared = arch.get("controls", {})

    for node in nodes:
        nid = node.get("unique-id")
        if not nid:
            errors.append("Node missing 'unique-id'")
            continue
        if nid in node_ids:
            errors.append(f"Duplicate node unique-id '{nid}'")
        node_ids.add(nid)

        layer = node.get("layer")
        if layer:
            layers_present.add(layer)

        for iface in node.get("interfaces", []):
            iid = iface.get("unique-id")
            if iid:
                interface_owner[iid] = nid

        for cid in node.get("controls", []):
            if cid not in controls_declared:
                errors.append(f"Node '{nid}' references undeclared control '{cid}'")

    for expected_layer in EXPECTED_LAYERS:
        if expected_layer not in layers_present:
            errors.append(f"Missing architectural layer '{expected_layer}' in CALM nodes")

    relationships = arch.get("relationships", [])
    rel_ids: set[str] = set()
    connected_nodes: set[str] = set()

    # Track direct connections to enforce zero-trust gateway choke points
    direct_edges: list[tuple[str, str, str]] = []

    for rel in relationships:
        rid = rel.get("unique-id")
        if not rid:
            errors.append("Relationship missing 'unique-id'")
            continue
        if rid in rel_ids:
            errors.append(f"Duplicate relationship unique-id '{rid}'")
        rel_ids.add(rid)

        rtype = rel.get("relationship-type", {})
        if "connects" in rtype:
            conn = rtype["connects"]
            src = conn.get("source", {}).get("node")
            dst_obj = conn.get("destination", {})
            dst = dst_obj.get("node")
            if src not in node_ids:
                errors.append(f"Relationship '{rid}' has unknown source node '{src}'")
            if dst not in node_ids:
                errors.append(f"Relationship '{rid}' has unknown destination node '{dst}'")
            if src and dst:
                connected_nodes.add(src)
                connected_nodes.add(dst)
                direct_edges.append((src, dst, rid))
            for iface_id in dst_obj.get("interfaces", []):
                if iface_id not in interface_owner or interface_owner[iface_id] != dst:
                    errors.append(
                        f"Relationship '{rid}' references interface '{iface_id}' not owned by destination '{dst}'"
                    )
        elif "interacts" in rtype:
            inter = rtype["interacts"]
            actor = inter.get("actor")
            if actor not in node_ids:
                errors.append(f"Relationship '{rid}' has unknown actor '{actor}'")
            else:
                connected_nodes.add(actor)
            for target_node in inter.get("nodes", []):
                if target_node not in node_ids:
                    errors.append(f"Relationship '{rid}' has unknown target node '{target_node}'")
                else:
                    connected_nodes.add(target_node)
                    if actor:
                        direct_edges.append((actor, target_node, rid))
        elif "deployed-in" in rtype:
            dep = rtype["deployed-in"]
            container = dep.get("container")
            if container not in node_ids:
                errors.append(f"Relationship '{rid}' has unknown container '{container}'")
            else:
                connected_nodes.add(container)
            for child in dep.get("nodes", []):
                if child not in node_ids:
                    errors.append(f"Relationship '{rid}' has unknown deployed node '{child}'")
                else:
                    connected_nodes.add(child)
        else:
            errors.append(f"Relationship '{rid}' has unsupported relationship-type")

        for cid in rel.get("controls", []):
            if cid not in controls_declared:
                errors.append(f"Relationship '{rid}' references undeclared control '{cid}'")

    # Zero-Trust Gateway Bypass Checks (T-AGL-02, T-MCP-03, T-LLM-05)
    agent_internal_nodes = {
        "supervisor-agent",
        "worker-agent-pool",
        "unified-agent-runtime",
        "secure-execution-sandbox",
    }
    for src, dst, rid in direct_edges:
        if src in {"user-actor", "application-surface"} and dst in agent_internal_nodes:
            errors.append(
                f"Zero-Trust Violation (T-AGL-02) in '{rid}': '{src}' connects directly to '{dst}' bypassing 'agent-gateway'"
            )
        if src in agent_internal_nodes and dst == "mcp-server-registry":
            errors.append(
                f"Zero-Trust Violation (T-MCP-03) in '{rid}': '{src}' connects directly to 'mcp-server-registry' bypassing 'mcp-gateway'"
            )
        if src in agent_internal_nodes and dst == "model-registry":
            errors.append(
                f"Zero-Trust Violation (T-LLM-05) in '{rid}': '{src}' connects directly to 'model-registry' bypassing 'llm-gateway'"
            )

    orphan_nodes = node_ids - connected_nodes
    if orphan_nodes:
        errors.append(f"Orphan nodes not participating in any relationship: {sorted(orphan_nodes)}")

    # Verify 100% parity with Threat Model C1..C36 and 43 Threats
    for cid in sorted(md_controls):
        if cid not in controls_declared:
            errors.append(f"Missing Threat Model control '{cid}' in CALM controls block")

    calm_threats = {t.get("threat-id"): t for t in arch.get("threat-mappings", [])}
    for tid, expected_ctrls in sorted(md_threats.items()):
        if tid not in calm_threats:
            errors.append(f"Missing Threat Model entry '{tid}' in CALM threat-mappings")
            continue
        actual_ctrls = set(calm_threats[tid].get("controls", []))
        if actual_ctrls != expected_ctrls:
            errors.append(
                f"Threat '{tid}' control mismatch: CALM has {sorted(actual_ctrls)}, threat model requires {sorted(expected_ctrls)}"
            )
        for ac in calm_threats[tid].get("aigf-controls", []):
            if ac not in controls_declared:
                errors.append(f"Threat '{tid}' references undeclared AIGF control '{ac}'")

    return errors


def validate_all() -> tuple[bool, list[str], dict[str, int]]:
    errors: list[str] = []
    stats = {"nodes": 0, "relationships": 0, "controls": 0, "threats": 0, "aigf_schemas": 0}

    if not CALM_ARCH_PATH.is_file():
        return False, [f"Missing {CALM_ARCH_PATH}"], stats
    if not THREAT_MODEL_MD_PATH.is_file():
        return False, [f"Missing {THREAT_MODEL_MD_PATH}"], stats

    arch = json.loads(CALM_ARCH_PATH.read_text(encoding="utf-8"))
    md_text = THREAT_MODEL_MD_PATH.read_text(encoding="utf-8")
    md_controls, md_threats = extract_markdown_threats_and_controls(md_text)

    errors.extend(validate_calm_architecture(arch, md_controls, md_threats))

    stats["nodes"] = len(arch.get("nodes", []))
    stats["relationships"] = len(arch.get("relationships", []))
    stats["controls"] = len(md_controls)
    stats["threats"] = len(md_threats)

    req_dir = CONTROLS_DIR / "requirements"
    cfg_dir = CONTROLS_DIR / "configurations"
    req_files = sorted(req_dir.glob("*.requirement.json"))
    if len(req_files) < 5:
        errors.append(f"Expected >= 5 atomized AIGF requirement schemas, found {len(req_files)}")

    for req_file in req_files:
        stats["aigf_schemas"] += 1
        control_id = req_file.name.replace(".requirement.json", "")
        req_schema = json.loads(req_file.read_text(encoding="utf-8"))
        errors.extend(validate_requirement_schema_structure(req_schema, req_file.name))

        cfg_file = cfg_dir / f"{control_id}.json"
        if not cfg_file.is_file():
            errors.append(f"Missing configuration instance {cfg_file.name}")
            continue
        cfg_instance = json.loads(cfg_file.read_text(encoding="utf-8"))
        if cfg_instance.get("$schema") != req_schema.get("$id"):
            errors.append(
                f"{cfg_file.name}: $schema does not match requirement $id '{req_schema.get('$id')}'"
            )
        errors.extend(validate_json_value(cfg_instance, req_schema, cfg_file.name))

    return len(errors) == 0, errors, stats


def run_self_tests() -> bool:
    print("Running 14 adversarial red-team self-test scenarios...")
    arch = json.loads(CALM_ARCH_PATH.read_text(encoding="utf-8"))
    md_controls, md_threats = extract_markdown_threats_and_controls(
        THREAT_MODEL_MD_PATH.read_text(encoding="utf-8")
    )

    req_18_1 = json.loads(
        (CONTROLS_DIR / "requirements/FINOS-PREV-018-001.requirement.json").read_text(encoding="utf-8")
    )
    cfg_18_1 = json.loads(
        (CONTROLS_DIR / "configurations/FINOS-PREV-018-001.json").read_text(encoding="utf-8")
    )
    req_18_2 = json.loads(
        (CONTROLS_DIR / "requirements/FINOS-PREV-018-002.requirement.json").read_text(encoding="utf-8")
    )
    cfg_18_2 = json.loads(
        (CONTROLS_DIR / "configurations/FINOS-PREV-018-002.json").read_text(encoding="utf-8")
    )
    req_19_1 = json.loads(
        (CONTROLS_DIR / "requirements/FINOS-PREV-019-001.requirement.json").read_text(encoding="utf-8")
    )
    cfg_19_1 = json.loads(
        (CONTROLS_DIR / "configurations/FINOS-PREV-019-001.json").read_text(encoding="utf-8")
    )
    req_20_1 = json.loads(
        (CONTROLS_DIR / "requirements/FINOS-DET-020-001.requirement.json").read_text(encoding="utf-8")
    )
    cfg_20_1 = json.loads(
        (CONTROLS_DIR / "configurations/FINOS-DET-020-001.json").read_text(encoding="utf-8")
    )
    req_21_1 = json.loads(
        (CONTROLS_DIR / "requirements/FINOS-AUD-021-001.requirement.json").read_text(encoding="utf-8")
    )
    cfg_21_1 = json.loads(
        (CONTROLS_DIR / "configurations/FINOS-AUD-021-001.json").read_text(encoding="utf-8")
    )

    scenarios: list[tuple[str, list[str]]] = []

    # 1. Agent Gateway Bypass (T-AGL-02)
    s1 = copy.deepcopy(arch)
    s1["relationships"].append(
        {
            "unique-id": "rel-bypass-agent-gw",
            "description": "Direct bypass from application to supervisor agent",
            "relationship-type": {
                "connects": {
                    "source": {"node": "application-surface"},
                    "destination": {"node": "supervisor-agent"},
                }
            },
            "controls": ["C1"],
        }
    )
    scenarios.append(
        (
            "1. Block direct Application -> Supervisor Agent bypass (T-AGL-02)",
            validate_calm_architecture(s1, md_controls, md_threats),
        )
    )

    # 2. MCP Gateway Bypass (T-MCP-03)
    s2 = copy.deepcopy(arch)
    s2["relationships"].append(
        {
            "unique-id": "rel-bypass-mcp-gw",
            "description": "Direct bypass from runtime to MCP registry",
            "relationship-type": {
                "connects": {
                    "source": {"node": "unified-agent-runtime"},
                    "destination": {"node": "mcp-server-registry"},
                }
            },
            "controls": ["C11"],
        }
    )
    scenarios.append(
        (
            "2. Block direct Agent Runtime -> MCP Registry bypass (T-MCP-03)",
            validate_calm_architecture(s2, md_controls, md_threats),
        )
    )

    # 3. Missing Threat Model Control (e.g. C36 removed)
    s3 = copy.deepcopy(arch)
    del s3["controls"]["C36"]
    scenarios.append(
        (
            "3. Detect removal of mandatory Threat Model control C36 (Signed Agent Card)",
            validate_calm_architecture(s3, md_controls, md_threats),
        )
    )

    # 4. Threat-to-Control mapping drift on T-XL-01 (MNPI Leakage)
    s4 = copy.deepcopy(arch)
    for t in s4["threat-mappings"]:
        if t["threat-id"] == "T-XL-01":
            t["controls"] = ["C8"]
    scenarios.append(
        (
            "4. Detect threat control drift on T-XL-01 (MNPI Leakage Across Agent Boundaries)",
            validate_calm_architecture(s4, md_controls, md_threats),
        )
    )

    # 5. Orphan unreferenced node in CALM architecture
    s5 = copy.deepcopy(arch)
    s5["nodes"].append(
        {
            "unique-id": "shadow-unregistered-agent",
            "node-type": "service",
            "name": "Shadow Agent",
            "layer": "Agent Layer",
            "controls": ["C14"],
        }
    )
    scenarios.append(
        (
            "5. Detect orphan unreferenced shadow node in CALM graph",
            validate_calm_architecture(s5, md_controls, md_threats),
        )
    )

    # 6. Broken $id path in requirement schema
    s6 = copy.deepcopy(req_19_1)
    s6["$id"] = "https://finos.github.io/wrong-path/FINOS-PREV-019-001.json"
    scenarios.append(
        (
            "6. Detect broken $id URI path in CALM requirement schema",
            validate_requirement_schema_structure(s6, "FINOS-PREV-019-001.requirement.json"),
        )
    )

    # 7. Insecure http:// CALM meta-schema $ref
    s7 = copy.deepcopy(req_19_1)
    s7["allOf"][0]["$ref"] = "http://calm.finos.org/controls/2025-03/meta/control-requirement.json"
    scenarios.append(
        (
            "7. Reject insecure http:// CALM meta-schema $ref",
            validate_requirement_schema_structure(s7, "FINOS-PREV-019-001.requirement.json"),
        )
    )

    # 8. Missing uniqueItems: true on enum array with minItems > 1
    s8 = copy.deepcopy(req_19_1)
    del s8["properties"]["required-decision-inputs"]["uniqueItems"]
    scenarios.append(
        (
            "8. Detect missing uniqueItems: true on required-decision-inputs schema",
            validate_requirement_schema_structure(s8, "FINOS-PREV-019-001.requirement.json"),
        )
    )

    # 9. Duplicate items in required-decision-inputs configuration instance
    s9 = copy.deepcopy(cfg_19_1)
    s9["required-decision-inputs"] = ["user-id", "user-id", "user-id"]
    scenarios.append(
        (
            "9. Reject duplicate items in required-decision-inputs instance",
            validate_json_value(s9, req_19_1),
        )
    )

    # 10. MI-18 (001): Stale mandate window exceeding 300s ceiling
    s10 = copy.deepcopy(cfg_18_1)
    s10["max-mandate-staleness-seconds"] = 3600
    scenarios.append(
        (
            "10. Reject MI-18-001 stale mandate freshness window (> 300s)",
            validate_json_value(s10, req_18_1),
        )
    )

    # 11. MI-18 (002): Excessive multi-agent delegation depth (> 5)
    s11 = copy.deepcopy(cfg_18_2)
    s11["max-delegation-depth"] = 10
    scenarios.append(
        (
            "11. Reject MI-18-002 excessive delegation hop depth (> 5)",
            validate_json_value(s11, req_18_2),
        )
    )

    # 12. MI-20: Omitting ST-05 collective systemic exposure trigger
    s12 = copy.deepcopy(cfg_20_1)
    s12["mandatory-state-triggers"] = [
        "ST-01-velocity-and-rate-anomaly",
        "ST-02-scope-and-authority-violation",
        "ST-03-loop-and-recursion-exhaustion",
        "ST-04-data-boundary-and-egress-violation",
    ]
    scenarios.append(
        (
            "12. Reject MI-20 circuit breaker omitting ST-05 collective systemic exposure trigger",
            validate_json_value(s12, req_20_1),
        )
    )

    # 13. MI-20: Enabling unattended auto-reset after circuit breaker trip
    s13 = copy.deepcopy(cfg_20_1)
    s13["auto-reset-permitted"] = True
    scenarios.append(
        (
            "13. Reject MI-20 circuit breaker enabling unattended auto-reset",
            validate_json_value(s13, req_20_1),
        )
    )

    # 14. MI-21: Omitting execution-environment-attestation-digest from SCITT audit receipt
    s14 = copy.deepcopy(cfg_21_1)
    s14["required-receipt-claims"] = [
        "mandate-id",
        "policy-digest",
        "inputs-hash",
        "decision-verdict",
        "monotonic-sequence-number",
    ]
    scenarios.append(
        (
            "14. Reject MI-21 SCITT receipt omitting execution-environment-attestation-digest",
            validate_json_value(s14, req_21_1),
        )
    )

    passed = 0
    for label, errs in scenarios:
        if errs:
            print(f"  [PASS] {label} -> caught ({errs[0]})")
            passed += 1
        else:
            print(f"  [FAIL] {label} -> mutation was NOT caught!")

    print(f"\nAdversarial Self-Test Summary: {passed}/{len(scenarios)} scenarios passed.")
    return passed == len(scenarios)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the FINOS Multi-Agent Reference Architecture CALM model and atomized AIGF controls."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run 14 adversarial red-team mutation scenarios against the validator.",
    )
    args = parser.parse_args()

    ok, errors, stats = validate_all()
    if not ok:
        print(f"[FAIL] Validation failed with {len(errors)} error(s):")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(
        f"[PASS] Validated CALM Multi-Agent Architecture ({stats['nodes']} nodes, "
        f"{stats['relationships']} relationships, {stats['controls']} Threat Model controls C1..C36, "
        f"{stats['threats']} threats, {stats['aigf_schemas']} atomized AIGF control schemas) with 0 errors."
    )

    if args.self_test:
        if not run_self_tests():
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
