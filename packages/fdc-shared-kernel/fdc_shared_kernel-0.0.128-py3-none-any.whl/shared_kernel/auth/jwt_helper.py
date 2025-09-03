import jwt
from datetime import timedelta
from shared_kernel.exceptions import Unauthorized


class JWTTokenHandler:
    _instance = None

    def __new__(cls, secret_key: str = None):
        if cls._instance is None:
            if secret_key is None:
                raise ValueError("Secret key must be provided for the first initialization.")
            cls._instance = super(JWTTokenHandler, cls).__new__(cls)
            cls._instance._initialize(secret_key)
        return cls._instance

    def _initialize(self, secret_key: str):
        """
        Initialize the JWTTokenHandler with a secret key.

        Args:
            secret_key (str): The secret key used for encoding and decoding JWT tokens.
        """
        self.secret_key = secret_key

    def decode_token(self, token: str) -> dict:
        """
        Decode and verify a JWT token using the provided secret key.

        Args:
            token (str): The JWT token to be decoded.

        Returns:
            dict: The payload of the decoded token.

        Raises:
            Unauthorized: If the token is expired or invalid.
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise Unauthorized('Token expired')
        except jwt.InvalidTokenError:
            raise Unauthorized('Invalid token')

    def generate_token(self, payload: dict, expires_in: int = None) -> str:
        """
        Generate a JWT token from the given payload.

        Args:
            payload (dict): Data to encode into the token.
            expires_in (int, optional): Number of seconds until the token expires. Defaults to None, which means the token does not expire.

        Returns:
            str: The encoded JWT token.
        """
        # Set expiration time if provided
        if expires_in:
            exp = jwt.utils.utcnow() + timedelta(seconds=expires_in)
            payload['exp'] = exp

        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        return token.decode('utf-8')  # Decode bytes to string
