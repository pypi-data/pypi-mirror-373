import logging
import time
from datetime import timedelta

import jwt

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class JWTGenerator:
    def __init__(
        self,
        client_id,
        private_key,
        username,
        audience,
        session_duration_hours,
    ):
        self.client_id = client_id
        self.private_key = private_key
        self.username = username
        self.audience = audience
        self.session_duration_hours = session_duration_hours

    def generate_token(self) -> str:
        current_time = int(time.time())
        expiration_time = str(
            current_time
            + int(timedelta(hours=self.session_duration_hours).total_seconds())
        )

        payload = {
            "iss": self.client_id,
            "sub": self.username,
            "aud": self.audience,
            "exp": expiration_time,
        }

        try:
            token = jwt.encode(payload, self.private_key, algorithm="RS256")
        except ValueError:
            logging.error(
                "[ERROR: generate_token]: Cannot generate the JWT token for authentication."  # noqa: E501
            )
            token = ""

        return token
