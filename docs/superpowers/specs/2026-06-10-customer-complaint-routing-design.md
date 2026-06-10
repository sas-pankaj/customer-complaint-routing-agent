# Customer Complaint Classification and Routing Engine Design

Date: 2026-06-10
Status: Approved for planning

## 1. Goal and Scope

Build a notebook-first, agentic pipeline that processes customer complaints, classifies them into operational categories, assesses severity and intent, applies a confidence gate with human fallback, and routes approved complaints to the correct internal team.

In scope for MVP:

- Sample complaint input dataset (demo data)
- End-to-end automated flow for classify -> analyze -> confidence gate -> route
- Human-in-the-loop escalation when confidence is below threshold
- Structured outputs suitable for extension

Out of scope for MVP (future scope):

- UI/dashboard in the hackathon demo
- Live omni-channel ingestion (email, WhatsApp, Twitter, forms)
- Real ticket creation in Jira/ServiceNow

## 2. Platform and Technical Choices

- Runtime platform: AMD Developer Cloud notebook environment
- Base image: ROCm + vLLM
- Model strategy: Approach 2 (specialized modular agents)
- Model family for MVP: Mistral 7B class model served via vLLM on AMD GPU
- Orchestration style: Lightweight custom Python orchestration (no heavy agent framework)
- Structured validation: Pydantic models for all agent outputs

Rationale:

- Demonstrates efficient GPU utilization with high throughput
- Keeps architecture modular and extensible
- Minimizes framework overhead for hackathon speed

## 3. Agent Pipeline Architecture

### Stage 0: Input Loader

Input source for MVP is a curated sample complaint dataset.

Output contract:

- complaint_id: string
- channel: string (demo metadata)
- complaint_text: string
- received_at: ISO timestamp

### Stage 1: Classification Agent

Purpose:

- Assign complaint category from approved taxonomy.

Allowed categories:

- Payments / Refund related
- Baggage / Item lost
- Booking issues
- General inquiry
- Safety / Security concern
- Service quality
- Other

Output contract:

- category: enum (above)
- category_confidence: float [0, 1]
- classifier_reason: short string

### Stage 2: Severity and Intention Agent

Purpose:

- Infer urgency profile and customer intent.

Output contract:

- severity_level: enum {High, Medium, Low}
- severity_detail: string
- intention: enum {Complaint, Inquiry, Request, Escalation, Unknown}
- analysis_confidence: float [0, 1]
- analysis_reason: short string

### Stage 3: Confidence Gate Agent

Purpose:

- Decide auto-routing eligibility.

Rule:

- If final_confidence >= 0.70 -> auto-route
- Else -> escalate to human review queue

Final confidence policy:

- final_confidence = min(category_confidence, analysis_confidence)

Output contract:

- final_confidence: float [0, 1]
- auto_route: boolean
- escalation_reason: string

### Stage 4: Notification and Routing Agent

Purpose:

- Route approved case to destination team and log routing payload.

Category to team mapping:

- Payments / Refund related -> Finance Team
- Baggage / Item lost -> Logistics Team
- Booking issues -> Reservations Team
- General inquiry -> Support Team
- Safety / Security concern -> Compliance Team
- Service quality -> Operations Team
- Other -> Support Team

Output contract:

- route_status: enum {Routed, HumanReview}
- destination_team: string
- priority_hint: enum {High, Medium, Low}
- routing_timestamp: ISO timestamp
- routing_note: string

## 4. End-to-End Data Flow

For each complaint:

1. Load complaint text and metadata.
2. Run Classification Agent and validate output.
3. Run Severity and Intention Agent and validate output.
4. Apply Confidence Gate using threshold = 0.70.
5. If auto_route is true, execute Routing Agent and emit route payload.
6. If auto_route is false, send case to human-review queue payload.

## 5. Error Handling and Guardrails

- Invalid category output:
  - Fallback to Other
  - Mark for human review
- Missing or non-numeric confidence:
  - Set auto_route=false
  - Escalate to human review
- LLM timeout or inference error:
  - Retry once
  - On second failure, escalate to human review
- Empty complaint text:
  - Reject with validation error and human queue tag
- Prompt drift/hallucination:
  - Strict schema validation via Pydantic
  - Keep prompts bounded to taxonomy and enums

## 6. Notebook Implementation Plan (Execution Units)

Notebook 1: Environment and Model Serving

- Verify ROCm/GPU visibility
- Install/verify dependencies
- Start vLLM server for selected Mistral model
- Run health checks and a sample inference

Notebook 2: Agent Contracts and Prompt Templates

- Define Pydantic schemas
- Define prompts for Stage 1-4
- Build helper client wrappers for vLLM calls

Notebook 3: Pipeline Execution with Sample Complaints

- Load sample complaints
- Execute full pipeline per complaint
- Persist structured outputs to dataframe/json

Notebook 4: Evaluation and Efficiency Metrics

- Category and severity distribution
- Auto-route vs human-review rate
- Latency summary and throughput snapshots
- GPU-efficiency evidence for PPT

## 7. Metrics for Hackathon Demonstration

Primary success metric:

- Balanced quality across classification accuracy, routing correctness, and SLA-risk relevance.

Operational metrics:

- Classification agreement on labeled sample set
- Routing precision by category
- Human escalation ratio (confidence < 0.70)
- End-to-end latency per complaint
- Throughput (complaints per minute) under batch execution

## 8. Extension Roadmap (Post-MVP)

- Add live ingestion connectors (email/social/form)
- Add ticketing adapters (Jira/ServiceNow)
- Add dashboard/UI for operations team
- Add retraining or feedback loop from human-review outcomes

## 9. Open Decisions Locked for MVP

Locked:

- No UI in MVP
- Sample complaints as input
- 70% confidence threshold
- Lightweight custom orchestration
- Modular specialized agent chain

This design is approved as the implementation baseline for planning.
