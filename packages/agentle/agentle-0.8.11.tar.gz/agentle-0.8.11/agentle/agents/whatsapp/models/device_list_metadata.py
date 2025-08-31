from typing import TypedDict


class DeviceListMetadata(TypedDict):
    """Metadados da lista de dispositivos WhatsApp.

    Attributes:
        senderKeyHash: Hash da chave do remetente
        senderTimestamp: Timestamp do remetente
        recipientKeyHash: Hash da chave do destinatário
        recipientTimestamp: Timestamp do destinatário
    """

    senderKeyHash: str
    senderTimestamp: str
    recipientKeyHash: str
    recipientTimestamp: str