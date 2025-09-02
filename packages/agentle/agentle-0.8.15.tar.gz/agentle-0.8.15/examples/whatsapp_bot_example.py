# examples/whatsapp_bot_example.py
"""
Example of using Agentle agents as WhatsApp bots with simplified configuration.
"""

import logging
import os

import uvicorn
from blacksheep import Application
from dotenv import load_dotenv

from agentle.agents.agent import Agent
from agentle.agents.conversations.json_file_conversation_store import (
    JSONFileConversationStore,
)
from agentle.agents.whatsapp.models.whatsapp_bot_config import WhatsAppBotConfig
from agentle.agents.whatsapp.models.whatsapp_session import WhatsAppSession
from agentle.agents.whatsapp.providers.evolution.evolution_api_config import (
    EvolutionAPIConfig,
)
from agentle.agents.whatsapp.providers.evolution.evolution_api_provider import (
    EvolutionAPIProvider,
)
from agentle.agents.whatsapp.whatsapp_bot import WhatsAppBot
from agentle.sessions.in_memory_session_store import InMemorySessionStore
from agentle.sessions.session_manager import SessionManager

load_dotenv()

logging.basicConfig(level=logging.INFO)


def create_development_bot() -> Application:
    """Example 1: Development bot with simplified configuration."""

    agent = Agent(
        instructions="Você é um assistente útil para desenvolvimento. Responda de forma clara e concisa.",
    )

    # Create provider
    provider = EvolutionAPIProvider(
        config=EvolutionAPIConfig(
            base_url=os.getenv("EVOLUTION_API_URL", "http://localhost:8080"),
            instance_name=os.getenv("EVOLUTION_INSTANCE_NAME", "dev-bot"),
            api_key=os.getenv("EVOLUTION_API_KEY", "your-api-key"),
        ),
    )

    # Use development configuration preset
    bot_config = WhatsAppBotConfig.development(
        welcome_message="🚀 Olá! Sou seu assistente de desenvolvimento. Como posso ajudar?",
        quote_messages=False,  # Don't quote messages in development
        debug_mode=True,
    )

    # Validate configuration
    issues = bot_config.validate_config()
    if issues:
        logging.warning(f"Configuration issues: {issues}")

    # Create WhatsApp bot
    whatsapp_bot = WhatsAppBot(agent=agent, provider=provider, config=bot_config)

    return whatsapp_bot.to_blacksheep_app(
        webhook_path="/webhook/whatsapp",
        show_error_details=True,
    )


def create_production_bot() -> Application:
    """Example 2: Production bot with optimized configuration."""

    agent = Agent(
        instructions="Você é um assistente profissional. Seja útil, cortês e eficiente.",
        conversation_store=JSONFileConversationStore(),
    )

    session_manager = SessionManager[WhatsAppSession](
        session_store=InMemorySessionStore[WhatsAppSession](),
        default_ttl_seconds=3600,
        enable_events=True,
    )

    # Create provider with session management
    provider = EvolutionAPIProvider(
        config=EvolutionAPIConfig(
            base_url=os.getenv("EVOLUTION_API_URL", "http://localhost:8080"),
            instance_name=os.getenv("EVOLUTION_INSTANCE_NAME", "production-bot"),
            api_key=os.getenv("EVOLUTION_API_KEY", "your-api-key"),
        ),
        session_manager=session_manager,
        session_ttl_seconds=3600,
    )

    # Use production configuration preset
    bot_config = WhatsAppBotConfig.production(
        welcome_message="Teste",
        quote_messages=False,  # Don't quote by default
        enable_spam_protection=True,
    )

    # Validate configuration
    issues = bot_config.validate_config()
    if issues:
        logging.warning(f"Production configuration issues: {issues}")

    whatsapp_bot = WhatsAppBot(agent=agent, provider=provider, config=bot_config)

    return whatsapp_bot.to_blacksheep_app(
        webhook_path="/webhook/whatsapp",
        show_error_details=False,
    )


