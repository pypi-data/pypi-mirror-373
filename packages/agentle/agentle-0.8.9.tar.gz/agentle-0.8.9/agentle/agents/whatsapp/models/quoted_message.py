from typing import NotRequired, TypedDict


class QuotedMessage(TypedDict):
    """Mensagem citada/respondida no WhatsApp.

    Attributes:
        conversation: Texto da mensagem citada (para mensagens de texto)
        imageMessage: Dados da imagem citada (opcional)
        documentMessage: Dados do documento citado (opcional)
        audioMessage: Dados do áudio citado (opcional)
        videoMessage: Dados do vídeo citado (opcional)
    """

    conversation: NotRequired[str]
    imageMessage: NotRequired[dict[str, str]]  # Estrutura simplificada para imagem
    documentMessage: NotRequired[dict[str, str]]  # Estrutura simplificada para documento
    audioMessage: NotRequired[dict[str, str]]  # Estrutura simplificada para áudio
    videoMessage: NotRequired[dict[str, str]]  # Estrutura simplificada para vídeo