import asyncio
import aiohttp
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_simulation():
    """Test the trial event simulation endpoint."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post('http://localhost:8003/api/trials/simulate', 
                                  json={'num_events': 3}) as response:
                logger.info(f'Status: {response.status}')
                result = await response.text()
                logger.info(f'Response: {result}')
                return response.status == 200
    except Exception as e:
        logger.error(f"Error testing simulation: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_simulation())
