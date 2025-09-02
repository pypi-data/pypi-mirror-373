# JSON Web Token Implementation (Python)

The `pyjwt-tspspi` project is a simple JWT implementation that builds upon the [pycryptodomex](https://pypi.org/project/pycryptodomex/) cryptography library. It performs JSON serialization of encrypted (JWE) and signed (JWS) objects as well as accompanying keys (JWK). The library supports both compact and non-compact JWTs.

## Installation

To install the package, use the following command:

```bash
pip install pyjwt-tspspi
```

## Supported Mechanisms

- **Signature Algorithms**: RS256, HS256, etc.
- **Encryption Algorithms**: RSA-OAEP, A128GCM, etc.

## Documentation

For more detailed information, please refer to the [documentation](./doc/).

## Usage

### JSON Web Encryption (JWE)

This example demonstrates how to create and parse a JSON Web Encryption (JWE).

```python
from jwe import JWE
from keystore import Keystore
from jwk import JWK_RSA

# Sample payload
payload = {"sub": "1234567890", "name": "John Doe", "admin": True}

# Create a keystore and add an RSA JWK
keystore = Keystore()
jwk_rsa = JWK_RSA.create(bits=2048, key_ops=["encrypt", "decrypt"], key_id="RSA test key")
keystore.add(jwk_rsa)

# Create a JWE
jwe = JWE.create(payload, [jwk_rsa], compact=False)
print("Created JWE:", jwe.to_json(indent=4))

# Parse the JWE
parsed_jwe = JWE.parse(jwe.to_json(), keystore=keystore)
print("Parsed Payload:", json.dumps(parsed_jwe.get_payload(), indent=2))
```

### JSON Web Key (JWK) Encryption/Decryption

This example demonstrates how to encrypt and decrypt data using JSON Web Key (JWK).

```python
from jwk import JWK_RSA

# Sample payload
payload = b"This is a secret message."

# Create an RSA JWK for encryption and decryption
jwk = JWK_RSA.create(bits=2048, use="enc")

# Encrypt the payload
encrypted_payload = jwk.encrypt(payload)
print("Encrypted Payload:", encrypted_payload)

# Decrypt the payload
decrypted_payload = jwk.decrypt(encrypted_payload)
print("Decrypted Payload:", decrypted_payload.decode('utf-8'))
```

### JSON Web Signature (JWS)

This example demonstrates how to create and parse a JSON Web Signature (JWS).

```python
from jws import JWS
from keystore import Keystore
from jwk import JWK_Shared

# Sample payload
payload = {"sub": "1234567890", "name": "John Doe", "admin": True}

# Create a JWK for signing
jwk = JWK_Shared.create(secret=b"secret", use="sig", key_id="test-key")

# Create a keystore and add the key
keystore = Keystore()
keystore.add(jwk)

# Create a JWS
jws = JWS.create(payload, signaturekeys=jwk, compact=True)
print("Created JWS:", jws.to_json())

# Parse the JWS
parsed_jws = JWS.parse(jws.to_json(), keystore=keystore)
print("Parsed Payload:", parsed_jws.get_payload())
```

### JSON Web Token (JWT)

This example demonstrates how to create and parse a JSON Web Token (JWT).

```python
from jwt import parse_jwt
from keystore import Keystore
from jwk import JWK_Shared
from jws import JWS

# Create a JWK for signing
jwk = JWK_Shared.create(secret=b"my-secret-key", use="sig", key_id="test-key")

# Create a keystore and add the key
keystore = Keystore()
keystore.add(jwk)

# Create sample JWT payload (claims)
payload = {
    "sub": "1234567890",
    "name": "John Doe", 
    "admin": True,
    "iat": 1516239022
}

# Create a JWT
jwt = JWS.create(payload, signaturekeys=jwk, compact=True)
jwt_token = jwt.to_json()

print("Created JWT:", jwt_token)

# Parse the JWT token
parsed_jwt = parse_jwt(jwt_token, keystore=keystore)
print("Parsed JWT payload:", parsed_jwt.get_payload())
```

