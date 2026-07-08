# Database Design

## Tables

### Users

| Column | Description |
|---------|-------------|
| user_id | User ID |
| signup_date | Registration date |
| country | Country |
| plan | Trial/Paid |

---

### Sessions

| Column | Description |
|---------|-------------|
| session_id | Session ID |
| user_id | User ID |
| login_time | Login |
| logout_time | Logout |

---

### Feature Usage

| Column | Description |
|---------|-------------|
| feature_id | Feature ID |
| user_id | User ID |
| feature_name | Used feature |
| timestamp | Event time |

---

### Subscription

| Column | Description |
|---------|-------------|
| subscription_id | Subscription ID |
| user_id | User ID |
| upgrade_date | Upgrade date |
| plan | Paid plan |

---

## Relationships

Users

↓

Sessions

↓

Feature Usage

↓

Subscription