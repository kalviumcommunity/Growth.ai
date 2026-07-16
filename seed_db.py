from __future__ import annotations

import os
import random
from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy import create_engine

from growth_ai.config import get_settings


def generate_mock_data():
    print("Generating mock analytics data...")
    random.seed(42)

    # Generate Users
    num_users = 100
    start_date = datetime(2026, 1, 1)

    user_ids = [f"usr_{i:03d}" for i in range(1, num_users + 1)]
    signup_dates = [start_date + timedelta(days=random.randint(0, 90)) for _ in range(num_users)]
    countries = ["US", "CA", "GB", "DE", "FR", "IN", "JP", "AU"]
    user_countries = [random.choice(countries) for _ in range(num_users)]

    # We will initially label all users as trial or paid.
    # In the app, subscriptions table is what dictates who is 'paid' in KPI calculations.
    # So we set initial plan as 'trial' for most, and some as 'trial' but they upgrade later.
    user_plans = []
    upgraded_user_ids = []

    # Let's say 30% of users upgraded
    for i, u_id in enumerate(user_ids):
        if i % 3 == 0:
            user_plans.append("paid")
            upgraded_user_ids.append(u_id)
        else:
            user_plans.append("trial")

    df_users = pd.DataFrame(
        {
            "user_id": user_ids,
            "signup_date": [d.strftime("%Y-%m-%d %H:%M:%S") for d in signup_dates],
            "country": user_countries,
            "plan": user_plans,
        }
    )

    # Generate Subscriptions for upgraded users
    sub_ids = [f"sub_{i:03d}" for i in range(1, len(upgraded_user_ids) + 1)]
    upgrade_dates = []
    for u_id in upgraded_user_ids:
        # Find signup date
        idx = user_ids.index(u_id)
        signup_d = signup_dates[idx]
        upgrade_d = signup_d + timedelta(days=random.randint(2, 14))
        upgrade_dates.append(upgrade_d)

    df_subscriptions = pd.DataFrame(
        {
            "subscription_id": sub_ids,
            "user_id": upgraded_user_ids,
            "upgrade_date": [d.strftime("%Y-%m-%d %H:%M:%S") for d in upgrade_dates],
            "plan": ["Paid"] * len(upgraded_user_ids),
        }
    )

    # Generate Sessions
    sessions = []
    session_counter = 1
    features = [
        "Dashboard",
        "Export PDF",
        "Advanced Filters",
        "Billing Settings",
        "API Integrations",
        "User Management",
    ]
    feature_usages = []
    feature_counter = 1

    for idx, u_id in enumerate(user_ids):
        signup_d = signup_dates[idx]
        is_upgraded = u_id in upgraded_user_ids
        upgrade_d = upgrade_dates[upgraded_user_ids.index(u_id)] if is_upgraded else None

        # Active period: trial is 14 days, paid users can active up to 180 days
        num_sessions = random.randint(5, 40) if is_upgraded else random.randint(1, 8)

        current_time = signup_d
        for _ in range(num_sessions):
            # Session start
            current_time += timedelta(
                days=random.randint(0, 5),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )
            # Caps the session simulation range
            if current_time > datetime(2026, 7, 1):
                break

            session_len_min = random.randint(2, 60)
            logout_time = current_time + timedelta(minutes=session_len_min)

            s_id = f"sess_{session_counter:05d}"
            sessions.append(
                {
                    "session_id": s_id,
                    "user_id": u_id,
                    "login_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "logout_time": logout_time.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
            session_counter += 1

            # Generate feature usages during this session
            num_features = random.randint(1, 5)
            session_features = random.sample(features, k=min(num_features, len(features)))
            for f_name in session_features:
                f_time = current_time + timedelta(
                    minutes=random.randint(1, session_len_min - 1) if session_len_min > 2 else 1
                )
                feature_usages.append(
                    {
                        "feature_id": f"feat_{feature_counter:06d}",
                        "user_id": u_id,
                        "feature_name": f_name,
                        "timestamp": f_time.strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )
                feature_counter += 1

    df_sessions = pd.DataFrame(sessions)
    df_features = pd.DataFrame(feature_usages)

    print(f"Generated {len(df_users)} users.")
    print(f"Generated {len(df_subscriptions)} subscriptions.")
    print(f"Generated {len(df_sessions)} sessions.")
    print(f"Generated {len(df_features)} feature usage events.")

    return df_users, df_sessions, df_features, df_subscriptions


def main():
    settings = get_settings()

    # Ensure data directory exists
    db_path = settings.database_url
    if db_path.startswith("sqlite:///"):
        sqlite_file_path = db_path.replace("sqlite:///", "")
        dir_name = os.path.dirname(sqlite_file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

    engine = create_engine(settings.database_url)

    df_users, df_sessions, df_features, df_subscriptions = generate_mock_data()

    # Write to SQL database
    print(f"Writing to database: {settings.database_url}...")
    df_users.to_sql("users", engine, if_exists="replace", index=False)
    df_sessions.to_sql("sessions", engine, if_exists="replace", index=False)
    df_features.to_sql("feature_usage", engine, if_exists="replace", index=False)
    df_subscriptions.to_sql("subscriptions", engine, if_exists="replace", index=False)

    print("Database seeding completed successfully!")


if __name__ == "__main__":
    main()
