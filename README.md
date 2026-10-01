# AI CFO — Financial Decision Intelligence System

> A multi-agent financial intelligence platform that transforms transaction data into structured financial analysis, risk indicators, forecasting, AI-generated insights, and management reports.

**Live Demo:** https://ai-cfo-financial-intelligence.streamlit.app/

**GitHub:** https://github.com/AbdelrhmanAkl/AI-CFO-Financial-Intelligence

---

## Overview

**AI CFO** is a multi-agent financial decision intelligence system designed to analyze financial transaction data and convert analytical results into actionable management information.

Instead of relying on a single AI model, the system uses specialized agents, each responsible for a specific analytical task:

* Financial performance analysis
* Transaction risk analysis
* Transaction-volume forecasting
* Business insight generation
* Management report generation
* Automated report validation

The agents are orchestrated through a **LangGraph workflow**, creating a structured end-to-end financial analysis pipeline.

---

## Live Application

The complete system is deployed as a Streamlit application:

**Live Demo:**
https://ai-cfo-financial-intelligence.streamlit.app/

The application provides an interactive workspace for:

* Financial Performance
* Risk & Anomaly Analysis
* Forecasting
* AI Insights
* Executive Reports
* Report Validation

---

## System Architecture

```text
                         ┌──────────────────┐
                         │     User Query   │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │    Supervisor    │
                         └────────┬─────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              ▼                   ▼                   ▼
       ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
       │  SQL Agent  │     │  Risk Agent │     │ Forecast    │
       │             │     │             │     │    Agent    │
       └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  ▼
                         ┌──────────────────┐
                         │   Insight Agent  │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   Report Agent   │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Report Validator │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Validated Report │
                         └──────────────────┘
```

---

## Multi-Agent Workflow

### 1. Supervisor Agent

The Supervisor interprets the user's request and determines which analytical capabilities are required.

It coordinates the workflow and routes the request to the appropriate agents.

### 2. SQL Agent

The SQL Agent translates financial questions into SQL queries and retrieves structured information from the transaction database.

It supports analysis such as:

* Transaction volume
* Total money received
* Total money paid
* Average transaction amount
* Laundering-tagged transaction counts
* Historical transaction activity

The agent also validates generated SQL and restricts database operations to analytical queries.

### 3. Risk Agent

The Risk Agent analyzes transaction and account-level patterns using predefined analytical thresholds.

Current indicators include:

* High-value transactions
* High-value laundering-tagged transactions
* High-frequency accounts
* Transaction activity from high-frequency accounts
* Account-level activity patterns

These indicators are intended for analytical review and **do not establish fraud or financial crime**.

### 4. Forecast Agent

The Forecast Agent evaluates multiple statistical forecasting approaches for transaction volume.

Models currently evaluated include:

* Simple Exponential Smoothing
* 7-Day Moving Average
* Naive Last-Value Forecast

The models are compared using **Mean Absolute Error (MAE)** through historical backtesting.

The system then selects the model with the lowest observed backtesting error.

### 5. Insight Agent

The Insight Agent converts analytical outputs into concise business observations.

Its purpose is to bridge the gap between raw analytical results and management-level interpretation.

### 6. Report Agent

The Report Agent combines the outputs of the analytical agents into a structured management report.

The report includes:

* Executive Summary
* Financial Performance
* Risk & Anomaly Analysis
* Forecast
* Forecast Validation
* Historical Observations
* AI-Generated Insights
* Management Actions
* Data & Methodology

### 7. Report Validator

The final stage automatically validates the generated report against the underlying analytical results.

Validation checks include:

* Numerical integrity
* Required section integrity
* Cross-agent consistency
* Forecast consistency
* Report completeness

A report is marked as **PASSED** only when the validation checks succeed.

---

## Technology Stack

| Technology    | Purpose                                  |
| ------------- | ---------------------------------------- |
| Python        | Core application and agent development   |
| LangGraph     | Multi-agent orchestration                |
| LangChain     | LLM and agent integration                |
| SQLite        | Financial transaction database           |
| Streamlit     | Interactive web application              |
| Ollama        | Local LLM execution                      |
| Qwen3 8B      | Local language model                     |
| Google Gemini | Cloud LLM deployment                     |
| Pandas        | Data analysis                            |
| Scikit-learn  | Statistical evaluation                   |
| Git & GitHub  | Version control and portfolio deployment |

---

## Dataset

The system is built around a large financial transaction dataset containing transaction-level information such as:

* Timestamp
* Sending bank
* Sending account
* Receiving bank
* Receiving account
* Amount received
* Receiving currency
* Amount paid
* Payment currency
* Payment format
* Laundering label

### Deployment Dataset

For the public Streamlit deployment, a dedicated deployment database is used instead of the complete local dataset.

The deployment database contains:

