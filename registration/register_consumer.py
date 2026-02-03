#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "requests",
# ]
# ///
"""
Interactive helper for registering a Firstbeat Sports Cloud API consumer.

Run directly with uv (no virtual environment needed):
    uv run registration/register_consumer.py
"""

from __future__ import annotations

import argparse
from typing import Optional, Sequence, Tuple

import requests


API_URL = "https://api.firstbeat.com/v1/account/register"
DEFAULT_TIMEOUT: Tuple[float, float] = (5.0, 20.0)  # (connect, read)


class RegistrationError(Exception):
    """Raised when the API registration flow fails."""


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Register a Firstbeat Sports Cloud API consumer interactively or via"
            " command-line flags."
        ),
        epilog="""
examples:
  Interactive mode:
    uv run registration/register_consumer.py

  Automated mode:
    uv run registration/register_consumer.py --consumer-name "My Team Analytics" --yes
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--consumer-name",
        help="Provide the desired consumer name non-interactively.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip interactive confirmation prompts.",
    )
    parser.add_argument(
        "--api-url",
        default=API_URL,
        help="Override the registration endpoint (mostly for testing).",
    )
    return parser.parse_args(argv)


def prompt_consumer_name(input_fn=input) -> str:
    print("--- Firstbeat Sports Cloud API Consumer Registration ---")
    print("This script will help you create a new API consumer.")
    print("An API consumer is your application's identity for accessing the API.\n")

    print("!!! Choosing a Consumer Name !!!")
    print("Your 'consumerName' helps Firstbeat support identify your integration.")
    print("It cannot be changed later.")
    print("\nGOOD Examples:")
    print("  * 'FC Firstbeat Data Hub'")
    print("  * 'Jyväskylä Bears Analytics'")
    print("\nBAD Examples:")
    print("  * 'api_test'")
    print("  * 'script_1'\n")

    while True:
        consumer_name = input_fn("Enter your desired Consumer Name: ").strip()
        if not consumer_name:
            print("Consumer name cannot be empty. Please try again.")
            continue
        if len(consumer_name) < 5:
            print("Consumer name is too short. Please use a descriptive name.")
            continue
        return consumer_name


def confirm_action(consumer_name: str, auto_confirm: bool, input_fn=input) -> bool:
    print(f"\nYou are about to register a new API consumer: '{consumer_name}'")
    if auto_confirm:
        return True
    confirm = input_fn("Do you want to proceed? (yes/no): ").strip().lower()
    return confirm in {"y", "yes"}


def register_consumer(
    consumer_name: str,
    api_url: str,
    session: Optional[requests.Session] = None,
) -> dict:
    session_obj = session or requests.Session()
    try:
        response = session_obj.post(
            api_url,
            json={"consumerName": consumer_name},
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise RegistrationError(f"HTTP request failed: {exc}") from exc

    try:
        return response.json()
    except ValueError as exc:
        raise RegistrationError("Server returned an invalid JSON payload.") from exc


def announce_success(credentials: dict) -> None:
    print("\n" + "=" * 50)
    print("REGISTRATION SUCCESSFUL!")
    print("=" * 50)
    print(f"Consumer Name : {credentials.get('consumerName')}")
    print(f"Consumer ID   : {credentials.get('id')}")
    print(f"Shared Secret : {credentials.get('sharedSecret')}")
    print("=" * 50)
    print("IMPORTANT: Save the 'Consumer ID' and 'Shared Secret' securely now.")
    print("The Shared Secret will NOT be shown again.")
    print("=" * 50)


def print_next_steps(consumer_name: str, credentials: dict) -> None:
    consumer_id = credentials.get("id", "<unknown>")
    print("\n--- NEXT STEPS ---")
    print("1. EMAIL APPROVAL:")
    print("   Send an email to sports-cloud-api@firstbeat.com with:")
    print(f"     - Your Consumer Name: {consumer_name}")
    print(f"     - Your Consumer ID: {consumer_id}")
    print("     - The customer account names you need access to (e.g. 'FC Firstbeat')")
    print("     - Contact details for API notifications.")

    print("\n2. COACH AUTHORIZATION:")
    print("   Once Firstbeat approves the consumer, a Coach must log in to")
    print("   Sports Cloud (https://sports.firstbeat.com), go to Settings -> Cloud API,")
    print("   and grant access to your new consumer.")

    print("\n3. AUTHENTICATION:")
    print("   Use the ID and Shared Secret to generate JWT tokens for API access.")


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    consumer_name = args.consumer_name or prompt_consumer_name()

    if not confirm_action(consumer_name, args.yes):
        print("Registration cancelled.")
        return 0

    print(f"\nRegistering '{consumer_name}'...")
    try:
        credentials = register_consumer(
            consumer_name=consumer_name,
            api_url=args.api_url,
        )
    except RegistrationError as exc:
        print(f"\nError during registration: {exc}")
        return 1

    announce_success(credentials)
    print_next_steps(consumer_name, credentials)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
