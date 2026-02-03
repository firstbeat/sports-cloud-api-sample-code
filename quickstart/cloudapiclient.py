"""
Sports Cloud API code sample

Purpose of this file is to provide examples and explain how the API works.

* This code sample is *not* intended to be an example implementation of an API client for Firstbeat Sports Cloud API.
* Examples in this file don't cover all the possible use cases.
* Basic things like rate limiting, proper retry logic, logging etc. are missing and out of scope for this example.

There are comments in the file but studying the official documentation is a mandatory prerequisite to understand the API.
"""

import time

import jwt  # pyjwt
import requests


class CloudAPI:
    def __init__(self, api: str, shared_secret: str, consumer_id: str):
        self.api = api
        self.shared_secret = shared_secret
        self.consumer_id = consumer_id
        self.api_key: str | None = None

    def generate_jwt_token(self) -> str:
        """
        Generates a JWT token that is needed for each query except for registration.

        Since the token is valid for 5 minutes only, in this example we generate a new token for each query. 
        If lots of API calls are made, using some kind of token manager might make sense.

        Args:
            shared_secret (str): Shared secret
            consumer_id (str): Consumer ID

        Returns:
            str: JWT token
        """
        now = int(time.time())
        expires = now + 300
        payload = {"iss": self.consumer_id, "iat": now, "exp": expires}
        
        return jwt.encode(payload, self.shared_secret, algorithm="HS256")

    def generate_query_headers(self) -> dict:
        """
        Generate the API query headers.
        JWT token and API key must be included in all queries excluding the API registration and API key creation queries.

        Args:
            None

        Returns:
            dict: Headers
        """
        # Create the API key if it's not set
        if self.api_key is None:
            self.api_key = self.retrieve_api_key()

        headers = {
            "Authorization": f"Bearer {self.generate_jwt_token()}",
            "x-api-key": self.api_key,
        }

        return headers

    def retrieve_api_key(self) -> str | None:
        """
        Return the API key for the API consumer

        You need to include a JWT token in the query to retrieve an API key.

        An API key is created only once for each API consumer.
        If you call this endpoint again, the same API key is returned each time.

        Once the API key is created, store it securely and use in all subsequent queries.

        As a response you get:

        {"apikey":"cXvpCBUzE64odvHXA5tcDREMOVEDREMOVED"}

        Returns:
            str: API key or None if creation fails
        """

        url = f"{self.api}/v1/account/api-key"

        response = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {self.generate_jwt_token()}",
            },
        )
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.json())
            return None

        return response.json()["apikey"]

    def get_accounts(self) -> dict | None:
        """
        Get accounts assigned to the API consumer.
        One or more accounts can be assigned to one API consumer ("registration").

        Account can be accessed via Sports Cloud API if:

            1) Firstbeat support has granted access for your API consumer for the specific account(s)
            2) Account owner (for example team coach) has granted access to their account data

        Get the account ID of the account and use the ID in the subsequent queries to work with the selected account.

        If an empty list is returned, you don't have any access to any accounts.

        Example response:

        {
            "accounts": [
                {
                    "accountId": "3-99999",
                    "name": "FC Firstbeat",
                    "authorizedBy": {
                        "coachId": 0
                    }
                },
                {
                    "accountId": "3-99998",
                    "name": "Firstbeat Ice Hockey Team",
                    "authorizedBy": {
                        "coachId": 0
                    }
                },
                {
                    "accountId": "3-99997",
                    "name": "FC Firstbeat Juniors",
                    "authorizedBy": {
                        "coachId": 0
                    }
                }
            ]
        }

        Args:
            None

        Returns:
            list[dict]: Accounts or None if query fails

        """

        url = f"{self.api}/v1/sports/accounts/"
        response = requests.get(url, headers=self.generate_query_headers())
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.json())
            return None

        return response.json()["accounts"]

    def get_account_athletes(self, account_id: str) -> list | None:
        """Get all athletes on the account

        Note: There can be athletes on account that are not assigned to any team(s).

        Use the teams endpoint to get athletes belonging to a team:
        /sports/accounts/{{accountId}}/teams/{{teamId}}/athletes

        Example:

        {
            "more": false,
            "athletes": [
                {
                    "firstName": "John",
                    "lastName": "Doe",
                    "email": "john.doe1@firstbeat.com",
                    "athleteId": 381678
                },
                {
                    "firstName": "Joe",
                    "lastName": "Doe",
                    "athleteId": 381679
                },

        Args:
            account_id (str): Account ID

        Returns:
            dict: List of Athletes or None if query fails
        """

        url = f"{self.api}/v1/sports/accounts/{account_id}/athletes"
        params: dict[str, str | int] = {}
        athletes = []
        more = True

        while more:
            response = requests.get(
                url, params=params, headers=self.generate_query_headers()
            )
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                print(response.json())
                return None

            athletes.extend(response.json()["athletes"])
            more = response.json()["more"]
            params = {"offset": len(athletes)}

        return athletes

    def get_account_coaches(self, account_id: str) -> dict | None:
        """Get all coaches on the account

        Coach information can be e.g. used for showing which coach created a training session.

        Example:

        {
            "firstName": "test",
            "lastName": "coach1",
            "email": "noreply@firstbeat.com",
            "coachId": 381677
        }

        Args:
            account_id (str): Account ID

        Returns:
            dict: Coaches or None if query fails
        """

        url = f"{self.api}/v1/sports/accounts/{account_id}/coaches"
        response = requests.get(url, headers=self.generate_query_headers())
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.json())
            return None

        return response.json()

    def get_account_teams(self, account_id: str) -> list | None:
        """Get all teams and their groups (sub-groups) on the account

        Example:

        {
            "more": false,
            "teams": [
                {
                    "name": "team3",
                    "teamId": 10328,
                    "athleteIds": [],
                    "groups": [
                        {
                            "groupId": 10335,
                            "name": "Strikers",
                            "athleteIds": [
                                381678,
                                381687,
                                381688,
                                381689
                            ]
                        }
                    ]
                },
                {
                    "name": "team4",
                    "teamId": 10334,
                    "athleteIds": [],
                    "groups": []
                }
            ]
        }

        Args:
            account_id (str): Account ID

        Returns:
            dict: Teams or None if query fails
        """

        url = f"{self.api}/v1/sports/accounts/{account_id}/teams"
        params: dict[str, str | int] = {}
        teams = []
        more = True

        while more:
            response = requests.get(
                url, params=params, headers=self.generate_query_headers()
            )
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                print(response.json())
                return None

            teams.extend(response.json()["teams"])
            more = response.json()["more"]
            params = {"offset": len(teams)}

        return teams

    def get_athlete_measurements(self, account_id: str, athlete_id: str) -> list | None:
        """
        Returns all measurements for one athlete.

        !!! Important !!! Please read the documentation on differences between measurements and sessions.

        Lists only measurements, not the measurements analysis results (HR, TRIMP, EPOC...).

        All times are UTC
        Field "exerciseType" is available if value is set for the measurements. If it's not set, field is not included.

        Args:
            account_id (str): Account ID
            athlete_id (str): Athlete ID

        Returns:
            dict: Measurements or None if query fails
        """

        url = f"{self.api}/v1/sports/accounts/{account_id}/athletes/{athlete_id}/measurements"
        params: dict[str, str | int] = {}
        measurements = []
        more = True

        while more:
            response = requests.get(
                url, params=params, headers=self.generate_query_headers()
            )
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                print(response.json())
                return None

            measurements.extend(response.json()["measurements"])
            more = response.json()["more"]
            params = {"offset": len(measurements)}

        return measurements

    def get_athlete_measurement_results(
        self,
        account_id: str,
        athlete_id: str,
        measurement_id: str,
        variables: list[str] | None = None,
    ) -> dict | None:
        """
        Get athlete measurement results (analysis results) like HR, TRIMP ...
        
        The returned variables can be scalar values or time series data. By default, time series data is returned in decoded and compressed format. 
        See the API documentation for more information on how to decode the time series data or how to return the time series data in decompressed format.

        All data is not pre-analysed on the Server. Sometimes for old data, the first query can trigger analysis
        process to start and "202 Accepted" is returned. Wait for 5 seconds and invoke the same query again to get the results.
        202 Accepted can be returned for measurement, session and lap analysis results.

        Set the variables using the "var" parameter. If the "var" parameter is not set, all default values are returned.
        Get only the variables you need to save bandwidth and processing time.
        
        Note: Some time series variables need to be specifically requested and are not included in the default set because of they are computationally heavy.
        Note: Maximum payload size of the returned data is 6MB.

        Example Response:

        {
            "measurementId": 4535109,
            "sessionId": 74180,
            "startTime": "2018-03-01T08:20:51Z",
            "endTime": "2018-03-01T08:23:50Z",
            "variables": [
                {
                    "name": "trimp",
                    "value": 5.4673919677734375
                },
                {
                    "name": "trimpPerMinute",
                    "unit": "min⁻¹",
                    "value": 1.773193359375
                },
                {
                    "name": "heartRateAverage",
                    "unit": "min⁻¹",
                    "value": 149.56558227539062
                }
            ],
            "exerciseType": "Evening Practice",
            "athleteId": 381678
        }
        
        Args:
            account_id (str): Account ID
            athlete_id (str): Athlete ID
            measurement_id (str): Measurement ID
            variables (list): List of variables to fetch
        
        Returns:
            dict: Measurement results or None if query fails
        """
        if variables is None:
            variables = ["trimp", "trimpPerMinute", "heartRateAverage"]

        url = f"{self.api}/v1/sports/accounts/{account_id}/athletes/{athlete_id}/measurements/{measurement_id}/results"
        params = {"var": ",".join(variables)}

        max_retries = 5
        retry_count = 0

        while retry_count < max_retries:
            response = requests.get(
                url, headers=self.generate_query_headers(), params=params
            )

            # If we get a 200 OK response, return the results immediately
            if response.status_code == 200:
                return response.json()

            # If we get a 202 Accepted, wait and retry
            # This means that Server has started to process data and we need to wait for the results
            elif response.status_code == 202:
                retry_count += 1

                # If we've tried 5 times and still getting 202, return an error
                if retry_count >= max_retries:
                    error_message = f"Error: Maximum retries reached. API still returning 202 Accepted after {max_retries} attempts."
                    print(error_message)
                    return {"error": error_message, "status_code": 202}

                # Wait 5 seconds before retrying
                time.sleep(5)
                continue

            # For any other error status code
            else:
                print(f"Error: {response.status_code}")
                print(response.json())
                return None

        # This line should never be reached due to the conditions above
        return None
