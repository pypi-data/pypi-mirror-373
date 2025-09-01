# Ferma Congress
FermaCongress is a private Python package used internally by the Planners team at ZoomRx - Ferma Congress to automate extraction and management of congress-level data. The package provides utilities for Authentication, Session & Tweet Management, Annotation & Social Workflows

## **Installation**

```bash
pip install FermaCongress

# upgrade to the latest version
pip install --upgrade FermaCongress
```

---

# 🔐 **FermaCongress.auth**

To access Ferma, you must provide a `.env` file containing your authorized Ferma credentials.

| Function         | Description                                                                     |
| ---------------- | ------------------------------------------------------------------------------- |
| `adminlogin()`   | Authenticates with the **Ferma Admin Portal** and enables access to its APIs    |
| `supportlogin()` | Authenticates with the **Ferma Support Portal** and maintains an active session |

Both functions expect the following variables in your `.env` file:

```
FERMA_USERNAME=<your-username>
FERMA_PASSWORD=<your-password>
```

### **Quick Start**

```python
from FermaCongress.auth import adminlogin, supportlogin

# Authenticate to the Admin portal
admin_client = adminlogin(".env")

# Authenticate to the Support portal
support_client = supportlogin(".env")
```

### **Environment Variables (.env)**

```env
FERMA_USERNAME=your_username
FERMA_PASSWORD=your_password
```

**Encoded credentials**: If your `.env` file contains Base64-encoded values, simply add the `format="ENCODED"` argument:

```python
admin_client = adminlogin(".env", format="ENCODED")
```

# 🧠 **FermaCongress.annotate**
The `annotate()` function allows you to send a DataFrame to the Ferma **Support Portal** for keyword annotation and download the processed results.

> **Requires an authenticated Ferma Support Portal session** (via `supportlogin()` from `FermaCongress.auth`)


### Function

| Parameter           | Description                                                     |
| ------------------- | --------------------------------------------------------------- |
| `client`            | Authenticated `Session` instance from `supportlogin()` |
| `input_df`          | Pandas DataFrame **with an `id` column**                        |
| `custom_needles_df` | Optional DataFrame of user-defined needles                      |
| `needles`           | List of two ints: `[kb_status, nct_status]`                     |
| `entities`          | Optional entity configuration (dict)                            |
| `long_table`        | Use long table format (`True`) or pivot table format (`False`)  |

### **Quick Example**

```python
from FermaCongress.auth import supportlogin
from FermaCongress.annotate import annotate

# Authenticate to the Support portal
support_client = supportlogin(".env")

# Annotate
annotated_df = annotate(support_client, input_df=input_df, needles=[1, 1], long_table=True)
```

# 📥 FermaCongress.extractferma

This module provides a set of helper functions to extract congress-level data from the Ferma **Admin Portal**.
All functions require an authenticated Admin client (via `adminlogin()` from `FermaCongress.auth`).

### Functions

| Function              | Description                                                              |
| --------------------- | ------------------------------------------------------------------------ |
| `get_all_sessions()`  | Download all session-level metadata for a given congress ID              |
| `get_skg()`           | Download grouped session keyword data                                    |
| `get_fullabstracts()` | Download full abstracts for all sessions                                 |
| `get_summary()`       | Download session summaries                                               |
| `get_tweets()`        | Download tweet-level data and merge with session metadata and priorities |
| `get_priority()`      | Download and merge planner priority files into a consolidated DataFrame  |

---

### Example

```python
from FermaCongress.auth import adminlogin
from FermaCongress.extractferma import (
    get_all_sessions, get_skg, get_fullabstracts,
    get_summary, get_tweets, get_priority
)

# 1) Authenticate to the Admin portal
admin_client = adminlogin(".env")

# 2) Fetch Sessions / Keywords / Tweets
CONGRESS_ID = "221"

sessions_df = get_all_sessions(admin_client, CONGRESS_ID)
skg_df      = get_skg(admin_client, CONGRESS_ID)
abstracts_df = get_fullabstracts(admin_client, CONGRESS_ID)

summary_df  = get_summary(admin_client, CONGRESS_ID)
tweets_df   = get_tweets(admin_client, CONGRESS_ID)
priority_df = get_priority(admin_client, CONGRESS_ID)
```

---

# 🔄 FermaCongress.postferma
This module contains helper functions for posting **tweet-level updates** back to the Ferma Admin Portal and for triggering server-side buzz score recalculation.

### Functions

| Function         | Description                                                            |
| ---------------- | ---------------------------------------------------------------------- |
| `addtweets()`    | Uploads new tweets for a specific congress ID                          |
| `modifytweets()` | Modifies existing tweets for a specific congress ID                    |
| `populatebuzz()` | Triggers the server to populate or update buzz scores for all sessions |

All functions require an authenticated Admin client (`adminlogin()` from `FermaCongress.auth`).

---

### Example

```python
from FermaCongress.auth import adminlogin
from FermaCongress.postferma import addtweets, modifytweets, populatebuzz

client = adminlogin(".env")

CONGRESS_ID = "221"

# Add new tweets
addtweets(client, df, CONGRESS_ID)

# Modify tweets (if needed)
modifytweets(client, df, CONGRESS_ID)

# Recalculate buzz scores
populatebuzz(client, CONGRESS_ID)
```

---

# 🗂️ FermaCongress.planner

The `FermaCongress.planner` module provides utilities for generating congress planning files by combining session metadata, keyword information, and planner-level priorities.

### Functions

| Function        | Description                                                                    |
| --------------- | ------------------------------------------------------------------------------ |
| `baseplanner()` | Builds a fully enriched planning DataFrame for a given Congress and Planner ID |

---

### Example

```python
from FermaCongress.auth import adminlogin
from FermaCongress.planner import baseplanner

# 1) Authenticate to the Admin portal
client = adminlogin(".env")

# 2) Build a planner file
CONGRESS_ID = "221"
PLANNER_ID  = "4"

planner_df = baseplanner(client, CONGRESS_ID, PLANNER_ID)
print(planner_df.head())
```

---

# ⚙️ FermaCongress.formatexcel

The `FormatExcel` utility is used to apply styling and export your Ferma data (from a DataFrame or input file) into a clean, Ferma-styled Excel format.

```python
from FermaCongress.formatexcel import format

format(dataframe=df, output_path="priority_report.xlsx")  # Format from a DataFrame

format(input_path="raw_sessions.xlsx", output_path="formatted_sessions.xlsx")  # Format from Excel file

format(input_path="raw_data.csv", output_path="formatted_output.xlsx")  # Format from CSV file
```


| Parameter      | Type                         | Description                                                                                |
| -------------- | ---------------------------- | ------------------------------------------------------------------------------------------ |
| `input_path`   | `str`                        | Path to an input Excel or CSV file.                                                        |
| `dataframe`    | `pandas.DataFrame`           | DataFrame to format.                                                                       |
| `output_path`  | `str`                        | File path to save the formatted Excel output.                                              |
| `headers`      | `bool`                       | True to convert headers to proper casing (e.g., buzz_score → Buzz Score).                  |
| `input_sheet`  | `str`                        | Name of the sheet to read from (Excel only). Optional if only one sheet.                   |
| `output_sheet` | `str`                        | Name of the sheet to write into in the output Excel file.                                  |

---