**1,085,316 transactions**

It preserves the analytical structures required by the application while keeping the deployed application practical for a public demonstration.

The deployment dataset is a selected subset and should **not be interpreted as statistically equivalent to the full source dataset**.

---

## Example Financial Analysis

The deployed system currently provides metrics such as:

```text
Transactions
1,085,316

Money Received
4.61T

Money Paid
3.59T

Average Transaction
3.31M

Laundering Tagged
5,177
```

### Risk Indicators

```text
High-Value Transactions
192,079

High-Value Laundering
1,010

High-Frequency Accounts
4,919

Transactions From High-Frequency Accounts
1,044,651
```

### Forecasting

The forecasting pipeline evaluates candidate models through historical backtesting.

Example output:

```text
Selected Model
Naive Last-Value Forecast

Next-Day Transactions
11

Backtesting MAE
14,878.64

Backtesting Observations
11
```

The forecast is a statistical estimate based on the available historical observations and should not be treated as a guaranteed future value.

---

## Key Engineering Features

### Multi-Agent Architecture

The system separates responsibilities across specialized agents instead of placing the entire workflow inside one large prompt.

### Deterministic Financial Calculations

Core financial metrics are calculated from SQL/database operations rather than generated by the LLM.

### Controlled SQL Generation

The SQL Agent validates generated queries and restricts database interaction to analytical operations.

### Forecast Backtesting

Multiple forecasting methods are evaluated against historical observations before selecting the forecasting method.

### Automated Report Validation

The final report is independently checked against the analytical agent outputs.

### Local + Cloud LLM Architecture

The system supports two execution modes:

```text
Local Development
        │
        ▼
Ollama + Qwen3 8B

Cloud Deployment
        │
        ▼
Google Gemini
```

This allows development and testing locally while supporting a lightweight cloud deployment.

---

## Project Structure

```text
AI-CFO/
│
├── agents/
│   ├── forecast_agent.py
│   ├── insight_agent.py
│   ├── local_llm.py
│   ├── report_agent.py
│   ├── report_validator.py
│   ├── risk_agent.py
│   └── sql_agent.py
│
├── tools/
│   └── database.py
│
├── workflows/
│   ├── graph.py
│   └── state.py
│
├── data/
│   └── financial_deployment.db.gz
│
├── reports/
│
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/AbdelrhmanAkl/AI-CFO-Financial-Intelligence.git
cd AI-CFO-Financial-Intelligence
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the LLM

For local development with Ollama:

```env
LLM_PROVIDER=ollama
DATABASE_NAME=financial.db
```

For Gemini:

```env
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_api_key
```

### 5. Run the application

```bash
streamlit run app.py
```

---

## Cloud Deployment

The application is deployed using **Streamlit Community Cloud**.

The deployment architecture uses:

```text
GitHub
   │
   ▼
Streamlit Cloud
   │
   ├── Streamlit Application
   ├── Google Gemini
   └── Deployment SQLite Database
```

The deployment database is stored in compressed form and extracted automatically when required by the application.

---

## Project Goals

This project was built to demonstrate practical implementation of:

* Agentic AI
* Multi-agent systems
* LLM-powered data analysis
* Natural-language-to-SQL
* Financial analytics
* Risk intelligence
* Statistical forecasting
* Automated report generation
* LLM + deterministic system integration
* AI system validation
* Local and cloud LLM deployment

---

## Limitations

The system is a **financial intelligence and analytics prototype**, not a production financial or compliance system.

Important limitations include:

* The public deployment uses a selected dataset subset.
* Forecasting is based on a limited historical period.
* Risk indicators are analytical signals rather than proof of fraud or financial crime.
* Generated insights and management recommendations require human review.
* The system should not be used as the sole basis for financial, regulatory, or compliance decisions.

---

## Future Improvements

Potential future development includes:

* Real-time transaction ingestion
* More advanced anomaly detection
* Explainable risk scoring
* Time-series models such as Prophet or LSTM
* Interactive transaction investigation
* Persistent analytical memory
* More financial KPIs
* Role-based access control
* Production database integration
* Automated scheduled financial reports
* Human-in-the-loop approval workflows

---

## Author

**Eng.Abdelrahman Akl**

AI Engineer | Agentic AI | LLMs | RAG | Multi-Agent Systems | NLP | Computer Vision

GitHub:
https://github.com/AbdelrhmanAkl

LinkedIn:
https://www.linkedin.com/in/abdelrahmanakl/

---

## License

This project is licensed under the **Apache License 2.0**.

See the `LICENSE` file for details.

---

## Disclaimer

AI CFO is an educational and portfolio project demonstrating AI-powered financial analytics and multi-agent system design.

The outputs are analytical and informational. They are not financial, investment, legal, accounting, or compliance advice.
