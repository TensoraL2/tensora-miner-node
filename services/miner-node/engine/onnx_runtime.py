"""
ONNX Runtime Engine for Tensora Miner Node
Deterministic AI inference execution
"""

import onnxruntime as ort
import numpy as np
import hashlib
import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)


class ONNXEngine:
    """
    ONNX model execution engine with deterministic inference
    """
    
    def __init__(self, model_path: str):
        """
        Initialize ONNX session
        
        Args:
            model_path: Path to .onnx model file
        """
        self.model_path = Path(model_path)
        
        # Set deterministic execution
        session_options = ort.SessionOptions()
        session_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_DISABLE_ALL
        
        # Create session
        self.session = ort.InferenceSession(
            str(self.model_path),
            sess_options=session_options,
            providers=['CPUExecutionProvider']  # Deterministic on CPU
        )
        
        self.input_names = [inp.name for inp in self.session.get_inputs()]
        self.output_names = [out.name for out in self.session.get_outputs()]
        
        logger.info(f"ONNX model loaded: {model_path}")
        logger.info(f"Inputs: {self.input_names}")
        logger.info(f"Outputs: {self.output_names}")
    
    def prepare_input(self, input_data: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """
        Convert input JSON to numpy arrays
        
        Args:
            input_data: Dict of input tensors
            
        Returns:
            Dict mapping input names to numpy arrays
        """
        prepared = {}
        
        for name in self.input_names:
            if name not in input_data:
                raise ValueError(f"Missing input: {name}")
            
            # Convert to numpy array
            arr = np.array(input_data[name])
            
            # Ensure correct dtype (float32 for most models)
            if arr.dtype != np.float32:
                arr = arr.astype(np.float32)
            
            prepared[name] = arr
        
        return prepared
    
    def run_inference(self, input_data: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """
        Execute inference and compute result hash
        
        Args:
            input_data: Input tensors as dict
            
        Returns:
            Tuple of (outputs dict, result hash)
        """
        try:
            # Prepare inputs
            prepared_inputs = self.prepare_input(input_data)
            
            # Run inference
            logger.info("Running ONNX inference...")
            outputs = self.session.run(self.output_names, prepared_inputs)
            
            # Convert outputs to serializable dict
            output_dict = {}
            for name, tensor in zip(self.output_names, outputs):
                output_dict[name] = tensor.tolist()  # Convert numpy to list
            
            # Compute deterministic hash
            result_hash = self.compute_hash(output_dict)
            
            logger.info(f"Inference complete. Result hash: {result_hash}")
            
            return output_dict, result_hash
            
        except Exception as e:
            logger.error(f"ONNX inference failed: {e}")
            raise
    
    @staticmethod
    def compute_hash(output_dict: Dict[str, Any]) -> str:
        """
        Compute deterministic hash of outputs
        
        Args:
            output_dict: Output tensors
            
        Returns:
            SHA256 hash as hex string
        """
        # Sort keys for determinism
        json_str = json.dumps(output_dict, sort_keys=True, separators=(',', ':'))
        
        # Compute SHA256
        result_hash = hashlib.sha256(json_str.encode('utf-8')).hexdigest()
        
        return f"0x{result_hash}"
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model metadata
        
        Returns:
            Dict with input/output shapes and types
        """
        inputs_info = []
        for inp in self.session.get_inputs():
            inputs_info.append({
                "name": inp.name,
                "shape": inp.shape,
                "type": str(inp.type)
            })
        
        outputs_info = []
        for out in self.session.get_outputs():
            outputs_info.append({
                "name": out.name,
                "shape": out.shape,
                "type": str(out.type)
            })
        
        return {
            "inputs": inputs_info,
            "outputs": outputs_info
        }


def run_onnx_job(model_path: str, input_data: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    """
    Convenience function to run a complete ONNX job
    
    Args:
        model_path: Path to .onnx model
        input_data: Input tensors
        
    Returns:
        Tuple of (outputs, result_hash)
    """
    engine = ONNXEngine(model_path)
    return engine.run_inference(input_data)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Test with a simple model (would be downloaded from IPFS in production)
    print("ONNX Runtime Engine - Ready for Tensora Miner Beta")
    print("=" * 60)
    print("Supports deterministic AI inference with verifiable results")
    print("")
    print("Usage:")
    print("  engine = ONNXEngine('model.onnx')")
    print("  outputs, hash = engine.run_inference(inputs)")
    print("  # Submit hash to SubnetJobs contract")

