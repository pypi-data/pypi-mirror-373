import base64
from .keysutil import KeysUtil
from .encryptionutil import EncryptionUtil


class OnboardingUtil:
    @staticmethod
    def generate_pkam_keypair(keys):
        private_key_bytes, public_key_bytes = EncryptionUtil.generate_rsa_key_pair()

        public_key_string = base64.b64encode(public_key_bytes).decode()
        private_key_string = base64.b64encode(private_key_bytes).decode()

        keys[KeysUtil.pkam_public_key_name] = public_key_string
        keys[KeysUtil.pkam_private_key_name] = private_key_string

    @staticmethod
    def generate_encryption_keypair(keys):
        private_key_bytes, public_key_bytes = EncryptionUtil.generate_rsa_key_pair()

        public_key_string = base64.b64encode(public_key_bytes).decode()
        private_key_string = base64.b64encode(private_key_bytes).decode()

        keys[KeysUtil.encryption_public_key_name] = public_key_string
        keys[KeysUtil.encryption_private_key_name] = private_key_string

    @staticmethod
    def generate_self_encryption_key(keys):
        self_encryption_key = EncryptionUtil.generate_aes_key_base64()
        keys[KeysUtil.self_encryption_key_name] = self_encryption_key

    @staticmethod
    def store_pkam_public_key(connection, keys):
        connection.execute_command("update:privatekey:at_pkam_publickey " + keys[KeysUtil.pkam_public_key_name])

    @staticmethod
    def store_public_encryption_key(connection, atsign, keys):
        connection.execute_command("update:public:publickey@" + atsign + " " + keys[KeysUtil.encryption_public_key_name])

    @staticmethod
    def delete_cram_key(connection):
        connection.execute_command("delete:privatekey:at_secret")