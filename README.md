# California School Data Scraper & Lead Generation (Case Study)

> **Project Type**: One-time Data Scraping & Normalization Pipeline  
> **Author**: *Derious Vaughn / theHaruspex*  
> **Last Updated**: *February 15th, 2025*  

---

## Table of Contents
1. Overview
2. Use Cases / Case Study
3. Data Pipeline Architecture
4. Installation & Setup
5. Running the Pipeline
6. Data Privacy & Compliance
7. Sample Data Only
8. Success Metrics
9. Future Enhancements
10. Acknowledgments

---

## Overview
This repository contains a **Python-based pipeline** that:
- **Scrapes** the official California school directory.
- **Normalizes** the resulting data (cleaning addresses, extracting administrator contacts).
- **Enriches** each school record with **demographic data** (e.g., black population ratio in the school’s city).
- **Generates** an **Excel spreadsheet** separating public and private schools, complete with contact info and a composite score (or ranking score) for lead generation.

**Why?**  
- **Shades of Color**: A black-owned company looking to expand its fundraising program, targeting schools with significant black populations and straightforward decision-making processes.  
- **Educational Consulting Startup**: Seeking to identify prospective school clients for consulting services, with a particular focus on private schools (which often have fewer bureaucratic hurdles).

---

## Use Cases / Case Study

### Shades of Color
- **Objective**: Identify schools (especially private) that are more likely to partner for fundraising programs.
- **Reasoning**: Private schools can quickly make decisions; city-level black population data helps align outreach with the company’s main audience.
- **Output**: A CRM-friendly spreadsheet separating public vs. private leads, listing administrator emails/phones for direct contact.

### Educational Consulting Startup
- **Objective**: Acquire a leads list of schools (both public and private) that may need consulting services.
- **Reasoning**: The composite/ranking scores highlight high-enrollment schools (potentially larger budgets) in cities with relevant demographics.
- **Output**: A single spreadsheet to import into a CRM or further refine.

---

## Data Pipeline Architecture
1. **Scraper**  
   - Scrapes ~13,000+ California schools from the official directory.  
   - Captures school name, address, phone, possible administrator contacts, etc.

2. **Normalizer**  
   - Cleans up addresses, merges multi-layer data, standardizes fields (e.g., “County,” “School,” etc.).
   - Introduces a test mode (limited to 10 schools) for quick demos.

3. **Demographic Calculator**  
   - Cross-references city-level data (e.g., black population) from a public CSV source.  
   - Injects a **“Black Population Ratio”** into each school’s record.

4. **Spreadsheet Builder**  
   - Separates **public** vs. **private** schools.  
   - **Public**: A “Composite Score” = 0.5 * (normalized enrollment) + 0.5 * (black population ratio).  
   - **Private**: A “Ranking Score” = black population ratio.  
   - Produces an **Excel file** (two sheets) with contact columns, phone, email, etc.

---

## Installation & Setup

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/your-username/CA-School-Scraper.git
   cd CA-School-Scraper
   ```

2. **Install Requirements**  
   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional) Create Virtual Environment**  
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

---

## Running the Pipeline

1. **Main Pipeline**  
   Run everything (scrape → normalize → demographic → spreadsheet):
   ```bash
   python pipeline.py
   ```

   - **Note**: This will attempt to scrape all 13,000+ schools (generating a large dataset).

2. **Test Mode**  
   If you only want to handle 10 schools:
   ```bash
   # Edit pipeline.py or DirectoryScraper init to test_mode=True
   python pipeline.py
   ```

   - This creates a much smaller dataset (~10 schools) for quick demos.

3. **Output**  
   - Final output is an Excel file named `School_Outreach_Contacts.xlsx` in the project root (configurable).
   - You can find intermediate JSON files in the `data/` subdirectories (ignored by default in `.gitignore`).

---

## Data Privacy & Compliance

1. **Publicly Available Data**  
   - All school info (names, addresses, admin emails) is taken from **public** directories and websites.  
   - City-level demographic data is also publicly accessible (no private or student-level info is collected).

2. **Email Compliance**  
   - If using these contacts for **outreach** or **marketing** (e.g., mass emailing), ensure you follow **CAN-SPAM** or other relevant regulations in your jurisdiction.

3. **Data Privacy Notice**  
   - No personal or private student data is collected.
   - Administrator contact details are **institutional/professional** and publicly listed.
   - For demonstration, only **10-school** sample data is committed to this repo.

---

## Sample Data Only
- This repository **does not** include the full 13,000-school JSON dataset (~98MB).  
- A small **sample** of ~10 schools is provided for **testing** and **demonstration**.  
- **If you want the entire dataset**:
  - Remove or modify the `.gitignore` entries.
  - Run `pipeline.py` in full mode (i.e., `test_mode=False`).
  - Be aware of large storage requirements (~100MB of JSON).

---

## Success Metrics
Since this project focuses on **data scraping and lead generation**, success is measured by:
1. **Accuracy**:  
   - Are addresses and administrator emails correct and properly formatted?  
   - Does the city-level demographic data match each school’s location?
2. **Completeness**:  
   - Are nearly all schools in the official CA directory captured?  
   - Is each record enriched with a “Black Population Ratio” (or `None` if data is unavailable)?
3. **Output Format**:  
   - The final Excel spreadsheet must be **CRM-friendly** (easy to import) and separate public/private schools on different sheets.

---

## Future Enhancements
1. **Hispanic or Other Demographics**  
   - The pipeline can be extended to incorporate more ethnicity or socioeconomic data.
2. **Geographic Expansion**  
   - Potentially adapt the scraper to other states or national directories.
3. **Integrated Email Outreach**  
   - Pair this leads data with an email API (like Gmail API) for direct, automated campaigns.

---

## Acknowledgments
- **California Department of Education** for the original school directory data.  
- **Public IRS/City Data** sources for demographic information.  

**Questions or Comments?**  
Feel free to open an Issue or PR if you’d like to improve the pipeline or add new demographic layers!
