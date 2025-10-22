"""
vLLM Runtime Engine for Tensora Miner Node
Deterministic LLM inference execution
"""

from vllm import LLM, SamplingParams
import hashlib
import json
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)


class VLLMEngine:
    """
    vLLM model execution engine with deterministic inference
    """
    
    def __init__(self, model_name: str, gpu_memory_utilization: float = 0.9):
        """
        Initialize vLLM engine
        
        Args:
            model_name: HuggingFace model name or local path
            gpu_memory_utilization: GPU memory to use (0.0-1.0)
        """
        self.model_name = model_name
        
        logger.info(f"Loading vLLM model: {model_name}")
        
        # Initialize LLM with deterministic settings
        self.llm = LLM(
            model=model_name,
            seed=0,  # Deterministic seed
            gpu_memory_utilization=gpu_memory_utilization,
            trust_remote_code=True,
            dtype="float16"
        )
        
        logger.info(f"vLLM model loaded successfully")
    
    def run_inference(
        self,
        prompts: List[str],
        max_tokens: int = 100,
        temperature: float = 0.0
    ) -> Tuple[List[str], str]:
        """
        Execute LLM inference with deterministic sampling
        
        Args:
            prompts: List of text prompts
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 = deterministic)
            
        Returns:
            Tuple of (generated texts, result hash)
        """
        try:
            # Deterministic sampling parameters
            sampling_params = SamplingParams(
                temperature=temperature,
                max_tokens=max_tokens,
                seed=0,  # Deterministic
                top_p=1.0,
                top_k=-1,  # Disabled for determinism
                use_beam_search=False
            )
            
            logger.info(f"Running vLLM inference on {len(prompts)} prompts...")
            
            # Generate
            outputs = self.llm.generate(prompts, sampling_params)
            
            # Extract generated texts
            generated_texts = []
            for output in outputs:
                text = output.outputs[0].text
                generated_texts.append(text)
            
            # Create result structure
            results = {
                "prompts": prompts,
                "outputs": generated_texts,
                "model": self.model_name,
                "params": {
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "seed": 0
                }
            }
            
            # Compute deterministic hash
            result_hash = self.compute_hash(results)
            
            logger.info(f"vLLM inference complete. Result hash: {result_hash}")
            
            return generated_texts, result_hash
            
        except Exception as e:
            logger.error(f"vLLM inference failed: {e}")
            raise
    
    @staticmethod
    def compute_hash(results: Dict[str, Any]) -> str:
        """
        Compute deterministic hash of results
        
        Args:
            results: Results dict
            
        Returns:
            SHA256 hash as hex string
        """
        # Sort keys for determinism
        json_str = json.dumps(results, sort_keys=True, separators=(',', ':'))
        
        # Compute SHA256
        result_hash = hashlib.sha256(json_str.encode('utf-8')).hexdigest()
        
        return f"0x{result_hash}"
    
    def run_batch(
        self,
        prompts: List[str],
        batch_size: int = 8,
        max_tokens: int = 100
    ) -> Tuple[List[str], str]:
        """
        Run inference on large batch with batching
        
        Args:
            prompts: List of prompts
            batch_size: Batch size for processing
            max_tokens: Max tokens per output
            
        Returns:
            Tuple of (all outputs, combined hash)
        """
        all_outputs = []
        
        # Process in batches
        for i in range(0, len(prompts), batch_size):
            batch = prompts[i:i + batch_size]
            logger.info(f"Processing batch {i // batch_size + 1}/{(len(prompts) + batch_size - 1) // batch_size}")
            
            outputs, _ = self.run_inference(batch, max_tokens=max_tokens)
            all_outputs.extend(outputs)
        
        # Compute combined hash
        results = {
            "outputs": all_outputs,
            "model": self.model_name,
            "batch_size": batch_size
        }
        
        combined_hash = self.compute_hash(results)
        
        return all_outputs, combined_hash


def run_vllm_job(
    model_name: str,
    prompts: List[str],
    max_tokens: int = 100
) -> Tuple[List[str], str]:
    """
    Convenience function to run a complete vLLM job
    
    Args:
        model_name: Model to use
        prompts: Input prompts
        max_tokens: Max tokens to generate
        
    Returns:
        Tuple of (outputs, result_hash)
    """
    engine = VLLMEngine(model_name)
    return engine.run_inference(prompts, max_tokens=max_tokens)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    print("vLLM Runtime Engine - Ready for Tensora Miner Beta")
    print("=" * 60)
    print("Supports deterministic LLM inference with verifiable results")
    print("")
    print("Usage:")
    print("  engine = VLLMEngine('meta-llama/Llama-2-7b-hf')")
    print("  outputs, hash = engine.run_inference(['Hello, world!'])")
    print("  # Submit hash to SubnetJobs contract")
    print("")
    print("Note: Requires GPU and vLLM installed")
    print("  pip install vllm")

