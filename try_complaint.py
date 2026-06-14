"""Manual tester: pipe or pass a complaint and see every stage.

Usage:
    python try_complaint.py "I was charged twice and need a refund urgently"
    python try_complaint.py            # uses a built-in example
"""

import sys

from complaint_router.llm.mock_client import MockClient
from complaint_router.pipeline import run_pipeline
from complaint_router.schemas import ComplaintInput, utcnow

text = " ".join(sys.argv[1:]) or "My booking was cancelled and I want to speak to a manager."

complaint = ComplaintInput(
    complaint_id="MANUAL",
    channel="manual",
    complaint_text=text,
    received_at=utcnow(),
)

result = run_pipeline(complaint, MockClient())

print(f"\ncomplaint: {text}\n")
if result.classification:
    print(f"  [1] category   : {result.classification.category.value} "
          f"(conf {result.classification.category_confidence})")
if result.analysis:
    print(f"  [2] severity   : {result.analysis.severity_level.value}")
    print(f"      intention  : {result.analysis.intention.value} "
          f"(conf {result.analysis.analysis_confidence})")
if result.gate:
    print(f"  [3] final_conf : {result.gate.final_confidence:.2f}  "
          f"auto_route={result.gate.auto_route}")
    print(f"      reason     : {result.gate.escalation_reason}")
print(f"  [4] route      : {result.route.route_status.value} -> "
      f"{result.route.destination_team} (priority {result.route.priority_hint.value})")
print(f"      note       : {result.route.routing_note}\n")
