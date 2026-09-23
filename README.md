# EPC Supply Chain Logistics ETL & Tag Unpacker Pipeline

An end-to-end Python-based ETL pipeline designed for complex EPC (Engineering, Procurement, Construction) supply chain logistics and procurement tracking. It unifies, cleans, and standardizes equipment, material tag numbers, and vendor documentation across disparate tracking reports and files (PSR, ESR, SSR, VDR, VDB, Spare Parts lists, etc.).

---

## 📌 Business Value & Objectives

This project addresses key supply chain management and site delivery operational challenges by serving two core target groups:

* **1. Operations & Construction Teams (External Focus / On-Site Transparency):**
  * Provides real-time visibility into material location, transit status, and estimated arrival dates (ETA) at the construction site.
  * Eliminates site downtime caused by missing or unverified equipment tags during installation.

* **2. Procurement, Expediting, Logistics & Management (Internal Focus / Control & Risk Mitigation):**
  * **Risk & Delay Control:** Identifies shipment bottlenecks and fabrication delays at vendor workshops.
  * **Documentation & Spare Parts Verification:** Streamlines the tracking of Vendor Data Books (VDB) and 2-year operational spare parts readiness before final handover.
  * **Data Integration:** Reconciles contractor reports using automated tag unpacking and fuzzy matching, replacing hundreds of hours of manual VLOOKUP/Excel checks.


---

## 📌 Business Problem

In major industrial construction projects, vendor tracking reports often contain inconsistent equipment tagging formats:
* **Ranges & Lists:** Tags provided as ranges (e.g., `10-P-101A-D`, `20-V-001/002/003`) or multi-line strings within a single cell.
* **Format Variations:** Inconsistent naming conventions between Procurement (PSR), Expediting (ESR), and Shippment Delivery (SSR) reports.
* **Data Quality Issues:** Non-standard characters, typos, and corrupted inputs leading to broken tracking reconciliations.

This pipeline automates the extraction, expansion, cleaning, and fuzzy matching of tags to produce a single, unified `Master_Tags` dataset for downstream Power BI reporting.

---

## 🚀 Key Features

* **Advanced Tag Expansion (`tag_unpacker.py`):**
  * Expands hyphenated ranges (`10-P-101A-D` $\rightarrow$ `10-P-101A`, `10-P-101B`, `10-P-101C`, `10-P-101D`).
  * Parses multi-line cells and slash/comma-separated lists.
  * Filters out corrupted tags (e.g., non-Latin strings, invalid characters).
* **Automated Reconciliation (`generic_matching_pipeline.py`):**
  * Implements fuzzy string matching via `RapidFuzz` to handle slight naming discrepancies across contractor submissions.
* **Error & Exception Logging:**
  * Automatically isolates problematic/corrupted tag rows into `tags_to_fix.xlsx` for manual site team review while continuing automated pipeline execution.

---

## 📊 Power BI Visualization & Executive Dashboards

The consolidated `Master_Tags` dataset serves as the relational data foundation for an interactive multi-page Power BI executive tracking suite:

* **Executive Summary & Financial Status:** High-level KPI metrics, S-Curve progress tracking, and risk breakdown by project discipline.
* **Material Tracking & Search:** Detailed cross-report reconciliation (PSR, ESR, SSR) enabling site teams to locate specific tag numbers and arrival dates (ETA).
* **Vendor Data Book (VDB) Control:** Specialized interface for tracking documentation approval statuses, missing technical passports, and vendor comments.
* **Data Model Architecture:** Optimized star schema featuring bridge tables (`PSR Bridge`, `ESR Bridge`, `SSR Bridge`) and normalized tag keys for high-performance filtering.

### Dashboard Overview
*(Anonymized Executive Views)*

#### 1. Executive Summary & Progress Tracking
![Executive Summary](docs/01_executive_summary.png)

#### 2. Detailed Material & Tag Search
![Material Search](docs/02_material_search.png)

#### 3. Vendor Data Book (VDB) Control
![VDB Control](docs/03_vdb_control.png)

#### 4. Power BI Data Model Architecture
![Data Model](docs/04_data_model.png)

---

## 📁 Repository Structure

supply_chain_logistics_etl/
├── data/
│   ├── psr_sample.xlsx       # Anonymized Procurement Status Report sample
│   ├── esr_sample.xlsx       # Anonymized Expediting Status Report sample
│   ├── ssr_sample.xlsx       # Anonymized Site Status Report sample
│   └── output/
│       ├── unpacked_tags_from_reports.xlsx  # Cleaned & extracted Master Tags
│       └── tags_to_fix.xlsx                 # Isolated parsing exceptions
├── src/
│   ├── tag_unpacker.py              # Parsing & string manipulation logic
│   ├── generic_matching_pipeline.py # Fuzzy matching pipeline logic
│   └── run_unpacker_pipeline.py     # Main execution script
├── .gitignore
├── README.md
└── requirements.txt