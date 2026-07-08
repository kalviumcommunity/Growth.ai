# System Architecture

## Overview

The project follows a data analytics pipeline.

```
Raw Data
    │
    ▼
SQL Database
    │
    ▼
SQL Queries
    │
    ▼
Pandas
    │
    ▼
NumPy Analysis
    │
    ▼
KPIs
    │
    ▼
Dashboard
```

---

## Components

### SQL Database

Stores

- Users
- Sessions
- Feature Usage
- Subscription History

---

### SQL Layer

Responsible for

- Joining tables
- Filtering data
- Aggregating records

---

### Pandas

Responsible for

- Cleaning data
- Removing duplicates
- Handling missing values
- Data transformation

---

### NumPy

Responsible for

- Statistical calculations
- Percentage calculations
- Numerical analysis

---

### Dashboard

Displays

- Conversion
- Engagement
- Feature adoption
- Retention