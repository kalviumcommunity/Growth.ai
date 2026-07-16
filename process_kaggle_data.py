from __future__ import annotations

import os

import numpy as np
import pandas as pd
from sqlalchemy import create_engine

from growth_ai.config import get_settings


def main():
    # 1. Paths
    dataset_dir = (
        "/home/scatterzz/.cache/kagglehub/datasets/"
        "rivalytics/saas-subscription-and-churn-analytics-dataset/versions/1"
    )

    accounts_path = os.path.join(dataset_dir, "ravenstack_accounts.csv")
    subscriptions_path = os.path.join(dataset_dir, "ravenstack_subscriptions.csv")
    feature_usage_path = os.path.join(dataset_dir, "ravenstack_feature_usage.csv")

    if not (
        os.path.exists(accounts_path)
        and os.path.exists(subscriptions_path)
        and os.path.exists(feature_usage_path)
    ):
        print(
            "Error: Kaggle dataset files not found. Make sure the dataset was downloaded correctly."
        )
        return

    print("Loading Kaggle CSVs...")
    df_accounts_raw = pd.read_csv(accounts_path)
    df_subscriptions_raw = pd.read_csv(subscriptions_path)
    df_features_raw = pd.read_csv(feature_usage_path)

    print(f"Loaded Accounts: {df_accounts_raw.shape}")
    print(f"Loaded Subscriptions: {df_subscriptions_raw.shape}")
    print(f"Loaded Feature Usage: {df_features_raw.shape}")

    # 2. Process Users table
    # Schema: user_id, signup_date, country, plan
    print("Processing Users table...")
    df_users = pd.DataFrame()
    df_users["user_id"] = df_accounts_raw["account_id"]
    df_users["signup_date"] = pd.to_datetime(df_accounts_raw["signup_date"])
    df_users["country"] = df_accounts_raw["country"]
    # If is_trial is True, plan is 'trial', otherwise 'paid'
    df_users["plan"] = df_accounts_raw["is_trial"].map({True: "trial", False: "paid"})

    # Ensure signup_date is string formatted for SQL
    df_users["signup_date"] = df_users["signup_date"].dt.strftime("%Y-%m-%d %H:%M:%S")

    # 3. Process Subscriptions table
    # Schema: subscription_id, user_id, upgrade_date, plan
    # In the app, subscriptions only lists users who upgraded/are paid.
    # We will filter to non-trial subscriptions (or subscriptions that are Paid tier)
    print("Processing Subscriptions table...")
    # Find records where is_trial is False (actual paid subscriptions)
    df_paid_subs = df_subscriptions_raw[not df_subscriptions_raw["is_trial"]].copy()

    df_subscriptions = pd.DataFrame()
    df_subscriptions["subscription_id"] = df_paid_subs["subscription_id"]
    df_subscriptions["user_id"] = df_paid_subs["account_id"]
    df_subscriptions["upgrade_date"] = pd.to_datetime(df_paid_subs["start_date"]).dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    df_subscriptions["plan"] = "paid"

    # Drop duplicates for subscription_id
    df_subscriptions = df_subscriptions.drop_duplicates(subset=["subscription_id"])

    # 4. Process Feature Usage table
    # Schema: feature_id, user_id, feature_name, timestamp
    print("Processing Feature Usage table...")
    # Join with subscriptions raw to get account_id (user_id)
    df_features_merged = df_features_raw.merge(
        df_subscriptions_raw[["subscription_id", "account_id"]], on="subscription_id", how="inner"
    )

    df_feature_usage = pd.DataFrame()
    df_feature_usage["feature_id"] = df_features_merged["usage_id"]
    df_feature_usage["user_id"] = df_features_merged["account_id"]
    df_feature_usage["feature_name"] = df_features_merged["feature_name"]
    df_feature_usage["timestamp"] = pd.to_datetime(df_features_merged["usage_date"]).dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # 5. Generate Sessions table
    # Schema: session_id, user_id, login_time, logout_time
    print("Generating Sessions table...")
    sessions_list = []
    session_id_counter = 1

    # First: Group feature usages by user_id and usage_date to form a session
    df_features_merged["usage_date_parsed"] = pd.to_datetime(df_features_merged["usage_date"])
    grouped = df_features_merged.groupby(["account_id", "usage_date"])

    # We will also track which users have at least one session
    users_with_sessions = set()

    for (user_id, usage_date), group in grouped:
        users_with_sessions.add(user_id)
        # Sum duration, default to random duration if missing or 0
        total_duration_secs = group["usage_duration_secs"].sum()
        if pd.isna(total_duration_secs) or total_duration_secs <= 0:
            duration_mins = np.random.randint(5, 45)
        else:
            duration_mins = int(total_duration_secs / 60)
            if duration_mins < 2:
                duration_mins = 2
            elif duration_mins > 120:
                duration_mins = 120

        # Generate login time at a random hour on that day
        hour = np.random.randint(8, 20)
        minute = np.random.randint(0, 59)
        second = np.random.randint(0, 59)

        login_time = pd.to_datetime(usage_date) + pd.Timedelta(
            hours=hour, minutes=minute, seconds=second
        )
        logout_time = login_time + pd.Timedelta(minutes=duration_mins)

        sessions_list.append(
            {
                "session_id": f"sess_{session_id_counter:06d}",
                "user_id": user_id,
                "login_time": login_time.strftime("%Y-%m-%d %H:%M:%S"),
                "logout_time": logout_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
        session_id_counter += 1

    # Second: For users who do NOT have any feature usage, create a session on their signup date
    all_user_ids = df_accounts_raw["account_id"].unique()
    for user_id in all_user_ids:
        if user_id not in users_with_sessions:
            # Find signup date
            signup_d_str = df_accounts_raw.loc[
                df_accounts_raw["account_id"] == user_id, "signup_date"
            ].values[0]
            signup_d = pd.to_datetime(signup_d_str)

            # Start session at 10 AM on signup date
            login_time = signup_d + pd.Timedelta(hours=10)
            logout_time = login_time + pd.Timedelta(minutes=np.random.randint(5, 20))

            sessions_list.append(
                {
                    "session_id": f"sess_{session_id_counter:06d}",
                    "user_id": user_id,
                    "login_time": login_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "logout_time": logout_time.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
            session_id_counter += 1

    df_sessions = pd.DataFrame(sessions_list)

    # 6. Write tables to the database
    settings = get_settings()
    # Ensure reports/data directories exist
    settings.ensure_directories()

    db_path = settings.database_url
    if db_path.startswith("sqlite:///"):
        sqlite_file_path = db_path.replace("sqlite:///", "")
        dir_name = os.path.dirname(sqlite_file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

    print(f"Connecting to database: {settings.database_url}")
    engine = create_engine(settings.database_url)

    print("Writing Users table to SQL...")
    df_users.to_sql("users", engine, if_exists="replace", index=False)

    print("Writing Subscriptions table to SQL...")
    df_subscriptions.to_sql("subscriptions", engine, if_exists="replace", index=False)

    print("Writing Feature Usage table to SQL...")
    df_feature_usage.to_sql("feature_usage", engine, if_exists="replace", index=False)

    print("Writing Sessions table to SQL...")
    df_sessions.to_sql("sessions", engine, if_exists="replace", index=False)

    print("\nProcessing completed successfully!")
    print("Total rows written:")
    print(f"- users: {len(df_users)}")
    print(f"- subscriptions: {len(df_subscriptions)}")
    print(f"- feature_usage: {len(df_feature_usage)}")
    print(f"- sessions: {len(df_sessions)}")


if __name__ == "__main__":
    main()
