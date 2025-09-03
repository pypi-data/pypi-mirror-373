from dataclasses import dataclass

from ...common.metadata import Metadata
from ...util.atconstants import *

@dataclass
class AtNotification:
    uuid: str = None
    key: str = ''
    from_atsign: str = ''
    to_atsign: str = ''
    epoch_millis: int = 0
    status: str = ''
    value: str = None
    operation: str = None
    message_type: str = None
    is_encrypted: str = None
    expires_at_in_epoch_millis: int = None
    metadata: Metadata = None

    def from_json(cls, json):
        metadata = None
        if json['metadata'] is not None:
            metadata = Metadata()
            metadata.enc_key_name = json['metadata'][ENCRYPTING_KEY_NAME]
            metadata.enc_algo = json['metadata'][ENCRYPTING_ALGO]
            metadata.iv_nonce = json['metadata'][IV_OR_NONCE]
            metadata.ske_enc_key_name = json['metadata'][SHARED_KEY_ENCRYPTED_ENCRYPTING_KEY_NAME]
            metadata.ske_enc_algo = json['metadata'][SHARED_KEY_ENCRYPTED_ENCRYPTING_ALGO]
        
        return cls(json['id'], json['key'], json['from'], json['to'], json['epochMillis'],
               json['messageType'], json[IS_ENCRYPTED],
               value=json['value'], operation=json['operation'],
               expiresAtInEpochMillis=json['expiresAt'], metadata=metadata)
    
    def to_json(self):
        return {
            'id': self.uuid,
            'key': self.key,
            'from': self.from_atsign,
            'to': self.to_atsign,
            'epochMillis': self.epoch_millis,
            'value': self.value,
            'operation': self.operation,
            'messageType': self.message_type,
            IS_ENCRYPTED: self.is_encrypted,
            'notificationStatus': self.status,
            'expiresAt': self.expires_at_in_epoch_millis,
            'metadata': self.metadata # to json?
        }
    
    # TO?DO: from_json_list, __str__(self)