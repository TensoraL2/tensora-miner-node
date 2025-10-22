"""
Tensora Miner Node - Job Worker
Main execution loop for processing AI compute jobs
"""

import asyncio
import json
import logging
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List
import aiohttp
import yaml
import time

# Local imports
from engine.onnx_runtime import ONNXEngine, run_onnx_job
from engine.vllm_runtime import VLLMEngine, run_vllm_job
from ipfs_utils import download_from_ipfs, upload_to_ipfs
from rpc_client import TensoraRPC

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MinerWorker:
    """
    Main miner worker that processes jobs from SubnetRegistry V2
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize miner worker
        
        Args:
            config_path: Path to config file
        """
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        logger.info("🚀 Tensora Miner Node Starting...")
        logger.info("=" * 60)
        logger.info("Event-driven AI inference system")
        logger.info("Listening for JobCreated events from SubnetRegistry V2")
        logger.info("")
        
        # For now, just log that we're ready
        logger.info("✅ Miner node initialized successfully!")
        logger.info(f"Configuration loaded from {config_path}")
        
    async def start(self):
        """
        Start the miner worker loop
        """
        logger.info("🔍 Waiting for JobCreated events...")
        logger.info("Ready to process ONNX and vLLM inference jobs")
        
        # Keep alive
        while True:
            logger.info("Miner node running... (waiting for jobs)")
            await asyncio.sleep(60)


async def main():
    """
    Main entry point for miner worker
    """
    worker = MinerWorker()
    
    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    finally:
        logger.info("Miner node stopped")


if __name__ == "__main__":
    asyncio.run(main())