def create_customer_service_bot() -> Application:
    """Example 3: Customer service bot with message quoting."""

    agent = Agent(
        instructions="""Você é um assistente de atendimento ao cliente profissional. 
        Seja sempre cortês, empático e eficiente. Mantenha um tom profissional mas amigável.""",
    )

    provider = EvolutionAPIProvider(
        config=EvolutionAPIConfig(
            base_url=os.getenv("EVOLUTION_API_URL", "http://localhost:8080"),
            instance_name=os.getenv("EVOLUTION_INSTANCE_NAME", "customer-service"),
            api_key=os.getenv("EVOLUTION_API_KEY", "your-api-key"),
        ),
    )

    # Use customer service configuration with message quoting
    bot_config = WhatsAppBotConfig.customer_service(
        welcome_message="👋 Olá! Bem-vindo ao nosso atendimento. Como posso ajudá-lo?",
        quote_messages=True,  # Enable quoting for context
        support_hours_message="Peço desculpas pelo inconveniente. Nossa equipe de suporte está disponível das 9h às 18h. Tente novamente durante nosso horário de funcionamento ou nos envie um email para suporte@empresa.com",
    )

    # Validate configuration
    issues = bot_config.validate_config()
    if issues:
        logging.warning(f"Customer service configuration issues: {issues}")

    whatsapp_bot = WhatsAppBot(agent=agent, provider=provider, config=bot_config)

    return whatsapp_bot.to_blacksheep_app(
        webhook_path="/webhook/whatsapp",
        show_error_details=False,
    )


def create_high_volume_bot() -> Application:
    """Example 4: High-volume bot optimized for performance."""

    agent = Agent(
        instructions="Você é um assistente otimizado para alto volume. Seja direto e eficiente.",
    )

    provider = EvolutionAPIProvider(
        config=EvolutionAPIConfig(
            base_url=os.getenv("EVOLUTION_API_URL", "http://localhost:8080"),
            instance_name=os.getenv("EVOLUTION_INSTANCE_NAME", "high-volume"),
            api_key=os.getenv("EVOLUTION_API_KEY", "your-api-key"),
        ),
    )

    # Use high-volume configuration for performance
    bot_config = WhatsAppBotConfig.high_volume(
        welcome_message="Olá! Processando sua mensagem...",
        quote_messages=False,  # Disabled for performance
    )

    # Validate configuration
    issues = bot_config.validate_config()
    if issues:
        logging.warning(f"High-volume configuration issues: {issues}")

    whatsapp_bot = WhatsAppBot(agent=agent, provider=provider, config=bot_config)

    return whatsapp_bot.to_blacksheep_app(
        webhook_path="/webhook/whatsapp",
        show_error_details=False,
    )


def create_custom_bot() -> Application:
    """Example 5: Custom configuration with specific needs."""

    agent = Agent(
        instructions="Você é um assistente personalizado com configurações específicas.",
    )

    provider = EvolutionAPIProvider(
        config=EvolutionAPIConfig(
            base_url=os.getenv("EVOLUTION_API_URL", "http://localhost:8080"),
            instance_name=os.getenv("EVOLUTION_INSTANCE_NAME", "custom-bot"),
            api_key=os.getenv("EVOLUTION_API_KEY", "your-api-key"),
        ),
    )

    # Start with a base configuration and customize
    bot_config = WhatsAppBotConfig.production(
        welcome_message="Teste",
        quote_messages=False,
    )

    # Customize specific parameters
    bot_config.batch_delay_seconds = 2.0  # Faster batching
    bot_config.max_batch_size = 15  # Larger batches
    bot_config.typing_duration = 1  # Shorter typing indicator
    bot_config.max_messages_per_minute = 30  # More lenient rate limiting

    # Validate the custom configuration
    issues = bot_config.validate_config()
    if issues:
        logging.warning(f"Custom configuration issues: {issues}")
        for issue in issues:
            logging.warning(f"  - {issue}")

    # Log configuration summary
    logging.info(f"Using configuration: {bot_config}")

    whatsapp_bot = WhatsAppBot(agent=agent, provider=provider, config=bot_config)

    return whatsapp_bot.to_blacksheep_app(
        webhook_path="/webhook/whatsapp",
        show_error_details=False,
    )


# Choose which bot to run based on environment variable
def create_server() -> Application:
    """Create the appropriate bot based on environment configuration."""

    bot_type = os.getenv("BOT_TYPE", "production").lower()

    if bot_type == "development":
        return create_development_bot()
    elif bot_type == "production":
        return create_production_bot()
    elif bot_type == "customer_service":
        return create_customer_service_bot()
    elif bot_type == "high_volume":
        return create_high_volume_bot()
    elif bot_type == "custom":
        return create_custom_bot()
    else:
        logging.warning(f"Unknown bot type '{bot_type}', using development")
        return create_development_bot()


app = create_server()
port = int(os.getenv("PORT", "8000"))

if __name__ == "__main__":
    # Log which bot type is being used
    bot_type = os.getenv("BOT_TYPE", "development")
    logging.info(
        f"Starting WhatsApp bot server with '{bot_type}' configuration on port {port}"
    )

    uvicorn.run(app, host="0.0.0.0", port=port)
