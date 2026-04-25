# FairLens ⚖️

FairLens is an India-first AI bias auditing dashboard designed to detect invisible socio-cultural proxies in hiring and lending datasets. 

While traditional AI fairness tools are hardcoded to detect Western-centric biases like race or age, FairLens specifically targets proxy variables relevant to the Indian context, such as caste-indicative surnames and regional pincodes. 

This tool provides a zero-code interface for HR managers and non-technical decision-makers to audit their data and receive actionable, plain-English fixes before deploying AI models. Built for the Google Solution Challenge 2026.

## The Problem
Biased AI is a black box. Currently, checking a dataset for bias requires a data science background. Furthermore, an AI might not explicitly discriminate against a protected class, but it will use highly correlated proxy variables (like a candidate's hometown or surname) to make biased decisions. 

## The Solution
FairLens acts as a cultural translator for Responsible AI. It calculates standard mathematical fairness metrics (like the Disparate Impact Ratio) and feeds them into Google Gemini 1.5 Flash to generate human-readable audit reports.

## Key Features
* **Drag-and-Drop Audit:** Instant CSV processing with no Python scripting required.
* **Proxy Detection:** Automatically flags sensitive variables alongside Indian socio-cultural proxies (Surnames, Pincodes).
* **The FairLens Score:** A unified 0-100 metric based on the 80% rule (Disparate Impact).
* **Gemini AI Insights:** Translates raw statistical ratios into actionable, plain-English fix recommendations.

## Tech Stack
* **Frontend & Logic:** Streamlit, Python 3
* **Data Processing:** Pandas
* **Visualization:** Plotly Express
* **AI Ethics Engine:** Google Gemini 1.5 Flash API

## How to Run Locally

1. Clone the repository:
   ```bash
   git clone [https://github.com/yourusername/FairLens.git](https://github.com/yourusername/FairLens.git)
   cd FairLens
