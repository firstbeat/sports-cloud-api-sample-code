#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "pyjwt",
#     "requests",
#     "rich",
# ]
# ///
"""
Sports Cloud API code sample

Purpose of this file is to provide examples and explain how the API works.

* This code sample is *not* intended to be an example implementation of an API client for Firstbeat Sports Cloud API.
* For this reason the examples miss basic things like error handling, request pagination, proper project structure etc.
* Examples in this file don't cover all the possible use cases.

There are comments in the file but studying the official documentation is a mandatory prerequisite to understand the API.
"""

import argparse
import os
import sys
import rich

import cloudapiclient

def select_account(accounts: list) -> str:
    """
    Select account from the list of accounts.
    
    One API consumer can be connected to several Firstbeat Sports customer accounts. 
    
    If the returned list is empty, your API consumer doesn't have access to any customer accounts.
    To add accounts, please contact Firstbeat Sports Cloud API support as there are two steps to get access:
    
    1) Firstbeat needs to add you access to the customer account.
    2) Owner of the customer account needs to approve the access to their data.

    Args:
        accounts (list): Accounts
    Returns:
        str: Account ID
    """
    if not accounts:
        print("No accounts found. Please contact support to get access to customer accounts.")
        sys.exit(0)

    if len(accounts) == 1:
        print(f"Using the only available account: {accounts[0]['name']}")
        return accounts[0]['accountId']

    print("\nAvailable Accounts:")
    for i, account in enumerate(accounts):
        print(f"{i+1}. {account['name']}")

    while True:
        try:
            selection = input(f"\nSelect account (1-{len(accounts)}): ")
            index = int(selection)
            if 1 <= index <= len(accounts):
                return accounts[index-1]['accountId']
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a number.")

def select_athlete(athletes: list) -> str:
    """
    Select athlete from the list of athletes

    Args:
        athletes (list): athletes
    Returns:
        str: athlete ID
    """
    if not athletes:
        print("No athletes found in this account.")
        sys.exit(0)

    if len(athletes) == 1:
        print(f"Using the only available athlete: {athletes[0]['firstName']} {athletes[0]['lastName']}")
        return athletes[0]['athleteId']

    print("\nAvailable Athletes:")
    # Show first 20 athletes to avoid flooding
    limit = 20
    for i, athlete in enumerate(athletes[:limit]):
        print(f"{i+1}. {athlete['firstName']} {athlete['lastName']}")
    
    if len(athletes) > limit:
        print(f"... and {len(athletes) - limit} more.")

    while True:
        try:
            selection = input(f"\nSelect athlete (1-{min(len(athletes), limit)}): ")
            index = int(selection)
            if 1 <= index <= len(athletes):
                return athletes[index-1]['athleteId']
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a number.")

def main():
    parser = argparse.ArgumentParser(description="Firstbeat Sports Cloud API example")
    parser.add_argument("--api", type=str, help="API url, default: https://api.firstbeat.com", default="https://api.firstbeat.com")
    parser.add_argument("--shared-secret", type=str, help="Shared secret from registration (or set FIRSTBEAT_SHARED_SECRET env var)")
    parser.add_argument("--consumer-id", type=str, help="Consumer ID from registration (or set FIRSTBEAT_CONSUMER_ID env var)")
    args = parser.parse_args()

    # Get credentials from args or environment variables
    shared_secret = args.shared_secret or os.getenv("FIRSTBEAT_SHARED_SECRET")
    consumer_id = args.consumer_id or os.getenv("FIRSTBEAT_CONSUMER_ID")

    # Validate credentials are provided
    if not shared_secret or not consumer_id:
        print("Error: Missing credentials!")
        print("\nProvide credentials either via:")
        print("  1. Command-line arguments:")
        print("     --shared-secret <secret> --consumer-id <id>")
        print("  2. Environment variables:")
        print("     export FIRSTBEAT_SHARED_SECRET='your-secret'")
        print("     export FIRSTBEAT_CONSUMER_ID='your-consumer-id'")
        return

    cloud_api = cloudapiclient.CloudAPI(args.api, shared_secret, consumer_id)

    # Fetch all the accounts and select which one to use
    print("Fetching accounts...")
    accounts = cloud_api.get_accounts()
    if accounts is None:
        return

    account_id = select_account(accounts)

    # Get the coaches
    print("\nFetching coaches...")
    account_coaches = cloud_api.get_account_coaches(account_id)
    if account_coaches is None:
        rich.print("No coaches found")
    else:
        rich.print(account_coaches)

    # Get the teams
    print("\nFetching teams...")
    account_teams = cloud_api.get_account_teams(account_id)
    if account_teams is None:
        rich.print("No teams found")
    else:
        rich.print(account_teams)

    # Get the athletes
    print("\nFetching athletes...")
    account_athletes = cloud_api.get_account_athletes(account_id)
    if account_athletes is None or len(account_athletes) == 0:
        rich.print("No athletes found")
        return
    # rich.print(account_athletes) # Can be too large

    # Select one athlete from the account_athletes response
    athlete_id = select_athlete(account_athletes)

    # Get the athlete measurements
    print(f"\nFetching measurements for athlete {athlete_id}...")
    athlete_measurements = cloud_api.get_athlete_measurements(account_id, athlete_id)

    if athlete_measurements is None or len(athlete_measurements) == 0:
        rich.print("No measurements found")
        return

    # print only the 3 latest measurements
    rich.print("Latest 3 measurements:")
    rich.print(athlete_measurements[-3:])

    # Select the latest measurement ID
    measurement_id = athlete_measurements[0]["measurementId"]

    # Define variables we want to fetch
    var = ['trimp', 'trimpPerMinute', 'heartRateAverage']

    # Get the athlete measurement results
    print(f"\nFetching results for measurement {measurement_id}...")
    athlete_measurement_results = cloud_api.get_athlete_measurement_results(account_id, athlete_id, measurement_id, var)
    rich.print(athlete_measurement_results)

    # This example doesn't include how to get teams sessions and their results, but they work similarly as the athlete measurements and results.

if __name__ == "__main__":
    main()
