import base64
import hashlib
from oauthlib.common import generate_token

def generate_code_pair():
    code_verifier = generate_token(43)  # Adequate randomness
    code_challenge = verifier_to_challenge(code_verifier)
    return code_verifier, code_challenge

def verifier_to_challenge(code_verifier):
    code_challenge_bytes = hashlib.sha256(code_verifier.encode('ascii')).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge_bytes).decode('ascii').rstrip('=')
    return code_challenge