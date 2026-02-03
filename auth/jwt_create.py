# /// script
# dependencies = [
#   "pyjwt",
# ]
# ///

import jwt
import time
import argparse
import sys

def create_jwt_token(consumer_id: str, shared_secret: str) -> str:
    """
    Generate a JWT token for Firstbeat Sports Cloud API.
    
    Args:
        consumer_id: The API Consumer ID (UUID)
        shared_secret: The API Shared Secret (UUID)
        
    Returns:
        Encoded JWT token string
    """
    now = int(time.time())
    expires = now + 300  # 5 minutes validity
    
    payload = {
        'iss': consumer_id,
        'iat': now,
        'exp': expires
    }
    
    # Explicitly specify the algorithm as HS256
    token = jwt.encode(payload, shared_secret, algorithm="HS256")
    return token

def main():
    parser = argparse.ArgumentParser(description="Generate a JWT for Firstbeat Sports Cloud API")
    parser.add_argument("--id", required=True, help="Consumer ID")
    parser.add_argument("--secret", required=True, help="Shared Secret")
    
    args = parser.parse_args()
    
    try:
        token = create_jwt_token(args.id, args.secret)
        print(f"Bearer {token}")
    except Exception as e:
        print(f"Error generating token: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
