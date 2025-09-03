import threading


should_be_running_lock = threading.Lock()
running_lock = threading.Lock()

ENCRYPTING_KEY_NAME = 'encKeyName'
ENCRYPTING_ALGO = 'encAlgo'
IV_OR_NONCE = 'ivNonce'
SHARED_KEY_ENCRYPTED_ENCRYPTING_KEY_NAME = 'skeEncKeyName'
SHARED_KEY_ENCRYPTED_ENCRYPTING_ALGO = 'skeEncAlgo'
IS_ENCRYPTED = 'isEncrypted'