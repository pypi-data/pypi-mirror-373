import hashlib
from ..exception import *
from .verbbuilder import FromVerbBuilder, PKAMVerbBuilder, CRAMVerbBuilder
from .encryptionutil import EncryptionUtil
from .keysutil import KeysUtil

class AuthUtil:
    HEX_ARRAY = "0123456789abcdef"

    def __init__(self) -> None:
        pass

    @staticmethod
    def authenticate_with_cram(connection, atsign, cram_secret):
        command = FromVerbBuilder().set_shared_by(atsign).build()
        from_response = str(connection.execute_command(command))
        if not from_response.startswith("data:"):
            raise AtUnauthenticatedException("Invalid response to 'from': " + from_response)

        challenge = from_response.replace("data:", "")
        try:
            cram_digest = AuthUtil._get_cram_digest(cram_secret, challenge)
        except Exception as e:
            raise AtEncryptionException(f"Failed to generate cramDigest - {e}")

        command = CRAMVerbBuilder().set_digest(cram_digest).build()
        cram_response = str(connection.execute_command(command))
        if not str(cram_response).startswith("data:success"):
            raise AtUnauthenticatedException(f"CRAM command failed: {cram_response}")
    
    @staticmethod
    def authenticate_with_pkam(connection, atsign, keys):
        command = FromVerbBuilder().set_shared_by(atsign).build()
        from_response = connection.execute_command(command).get_raw_data_response()

        try:
            signature = EncryptionUtil.sign_sha256_rsa(from_response, keys[KeysUtil.pkam_private_key_name])
        except:
            raise Exception("Failed to create SHA256 signature")

        command = PKAMVerbBuilder().set_digest(signature).build()
        pkam_response = connection.execute_command(command)

        if not str(pkam_response).startswith("data:success"):
            raise AtUnauthenticatedException(f"PKAM command failed: {pkam_response}")

    @staticmethod
    def _get_cram_digest(cram_secret, challenge):
        digest_input = cram_secret + challenge
        digest_input_bytes = digest_input.encode("utf-8")
        digest = hashlib.sha512(digest_input_bytes).digest()
        return AuthUtil.bytes_to_hex(digest)

    @staticmethod
    def bytes_to_hex(bytes):
        hex_chars = []
        for byte in bytes:
            v = byte & 0xFF
            hex_chars.append(AuthUtil.HEX_ARRAY[v >> 4])
            hex_chars.append(AuthUtil.HEX_ARRAY[v & 0x0F])
        return "".join(hex_chars)
