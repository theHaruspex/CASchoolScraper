# California School Data Scraper & Lead Generation

> **Project Type**: One-time Data Scraping & Normalization Pipeline  
> **Author**: Derious Vaughn  
> **Last Updated**: February 15th, 2025

---

## Table of Contents
1. [Overview](#overview)  
2. [Use Cases](#use-cases)  
3. [Case Study Insights](#case-study-insights)  
4. [Data Pipeline Architecture](#data-pipeline-architecture)  
5. [Installation & Setup](#installation--setup)  
6. [Running the Pipeline](#running-the-pipeline)  
7. [Data Privacy & Compliance](#data-privacy--compliance)  
8. [Sample Data Only](#sample-data-only)  
9. [Success Metrics](#success-metrics)  
10. [Future Enhancements](#future-enhancements)  
11. [Acknowledgments](#acknowledgments)  

---

## Overview
This repository contains a **Python-based pipeline** that:

- **Scrapes** the official California school directory (approximately 13,000 schools).  
- **Normalizes** the data (addresses, contact info, standardized fields).  
- **Enriches** each record with **demographic data** (e.g., black population ratio in the school’s city).  
- **Generates** an **Excel spreadsheet** separating **public** and **private** schools, complete with contact details and a composite or ranking score for lead generation.

**Why?**  
- **Shades of Color**: A black-owned company seeking to expand its fundraising program, targeting schools in areas with significant black populations.  
- **Educational Consulting Startup**: Identifying prospective school clients for consulting services, with a particular focus on private schools (faster decision cycles).

---

## Use Cases

### Shades of Color
- **Objective**: Identify schools (especially private) more likely to partner for fundraising.  
- **Reasoning**: Private schools can make decisions quickly; demographic data (black population ratio) helps align outreach with the company’s audience.  
- **Outcome**: A CRM-friendly spreadsheet listing school details, contact info, and demographic metrics.

### Educational Consulting Startup
- **Objective**: Garner a list of schools (both public and private) that may need consulting.  
- **Reasoning**: The composite and ranking scores highlight high-enrollment schools in relevant demographic areas.  
- **Outcome**: A single spreadsheet for import into a CRM or further segmentation.

---

## Case Study Insights
This repository is not only a functional **data-scraping pipeline** but also a demonstration of **engineering best practices** and **problem-solving skills**:

1. **Real-World Business Context**  
   - Serving *Shades of Color* (fundraising expansion) and an *Educational Consulting Startup*, showing how data engineering solutions solve practical lead-generation problems.

2. **Modular Architecture**  
   - Each stage (Scraper, Normalizer, Demographics, Spreadsheet) is isolated, making code easier to maintain, test, and extend.

3. **Scalable & Extensible**  
   - The pipeline can handle thousands of schools and integrate new data sources (like Hispanic demographics) with minimal refactoring.

4. **Validation & Quality Checks**  
   - Success metrics explicitly track **accuracy** and **completeness**, reflecting real-world QA processes.  
   - Spot-checking ensures data reliability before final handoff to outreach teams or CRMs.

5. **Practical Deliverable**  
   - The final Excel file is CRM-friendly, enabling direct import.  
   - Employers can see how data flows from raw scraping → standardized records → advanced analytics.

6. **Technical Fluency**  
   - Showcases proficiency in Python, library usage (e.g., `usaddress`, `pandas`), BeautifulSoup parsing, and environment setup.

---

## Data Pipeline Architecture

1. **Scraper**  
   - Pulls data from the California School Directory.  
   - Collects essential details: name, address, phone, and administrator contacts.
   - Offers a **test mode** (10 schools only) for quick demonstration.

2. **Normalizer**  
   - Cleans addresses (usaddress), standardizes fields, merges multi-layer data.  

3. **Demographic Calculator**  
   - Loads city-level demographic data (e.g., black population from IRS/census sources).  
   - Enriches each school record with a “Black Population Ratio.”

4. **Spreadsheet Builder**  
   - Splits data into **public** vs. **private** schools.  
   - **Public**: Calculates a “Composite Score” combining enrollment size and black population ratio.  
   - **Private**: Uses black population ratio as a “Ranking Score.”  
   - Outputs to an Excel workbook with separate sheets.

---

## Installation & Setup

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/theHaruspex/CA-School-Scraper.git
   cd CA-School-Scraper
   ```

2. **Install Requirements**  
   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional) Create a Virtual Environment**  
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scriptsctivate on Windows
   pip install -r requirements.txt
   ```

---

## Running the Pipeline

```bash
python pipeline.py
```

- Generates the full dataset (~13,000 schools).
- Outputs an Excel file (`School_Outreach_Contacts.xlsx`).
- Use **test mode** for smaller runs (~10 schools).

---

## Data Privacy & Compliance

- **Publicly Available Data**: No student-level PII, all administrator emails are professional/public.  
- **Compliance Considerations**: If using this for outreach, comply with **CAN-SPAM** & local laws.  
- **Test Mode Sample**: The repository contains a **10-school** sample only.

---

## Sample Data Only

- This repo **excludes** the full 13,000-school dataset (~98MB).  
- A **sample** of ~10 schools is provided for **testing** and **demonstration**.  

---

## Future Enhancements

- **Expand Demographics**: Add Hispanic/other data.  
- **Geographic Expansion**: Support for nationwide scraping.  
- **Email Outreach Integration**: Direct CRM/email API connections.

---

## Acknowledgments
- **California Department of Education** for the school directory data.  
- **Public IRS/City Data** for demographic information.  
- **Contributors** for refactoring and modularizing the code.

---
