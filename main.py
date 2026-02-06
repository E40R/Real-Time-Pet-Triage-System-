"""
Main Entry Point
Run this file to start the Pet Health Voice Agent
"""
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from config import Config
from agent import PetHealthVoiceAgent
from utils import Logger


async def main():
    """Main entry point"""
    try:
        # Load configuration
        config = Config.load()
        
        # Create agent
        agent = PetHealthVoiceAgent(config)
        
        # Start agent
        await agent.start()
    
    except ValueError as e:
        # Configuration error (e.g., missing API key)
        Logger.error(f"Configuration error: {e}")
        Logger.info("Please set PERPLEXITY_API_KEY in your .env file")
    
    except KeyboardInterrupt:
        Logger.info("Goodbye! Take care of your pet! 🐾")
    
    except Exception as e:
        Logger.error(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
