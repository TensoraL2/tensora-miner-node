"""
IPFS Utilities for Tensora Miner/Validator Nodes
Upload and download models, inputs, and results
"""

import aiohttp
import asyncio
import hashlib
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


async def download_from_ipfs(
    cid: str,
    gateway: str = "https://ipfs.io/ipfs/",
    timeout: int = 300
) -> Path:
    """
    Download file from IPFS
    
    Args:
        cid: IPFS CID (with or without ipfs:// prefix)
        gateway: IPFS gateway URL
        timeout: Download timeout in seconds
        
    Returns:
        Path to downloaded file
    """
    # Strip ipfs:// prefix if present
    if cid.startswith('ipfs://'):
        cid = cid[7:]
    
    url = f"{gateway}{cid}"
    cache_dir = Path.home() / '.tensora' / 'ipfs_cache'
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    # Check cache
    cache_path = cache_dir / cid
    if cache_path.exists():
        logger.info(f"Using cached file: {cid}")
        return cache_path
    
    logger.info(f"Downloading from IPFS: {cid}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                if response.status != 200:
                    raise Exception(f"IPFS download failed: HTTP {response.status}")
                
                # Download to cache
                with open(cache_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        f.write(chunk)
        
        logger.info(f"Downloaded {cache_path.stat().st_size} bytes")
        return cache_path
        
    except Exception as e:
        logger.error(f"IPFS download failed: {e}")
        raise


async def upload_to_ipfs(
    data: str,
    ipfs_api: str = "http://localhost:5001/api/v0"
) -> str:
    """
    Upload data to IPFS
    
    Args:
        data: String data to upload
        ipfs_api: IPFS API endpoint
        
    Returns:
        IPFS CID
    """
    try:
        async with aiohttp.ClientSession() as session:
            # Use IPFS HTTP API
            form_data = aiohttp.FormData()
            form_data.add_field('file', data.encode('utf-8'), filename='data.json')
            
            async with session.post(f"{ipfs_api}/add", data=form_data) as response:
                if response.status != 200:
                    raise Exception(f"IPFS upload failed: HTTP {response.status}")
                
                result = await response.json()
                cid = result['Hash']
                
                logger.info(f"Uploaded to IPFS: {cid}")
                return f"ipfs://{cid}"
                
    except Exception as e:
        logger.error(f"IPFS upload failed: {e}")
        
        # Fallback: return hash as placeholder
        content_hash = hashlib.sha256(data.encode()).hexdigest()
        logger.warning(f"Using hash as fallback CID: {content_hash}")
        return f"0x{content_hash}"


def verify_cid(data: bytes, expected_cid: str) -> bool:
    """
    Verify data matches expected CID
    
    Args:
        data: File data
        expected_cid: Expected IPFS CID
        
    Returns:
        True if matches
    """
    # Simplified verification (real impl would use multihash)
    actual_hash = hashlib.sha256(data).hexdigest()
    return expected_cid.endswith(actual_hash[:32])


async def pin_to_ipfs(cid: str, ipfs_api: str = "http://localhost:5001/api/v0"):
    """
    Pin CID to local IPFS node
    
    Args:
        cid: CID to pin
        ipfs_api: IPFS API endpoint
    """
    if cid.startswith('ipfs://'):
        cid = cid[7:]
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{ipfs_api}/pin/add?arg={cid}") as response:
                if response.status == 200:
                    logger.info(f"Pinned: {cid}")
                else:
                    logger.warning(f"Pin failed: HTTP {response.status}")
    except Exception as e:
        logger.warning(f"Failed to pin {cid}: {e}")


if __name__ == "__main__":
    # Test IPFS utils
    print("Tensora IPFS Utilities")
    print("=" * 60)
    print("Download: download_from_ipfs('QmHash')")
    print("Upload:   upload_to_ipfs(json_string)")
    print("Verify:   verify_cid(data, cid)")

