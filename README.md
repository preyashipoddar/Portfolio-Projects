**Portfolio Projects**

**🦠 Flu Hospital Admissions Forecast & Staffing Dashboard**

[![Repository](https://img.shields.io/badge/View-Repository-blue)](https://github.com/preyashipoddar/flu-admissions-forecast) [![Dashboard](https://img.shields.io/badge/View-Live%20Dashboard-orange)](https://public.tableau.com/views/FluStaffingOutlookUS/FluStaffingOutlookUS)

Four-week-ahead forecasts of weekly US flu hospital admissions with calibrated uncertainty ranges, evaluated the way CDC scores its own FluSight forecasting challenge and translated into a nurse staffing decision. Forecasting from data as it was first published, a linear model pooled across 53 states and territories scored 37% better than CDC's baseline on CDC's weighted interval score, within 0.04 of CDC's multi-team ensemble, with 82% of outcomes landing inside its 80% uncertainty range (ensemble: 78%).

Tech Stack: Python, pandas, statsmodels, NumPy, GitHub Actions, Google Sheets API, Tableau Public

Key Features

Rolling-origin backtest on 51 forecast dates using CDC's archive of 98 data versions, so each forecast used only the data available that week
Weekly monitoring job that logs forecasts before outcomes are known, scores them once data settles, and alerts if the model stops beating a seasonal baseline
Staffing-cost analysis across overtime and agency cost scenarios from published nurse wage data: 23-35% cheaper than CDC's baseline at every scenario
Self-updating Tableau Public dashboard fed by the weekly pipeline: forecast fan chart, track record of past forecasts, and a cost-ratio slider for staffing decisions

**🛡️ PaperShield - AI Contract Risk Analysis**

[![Repository](https://img.shields.io/badge/View-Repository-blue)](https://github.com/preyashipoddar/papershield)

An AI-powered contract analysis tool that identifies legal risks using Retrieval-Augmented Generation (RAG), combining vector search with large language models to provide structured risk assessments, clause explanations, and natural language question answering.

Tech Stack: Python, LangChain, GPT-4o, pgvector, PostgreSQL, Docker, Tavily API

**🏦 Modern Banking Data Platform**

[![Repository](https://img.shields.io/badge/View-Repository-blue)](https://github.com/preyashipoddar/banking-modern-datastack)

An end-to-end data engineering pipeline simulating a modern banking data stack. The project captures transactional changes from PostgreSQL using Change Data Capture (CDC), streams events through Kafka, stores raw data in a MinIO data lake, loads data into Snowflake, transforms it with dbt, orchestrates workflows with Airflow, and visualizes insights in Power BI.

Tech Stack: PostgreSQL, Debezium, Kafka, MinIO (S3), Snowflake, dbt, Airflow, Python, GitHub Actions, Power BI

Key Features

Built staging, dimensional, fact, and SCD Type 2 snapshot models using dbt
Implemented Airflow DAGs for scheduled ingestion and transformation workflows
Added CI/CD with GitHub Actions for automated dbt validation and deployment
Developed Power BI dashboards for customer, account, and transaction analytics

**🎵 Spotify Hit Prediction - Data Analytics & Machine Learning**

Built a machine learning model to predict Spotify song stream counts using a Kaggle dataset. The project includes exploratory data analysis, feature engineering, regression modeling (Linear Regression, Random Forest, Gradient Boosting, XGBoost), and a detailed project report.

Dataset: https://www.kaggle.com/datasets/nelgiriyewithana/top-spotify-songs-2023

**🦠 COVID-19 Data Exploration (SQL)**

Explored global COVID-19 trends using SQL, performing data cleaning, aggregations, joins, CTEs, and windowed rolling aggregates to prepare datasets for visualization.

**📊 COVID-19 Tableau Dashboard**

Interactive Tableau dashboard exploring COVID-19 cases, deaths, and regional trends.

https://public.tableau.com/views/CovidCasesDashboard_17200186679140/Dashboard1?:language=en-US&publish=yes&:sid=&:display_count=n&:origin=viz_share_link

**📈 Data Professional Survey Dashboard (Power BI)**

Interactive Power BI dashboard analyzing survey responses from data professionals.

Key Findings

630 survey participants across 5 countries
Average participant age: 29.87 years
Python was the most commonly used programming language

Features

Interactive drill-downs by gender and job role
DAX measures for demographic and salary analysis
Dynamic filtering and cross-visual interactions
