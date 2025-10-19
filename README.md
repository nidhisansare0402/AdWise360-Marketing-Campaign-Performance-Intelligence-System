# AdWise360-Marketing-Campaign-Performance-Intelligence-System
**“AdWise360 – Turning raw marketing data into actionable intelligence for smarter ad decisions.”**

### Problem Statement

Digital marketing teams handle large, unstructured, and isolated datasets from multiple ad platforms.
Manually analyzing these to understand ROI, CTR, or conversion trends is time-consuming and error-prone.
AdWise360 aims to automate this process by providing a **centralized, intelligent performance tracking and prediction platform**.

### Overview

**AdWise360** is an end-to-end **marketing analytics and intelligence system** designed to help organizations to analyze, predict, and optimize digital ad campaign performance.
The system brings together **data engineering**, **data analytics**, and **machine learning** to deliver a **360° view of campaign effectiveness** across platforms such as **Google Ads, Facebook Ads, and YouTube**.

### Project Goals

- Design a **realistic, normalized marketing database schema** in MySQL.  
- Analyze campaign KPIs like CTR, CPC, CPA, and ROI.  
- Build an ML-ready structure to predict campaign performance (High / Low).  
- Create insights that connect marketing analytics with data science.

### Entity Relationship Diagram (ERD)

Here’s the database structure of the AdWise360 project:

<p align="center">
  <img src="database/ERD_AdWise360.png" alt="AdWise360 ER Diagram" width="600"/>
</p>

### Tech Stack

| Layer | Technology Used |
|--------|----------------|
| **Database** | MySQL Workbench |
| **Backend/Analysis** | Python (pandas, NumPy, scikit-learn) |
| **Visualization** | Matplotlib, Seaborn |
| **Documentation** | Word |
| **Version Control** | Git & GitHub |
| **ERD Design Tool** | [dbdiagram.io](https://dbdiagram.io/) |

#### Tables Overview

| Table | Description |
|--------|--------------|
| **platforms** | Stores ad platform details (Google Ads, Facebook Ads, etc.) |
| **campaigns** | Contains campaign info like name, objective, region, and budget |
| **metrics** | Holds daily performance data — impressions, clicks, conversions, spend, and revenue |
| **predictions** | Stores machine learning results (performance category, confidence score) |

### Folder Structure

AdWise360/
│
├── database/
│ ├── adwise360_schema.sql
│ ├── adwise360_test_data.sql
│ └── ERD_AdWise360.png
│
├── docs/
│ ├── Day1_Marketing_Analytics_Interview_Notes.docx
│ ├── Day2_Database_Design_Interview_Notes.docx
│
└── README.md


