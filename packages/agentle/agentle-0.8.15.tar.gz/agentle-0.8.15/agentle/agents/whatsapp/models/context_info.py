from typing import NotRequired, TypedDict

from agentle.agents.whatsapp.models.quoted_message import QuotedMessage


class ContextInfo(TypedDict):
    """Informações de contexto da mensagem WhatsApp.

    Attributes:
        stanzaId: ID da stanza da mensagem
        participant: Participante da conversa
        quotedMessage: Mensagem citada/respondida
    """

    stanzaId: NotRequired[str]
    participant: NotRequired[str]
    quotedMessage: NotRequired[QuotedMessage]