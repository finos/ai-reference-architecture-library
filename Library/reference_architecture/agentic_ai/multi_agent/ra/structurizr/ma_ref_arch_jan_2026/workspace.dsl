/*
 * Multi-Agent Reference Architecture (Jan 2026) as a Structurizr model.
 *
 * Layers from ma_ref_arch_jan_2026.md are nested groups. Risks from the FINOS AI Governance
 * Framework are element properties plus one perspective per risk ID, so the Structurizr UI can
 * highlight every element affected by a chosen risk. RI-31 and RI-32 are on unmerged branches
 * of finos/ai-governance-framework at the time of writing.
 *
 * Element positions for the "Overview" view live in workspace.json and mirror
 * ../../assets/ma_ref_arch_jan_2026.drawio.
 */
workspace "Multi-Agent Reference Architecture" "FINOS AI Reference Architecture Library, Jan 2026" {

    !identifiers flat

    model {
        properties {
            "structurizr.groupSeparator" "/"
        }

        user = person "User" "Employee, customer, analyst or automated process."

        platform = softwareSystem "Multi-Agent Platform" "Governed, extensible multi-agent system." {
            group "User Interaction Layer" {
                application = container "Application" "Web, mobile, chatbot or workflow surface. Forwards user input to agents and returns responses; human-in-the-loop review." "" {
                    properties {
                        "risks" "RI-10, RI-18, RI-20, RI-31"
                    }
                    perspectives {
                        "RI-10" "Prompt Injection"
                        "RI-18" "Model Overreach / Expanded Use"
                        "RI-20" "Reputational Risk"
                        "RI-31" "Human Approval Fatigue and Consent Gate Degradation"
                    }
                }
            }

            group "Agent Gateway Layer" {
                agentRegistry = container "Agent Registry" "Catalog of agents, capabilities, metadata and configuration; versioning and controlled onboarding." "" "Database" {
                    properties {
                        "risks" "RI-18, RI-28"
                    }
                    perspectives {
                        "RI-18" "Model Overreach / Expanded Use"
                        "RI-28" "Multi-Agent Trust Boundary Violations"
                    }
                }
                agentGateway = container "Gateway" "Validates requests and routes each one to the correct agent or agent group." "" {
                    properties {
                        "risks" "RI-24, RI-28"
                    }
                    perspectives {
                        "RI-24" "Agent Action Authorization Bypass"
                        "RI-28" "Multi-Agent Trust Boundary Violations"
                    }
                }
                agentGuardrails = container "Agent Guardrails / Policies" "Zero trust, AuthN / AuthZ, input validation, content filtering, rate limits, dynamic policy." "ZeroTrust, AuthN, AuthZ" "Guardrails" {
                    properties {
                        "risks" "RI-10, RI-22, RI-24"
                    }
                    perspectives {
                        "RI-10" "Prompt Injection"
                        "RI-22" "Regulatory Compliance and Oversight"
                        "RI-24" "Agent Action Authorization Bypass"
                    }
                }
            }

            group "Agent Layer" {
                group "Agent Collaboration Patterns" {
                    supervisorWorker = container "Supervisor / Worker" "Supervisor decomposes the task and orchestrates specialised worker agents." "" "Pattern" {
                        properties {
                            "risks" "RI-4, RI-17, RI-28"
                        }
                        perspectives {
                            "RI-4" "Hallucination and Inaccurate Outputs"
                            "RI-17" "Lack of Explainability"
                            "RI-28" "Multi-Agent Trust Boundary Violations"
                        }
                    }
                    skillRouting = container "Skill Based Routing" "Request routed to an available agent that has the required skill." "" "Pattern" {
                        properties {
                            "risks" "RI-18, RI-28"
                        }
                        perspectives {
                            "RI-18" "Model Overreach / Expanded Use"
                            "RI-28" "Multi-Agent Trust Boundary Violations"
                        }
                    }
                    agentAsTool = container "Agent as a Tool" "One agent invokes another as a tool, enabling handoff to specialists." "" "Pattern" {
                        properties {
                            "risks" "RI-24, RI-25, RI-28"
                        }
                        perspectives {
                            "RI-24" "Agent Action Authorization Bypass"
                            "RI-25" "Tool Chain Manipulation and Injection"
                            "RI-28" "Multi-Agent Trust Boundary Violations"
                        }
                    }
                }

                group "Unified Agent Runtime" {
                    stateMgmt = container "State Management" "Complete task state enabling pause, resume and handoff." "" {
                        properties {
                            "risks" "RI-27, RI-28"
                        }
                        perspectives {
                            "RI-27" "Agent State Persistence Poisoning"
                            "RI-28" "Multi-Agent Trust Boundary Violations"
                        }
                    }
                    secureExec = container "Secure Execution" "Intercepts and validates all tool calls; handles execution and credentials inside the sandbox." "" {
                        properties {
                            "risks" "RI-24, RI-25, RI-29"
                        }
                        perspectives {
                            "RI-24" "Agent Action Authorization Bypass"
                            "RI-25" "Tool Chain Manipulation and Injection"
                            "RI-29" "Agent-Mediated Credential Discovery and Harvesting"
                        }
                    }
                    collabHandoff = container "Collaboration / Handoff" "Stateful collaboration between agents through shared memory and state." "" {
                        properties {
                            "risks" "RI-27, RI-28"
                        }
                        perspectives {
                            "RI-27" "Agent State Persistence Poisoning"
                            "RI-28" "Multi-Agent Trust Boundary Violations"
                        }
                    }
                    workspaceFs = container "Workspace File System" "Sandboxed, persistent file system for large artifacts." "" "Database" {
                        properties {
                            "risks" "RI-2, RI-27, RI-29"
                        }
                        perspectives {
                            "RI-2" "Information Leaked to Vector Store"
                            "RI-27" "Agent State Persistence Poisoning"
                            "RI-29" "Agent-Mediated Credential Discovery and Harvesting"
                        }
                    }
                    adaptiveLearning = container "Adaptive Learning" "Learning signals from execution outcomes refine prompts, agent configuration and tool selection." "" {
                        properties {
                            "risks" "RI-9, RI-14, RI-27"
                        }
                        perspectives {
                            "RI-9" "Data Poisoning"
                            "RI-14" "Inadequate System Alignment"
                            "RI-27" "Agent State Persistence Poisoning"
                        }
                    }
                    group "Tools Layer" {
                        mcpClient = container "MCP Client" "Secure bridge to the external MCP Layer." "" {
                            properties {
                                "risks" "RI-25, RI-26, RI-32"
                            }
                            perspectives {
                                "RI-25" "Tool Chain Manipulation and Injection"
                                "RI-26" "MCP Server Supply Chain Compromise"
                                "RI-32" "Third-Party Content Loaded as Agent Instructions"
                            }
                        }
                        shellTool = container "Shell Tool" "Sandboxed shell for basic commands." "" {
                            properties {
                                "risks" "RI-24, RI-25, RI-29"
                            }
                            perspectives {
                                "RI-24" "Agent Action Authorization Bypass"
                                "RI-25" "Tool Chain Manipulation and Injection"
                                "RI-29" "Agent-Mediated Credential Discovery and Harvesting"
                            }
                        }
                        ioTool = container "I/O Tool" "Reads from and writes to the workspace file system." "" {
                            properties {
                                "risks" "RI-27, RI-29"
                            }
                            perspectives {
                                "RI-27" "Agent State Persistence Poisoning"
                                "RI-29" "Agent-Mediated Credential Discovery and Harvesting"
                            }
                        }
                        webSearchTool = container "Web Search Tool" "Built-in web search." "" {
                            properties {
                                "risks" "RI-10, RI-19, RI-23"
                            }
                            perspectives {
                                "RI-10" "Prompt Injection"
                                "RI-19" "Data Quality and Drift"
                                "RI-23" "Intellectual Property (IP) and Copyright"
                            }
                        }
                    }

                    group "Short-Term Memory" {
                        contextManager = container "In-Session Context Manager" "Trimming and summarisation to manage context length, cost and latency." "" {
                            properties {
                                "risks" "RI-4, RI-10"
                            }
                            perspectives {
                                "RI-4" "Hallucination and Inaccurate Outputs"
                                "RI-10" "Prompt Injection"
                            }
                        }
                    }

                    group "Long-Term Memory" {
                        sessionSummaries = container "Session Summaries" "Summaries of past interactions for future reference." "" "Database" {
                            properties {
                                "risks" "RI-2, RI-27"
                            }
                            perspectives {
                                "RI-2" "Information Leaked to Vector Store"
                                "RI-27" "Agent State Persistence Poisoning"
                            }
                        }
                        personalization = container "User / Task Personalization" "User preferences and task-specific information across sessions." "" "Database" {
                            properties {
                                "risks" "RI-2, RI-16, RI-27"
                            }
                            perspectives {
                                "RI-2" "Information Leaked to Vector Store"
                                "RI-16" "Bias and Discrimination"
                                "RI-27" "Agent State Persistence Poisoning"
                            }
                        }
                    }

                }

            }

            group "Knowledge Layer" {
                sourceBases = container "Source Bases" "Internal and external authoritative repositories (structured, unstructured, graph)." "" "Database" {
                    properties {
                        "risks" "RI-9, RI-10, RI-19, RI-23"
                    }
                    perspectives {
                        "RI-9" "Data Poisoning"
                        "RI-10" "Prompt Injection"
                        "RI-19" "Data Quality and Drift"
                        "RI-23" "Intellectual Property (IP) and Copyright"
                    }
                }
                vectorDbs = container "Vector DBs" "Vector retrieval for semantic search and grounding." "" "Database" {
                    properties {
                        "risks" "RI-2, RI-9, RI-19"
                    }
                    perspectives {
                        "RI-2" "Information Leaked to Vector Store"
                        "RI-9" "Data Poisoning"
                        "RI-19" "Data Quality and Drift"
                    }
                }
            }

            group "MCP Layer" {
                mcpGuardrails = container "MCP Guardrails / Policies" "Zero trust, AuthN / AuthZ for every MCP request; tool entitlements, rate limits, parameter validation." "ZeroTrust, AuthN, AuthZ" "Guardrails" {
                    properties {
                        "risks" "RI-24, RI-25, RI-29"
                    }
                    perspectives {
                        "RI-24" "Agent Action Authorization Bypass"
                        "RI-25" "Tool Chain Manipulation and Injection"
                        "RI-29" "Agent-Mediated Credential Discovery and Harvesting"
                    }
                }
                mcpGateway = container "MCP Gateway" "Validates MCP connection requests and routes them to the correct server instance." "" {
                    properties {
                        "risks" "RI-24, RI-25"
                    }
                    perspectives {
                        "RI-24" "Agent Action Authorization Bypass"
                        "RI-25" "Tool Chain Manipulation and Injection"
                    }
                }
                mcpRegistry = container "MCP Registry" "Catalog of approved MCP servers; controlled onboarding." "" "Database" {
                    properties {
                        "risks" "RI-26"
                    }
                    perspectives {
                        "RI-26" "MCP Server Supply Chain Compromise"
                    }
                }
                mcpZoo = container "MCP Zoo" "Approved enterprise and third-party MCP servers." "" "External" {
                    properties {
                        "risks" "RI-1, RI-7, RI-26, RI-29, RI-32"
                    }
                    perspectives {
                        "RI-1" "Information Leaked To Hosted Model"
                        "RI-7" "Availability of Foundational Model"
                        "RI-26" "MCP Server Supply Chain Compromise"
                        "RI-29" "Agent-Mediated Credential Discovery and Harvesting"
                        "RI-32" "Third-Party Content Loaded as Agent Instructions"
                    }
                }
            }

            group "LLM Layer" {
                llmGuardrails = container "LLM Guardrails / Policies" "Zero trust, AuthN / AuthZ for every inference; prompt-injection checks, output filtering, cost limits." "ZeroTrust, AuthN, AuthZ" "Guardrails" {
                    properties {
                        "risks" "RI-1, RI-7, RI-10"
                    }
                    perspectives {
                        "RI-1" "Information Leaked To Hosted Model"
                        "RI-7" "Availability of Foundational Model"
                        "RI-10" "Prompt Injection"
                    }
                }
                llmGateway = container "LLM Gateway" "Routes inference requests to the correct model instance." "" {
                    properties {
                        "risks" "RI-1, RI-7"
                    }
                    perspectives {
                        "RI-1" "Information Leaked To Hosted Model"
                        "RI-7" "Availability of Foundational Model"
                    }
                }
                modelRegistry = container "Model Registry" "Catalog of approved models; versions, constraints, controlled onboarding." "" "Database" {
                    properties {
                        "risks" "RI-5, RI-8"
                    }
                    perspectives {
                        "RI-5" "Foundation Model Versioning"
                        "RI-8" "Tampering With the Foundational Model"
                    }
                }
                llmZoo = container "LLM Zoo" "Approved hosted and vendor foundation models." "" "External,Database" {
                    properties {
                        "risks" "RI-1, RI-4, RI-5, RI-6, RI-8, RI-16, RI-17, RI-23"
                    }
                    perspectives {
                        "RI-1" "Information Leaked To Hosted Model"
                        "RI-4" "Hallucination and Inaccurate Outputs"
                        "RI-5" "Foundation Model Versioning"
                        "RI-6" "Non-Deterministic Behaviour"
                        "RI-8" "Tampering With the Foundational Model"
                        "RI-16" "Bias and Discrimination"
                        "RI-17" "Lack of Explainability"
                        "RI-23" "Intellectual Property (IP) and Copyright"
                    }
                }
            }

            group "Observability Layer" {
                logs = container "Logs" "Structured and unstructured logs from all layers." "" "Database" {
                    properties {
                        "risks" "RI-2, RI-22, RI-29"
                    }
                    perspectives {
                        "RI-2" "Information Leaked to Vector Store"
                        "RI-22" "Regulatory Compliance and Oversight"
                        "RI-29" "Agent-Mediated Credential Discovery and Harvesting"
                    }
                }
                traces = container "Traces" "Distributed tracing across the request lifecycle." "" "Database" {
                    properties {
                        "risks" "RI-2, RI-17"
                    }
                    perspectives {
                        "RI-2" "Information Leaked to Vector Store"
                        "RI-17" "Lack of Explainability"
                    }
                }
                metrics = container "Metrics" "Latency, throughput, errors, model usage, resource use." "" "Database" {
                    properties {
                        "risks" "RI-7"
                    }
                    perspectives {
                        "RI-7" "Availability of Foundational Model"
                    }
                }
                events = container "Events" "Policy violations, model selection, escalations, evaluation outcomes." "" "Database" {
                    properties {
                        "risks" "RI-22"
                    }
                    perspectives {
                        "RI-22" "Regulatory Compliance and Oversight"
                    }
                }
                anomalyDetection = container "Anomaly Detection" "Detects failures, regressions, misuse and emerging risks." "" {
                    properties {
                        "risks" "RI-19, RI-27"
                    }
                    perspectives {
                        "RI-19" "Data Quality and Drift"
                        "RI-27" "Agent State Persistence Poisoning"
                    }
                }
                correlationEngine = container "Correlation Engine" "Correlates signals to connect symptoms to root causes." "" {
                    properties {
                        "risks" "RI-17"
                    }
                    perspectives {
                        "RI-17" "Lack of Explainability"
                    }
                }
            }

            group "Evaluation Layer" {
                feedbackEngine = container "Feedback" "Correctness, preference and quality signals." "" {
                    properties {
                        "risks" "RI-9, RI-14, RI-16"
                    }
                    perspectives {
                        "RI-9" "Data Poisoning"
                        "RI-14" "Inadequate System Alignment"
                        "RI-16" "Bias and Discrimination"
                    }
                }
                humanSupervision = container "Human Supervision" "Inspect, approve, correct or override agent outputs." "" {
                    properties {
                        "risks" "RI-18, RI-22, RI-31"
                    }
                    perspectives {
                        "RI-18" "Model Overreach / Expanded Use"
                        "RI-22" "Regulatory Compliance and Oversight"
                        "RI-31" "Human Approval Fatigue and Consent Gate Degradation"
                    }
                }
                runtimeProtection = container "Runtime Protection" "Detects unsafe or non-compliant behaviour; blocks actions or escalates." "" {
                    properties {
                        "risks" "RI-14, RI-24, RI-25"
                    }
                    perspectives {
                        "RI-14" "Inadequate System Alignment"
                        "RI-24" "Agent Action Authorization Bypass"
                        "RI-25" "Tool Chain Manipulation and Injection"
                    }
                }
            }

        }

        user -> application "Goals, inputs; reviews and approves outputs"
        application -> agentGateway "Agent requests"
        agentGateway -> agentRegistry "Resolves target agents"
        agentGateway -> agentGuardrails "AuthN / AuthZ, input validation"
        agentGateway -> skillRouting "Routes validated requests"
        supervisorWorker -> collabHandoff "Delegates work via"
        agentAsTool -> secureExec "Invokes agents as tools via"
        collabHandoff -> stateMgmt "Shares task state"
        stateMgmt -> sessionSummaries "Persists and restores context"
        secureExec -> mcpClient "Validated tool calls"
        secureExec -> shellTool ""
        secureExec -> ioTool ""
        secureExec -> webSearchTool ""
        ioTool -> workspaceFs "Reads and writes files"
        contextManager -> vectorDbs "Retrieves grounding context"
        contextManager -> sourceBases "Queries source data"
        contextManager -> llmGateway "Inference requests"
        mcpClient -> mcpGateway "MCP connection requests" "MCP"
        mcpGateway -> mcpGuardrails "AuthN / AuthZ, parameter validation"
        mcpGateway -> mcpRegistry "Looks up approved servers"
        mcpGateway -> mcpZoo "Routed MCP calls" "MCP"
        llmGateway -> llmGuardrails "AuthN / AuthZ, input / output filtering"
        llmGateway -> modelRegistry "Looks up approved models"
        llmGateway -> llmZoo "Routed inference requests"
        secureExec -> runtimeProtection "Agent actions for checking" "" "Oversight"
        runtimeProtection -> secureExec "Blocks / escalations" "" "Oversight"
        humanSupervision -> application "Approvals and overrides" "" "Oversight"
        feedbackEngine -> adaptiveLearning "Feedback signals" "" "Oversight"
        logs -> correlationEngine ""
        traces -> correlationEngine ""
        metrics -> anomalyDetection ""
        events -> anomalyDetection ""
        application -> logs "" "" "Telemetry" {
            properties {
                "signals" "Interaction logs, session events"
            }
        }
        agentGateway -> events "" "" "Telemetry" {
            properties {
                "signals" "Routing, policy, access signals"
            }
        }
        secureExec -> traces "" "" "Telemetry" {
            properties {
                "signals" "Reasoning traces, execution metrics"
            }
        }
        vectorDbs -> metrics "" "" "Telemetry" {
            properties {
                "signals" "Retrieval metrics, search traces"
            }
        }
        mcpGateway -> events "" "" "Telemetry" {
            properties {
                "signals" "Routing, policy, access signals"
            }
        }
        llmGateway -> metrics "" "" "Telemetry" {
            properties {
                "signals" "Model usage, routing signals"
            }
        }
        runtimeProtection -> events "" "" "Telemetry" {
            properties {
                "signals" "Feedback events, protection signals"
            }
        }
    }

    views {
        container platform "Overview" "All layers, arranged like the draw.io diagram." {
            include *
        }


        styles {
            element "Element" {
                metadata false
                description false
            }
            element "Person" {
                shape Person
                width 300
                height 300
                background #08427b
                color #ffffff
            }
            element "Container" {
                background #438dd5
                color #ffffff
                width 340
                height 100
                fontSize 22
            }
            element "Database" {
                shape Cylinder
            }
            element "Guardrails" {
                background #2f6aa5
            }
            element "Pattern" {
                shape RoundedBox
            }
            element "External" {
                background #999999
            }
            // Layers: solid light borders, so they can't be mistaken for arrows.
            element "Group" {
                color #444444
                stroke #c4c4c4
                strokeWidth 3
                border solid
            }
            relationship "Relationship" {
                style solid
                routing Direct
                thickness 3
                fontSize 20
                width 260
            }
            relationship "Telemetry" {
                color #d9822b
                thickness 2
            }
            relationship "Oversight" {
                color #7d3c98
            }
        }
    }

}
