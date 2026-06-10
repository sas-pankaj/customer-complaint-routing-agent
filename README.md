# Customer Complaint Classification & Routing Engine

> **Hackathon Challenge — AGENTS_004**

## Overview

An agentic AI solution that automatically classifies incoming customer complaints and service cases, prioritizes them based on severity, and routes them to the right team with full SLA awareness.

The solution is built using **Python** and **Jupyter Notebooks**, following an agent-oriented architecture where each component handles a distinct responsibility in the pipeline.

---

## Problem Statement

Customer service teams receive a high volume of complaints across multiple channels. Manual triage is slow, inconsistent, and SLA-breaching. This project solves that by:

- **Classifying** incoming complaints into categories (e.g. Baggage, Booking, Refund, Safety)
- **Prioritizing** cases based on urgency signals and SLA thresholds
- **Routing** each case to the correct team automatically
- **Surfacing** a live routing dashboard for operational visibility

---

## Key Features

| Feature | Description |
|---|---|
| Text Classification | NLP-based categorization of free-text complaints |
| Prioritization Logic | Rule-based + ML scoring for urgency and SLA impact |
| Intelligent Routing | Maps category + priority to the responsible team |
| SLA Awareness | Tracks deadlines and escalates cases at risk |
| Live Dashboard | Real-time view of incoming case stream and routing status |

---

## Tech Stack

- **Language:** Python 3.11+
- **Notebooks:** Jupyter Notebook / JupyterLab
- **NLP / ML:** (e.g. scikit-learn, spaCy, OpenAI API, LangChain — TBD)
- **Dashboard:** (e.g. Panel, Streamlit — TBD)
- **Data:** Synthetic complaint dataset

---

## Project Structure

```
customer-complaint-routing-agent/
│
├── data/                   # Raw and processed complaint datasets
├── notebooks/              # Jupyter notebooks for each agent component
│   ├── 01_classification.ipynb
│   ├── 02_prioritization.ipynb
│   ├── 03_routing.ipynb
│   └── 04_dashboard.ipynb
├── src/                    # Reusable Python modules
│   ├── classifier.py
│   ├── prioritizer.py
│   └── router.py
├── tests/                  # Unit tests
├── requirements.txt
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Jupyter Notebook or JupyterLab

### Installation

```bash
git clone https://github.com/<your-org>/customer-complaint-routing-agent.git
cd customer-complaint-routing-agent
pip install -r requirements.txt
jupyter notebook
```

### Running the Pipeline

Open the notebooks in order under `notebooks/` to step through classification, prioritization, routing, and the live dashboard.

---

## Agent Architecture

```
Incoming Case Stream
        │
        ▼
┌─────────────────┐
│  Classifier     │  → Assigns category label
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Prioritizer    │  → Scores urgency + SLA risk
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Router         │  → Sends to correct team queue
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Dashboard      │  → Live routing status view
└─────────────────┘
```

---

## Team

Built for the internal AI Hackathon — AGENTS_004 challenge.

---

## License

Internal use only.
