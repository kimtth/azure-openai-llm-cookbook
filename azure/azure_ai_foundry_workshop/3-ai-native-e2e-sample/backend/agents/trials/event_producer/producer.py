"""Trial Data Producer Module.

This module generates simulated trial events that feed into the event-driven architecture.
Generated events (with vital signs and adverse event data) are sent to Azure Event Hubs,
which then triggers multi-agent processing via the event consumer.
"""

import json
import random
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData
import logging
from utils.telemetry import tracer

from config import EVENT_HUBS_CONFIG

logger = logging.getLogger(__name__)

# Log config values at module import (without sensitive data)
logger.info("Producer module loaded with config:")
logger.info(f"Event Hub Name: {EVENT_HUBS_CONFIG.get('eventhub_name')}")
logger.info(f"Consumer Group: {EVENT_HUBS_CONFIG.get('consumer_group')}")
logger.info(f"Connection String Present: {bool(EVENT_HUBS_CONFIG.get('connection_string'))}")

def generate_trial_event() -> Dict[str, Any]:
    """Generate a simulated trial event with random data."""
    return {
        "trialId": f"CTO{random.randint(1,1000):03d}",
        "patientId": f"P{random.randint(1,1000):03d}",
        "studyArm": random.choice(["Drug A", "Drug B", "Placebo"]),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "vitals": {
            "heartRate": random.randint(60, 100),
            "bloodPressure": f"{random.randint(110,140)}/{random.randint(60,90)}",
            "temperature": round(random.uniform(36.1, 37.2), 1),
            "respiratoryRate": random.randint(12, 20),
            "oxygenSaturation": random.randint(95, 100)
        },
        "adverseEvents": [
            {
                "type": random.choice(["Mild", "Moderate", "Severe"]),
                "description": random.choice([
                    "Headache",
                    "Nausea",
                    "Fatigue",
                    "Dizziness",
                    None,
                    None,
                    None
                ])
            }
        ] if random.random() < 0.3 else []
    }

async def simulate_trial_data(num_events: int = 1) -> list:
    """Generate and send simulated trial data to Event Hub."""
    try:
        connection_string = EVENT_HUBS_CONFIG.get("connection_string")
        logger.info("Connection string type: %s", type(connection_string))
        logger.info("Connection string length: %s", len(connection_string) if connection_string else 0)
        logger.info("Connection string first 10 chars: %s", connection_string[:10] if connection_string else None)
        
        if not EVENT_HUBS_CONFIG.get('connection_string'):
            raise ValueError("Event Hubs connection string is missing or None")
            
        # Create and use EventHubProducerClient to send trial events
        logger.info("About to create EventHubProducerClient with connection string")
        producer = EventHubProducerClient.from_connection_string(
            conn_str=EVENT_HUBS_CONFIG["connection_string"],
            eventhub_name=EVENT_HUBS_CONFIG["eventhub_name"]
        )
        logger.info("Successfully created EventHubProducerClient")
        
        events = [generate_trial_event() for _ in range(num_events)]
        
        async with producer:
            event_data_batch = await producer.create_batch()
            for event in events:
                event_data = EventData(json.dumps(event))
                event_data_batch.add(event_data)
            await producer.send_batch(event_data_batch)
            logger.info(f"Successfully sent {len(events)} events to Event Hub")
            
        return events
        
    except Exception as e:
        logger.error(f"Error simulating trial data: {str(e)}", exc_info=True)
        raise RuntimeError(f"Error simulating trial data: {str(e)}") from e

async def start_continuous_simulation(
    interval_seconds: float = 5.0,
    max_events: Optional[int] = None
) -> None:
    """
    Start continuous trial data simulation.
    
    This function simulates trial events indefinitely (or up to max_events) and
    continuously feeds events into the processing pipeline.
    
    Args:
        interval_seconds: Time between event batches.
        max_events: Optional maximum number of events to generate.
    """
    events_sent = 0
    try:
        while True:
            await simulate_trial_data()
            events_sent += 1
            if max_events and events_sent >= max_events:
                break
            await asyncio.sleep(interval_seconds)
            
    except asyncio.CancelledError:
        pass
    except Exception as e:
        raise RuntimeError(f"Error in continuous simulation: {str(e)}") from e
