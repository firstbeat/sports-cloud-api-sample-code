# Authentication Scripts

This folder contains standalone scripts for generating JSON Web Tokens (JWT) required to authenticate with the Firstbeat Sports Cloud API.

Each script requires a specific library to handle JWT creation.

Examples for Javascript, Python, Java and R are provided. With help of these, you or any LLM-service should be able to create solution for other programming languages.

### Python
Requires `pyjwt`:
```bash
pip install pyjwt
```

### JavaScript (Node.js)
Requires `jsonwebtoken`:
```bash
npm install jsonwebtoken
```

### R
Requires `openssl` and `jose`:
```bash
Rscript -e 'install.packages(c("openssl", "jose"))'
```

### Java
Requires the `java-jwt` library (e.g., from Auth0).

## Usage

All scripts take your **Consumer ID** and **Shared Secret** as arguments and output the full `Authorization` header value.

### Python
```bash
python jwt_create.py --id <consumer_id> --secret <shared_secret>
```

### JavaScript (Node.js)
```bash
node jwt_create.js <consumer_id> <shared_secret>
```

### R
```bash
Rscript jwt_create.R <consumer_id> <shared_secret>
```

### Java
```bash
javac -cp "java-jwt.jar" JwtCreate.java
java -cp ".:java-jwt.jar" JwtCreate <consumer_id> <shared_secret>
```

## Security Note
Never commit your `Shared Secret` to version control or send it to Firstbeat Sports support. These scripts are intended for local development and testing purposes.
