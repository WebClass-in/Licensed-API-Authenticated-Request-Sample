import hashlib
import hmac
import base64


class HMACAuthenticator:

    @staticmethod
    def generate_signature(api_secret, method, path, query_string, body):

        body_hash = hashlib.sha256(body).hexdigest()

        canonical_message = (
            f"{method}\n"
            f"{path}\n"
            f"{query_string}\n"
            f"{body_hash}"
        )

        signature = hmac.new(
            api_secret.encode("utf-8"),
            canonical_message.encode("utf-8"),
            hashlib.sha256
        ).digest()

        encoded_signature = base64.b64encode(signature).decode("utf-8")

        return encoded_signature