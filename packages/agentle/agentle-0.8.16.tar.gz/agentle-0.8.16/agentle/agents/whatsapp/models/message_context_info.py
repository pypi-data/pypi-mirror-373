from typing import NotRequired, TypedDict

from agentle.agents.whatsapp.models.device_list_metadata import DeviceListMetadata


class MessageContextInfo(TypedDict):
    """Informações de contexto da mensagem WhatsApp.

    Attributes:
        deviceListMetadata: Metadados da lista de dispositivos
        deviceListMetadataVersion: Versão dos metadados da lista de dispositivos
        messageSecret: Segredo da mensagem para criptografia
    """

    deviceListMetadata: NotRequired[DeviceListMetadata]
    deviceListMetadataVersion: NotRequired[int]
    messageSecret: NotRequired[str]