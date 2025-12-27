"""
This module handles the model inference using vLLM.
"""
from vllm import LLM, SamplingParams

# Note: The following configuration is designed for a single NVIDIA L40 GPU (~48 GB VRAM)
# as specified in the project's spec.md.
# Running this code requires appropriate hardware and CUDA drivers.

class Model:
    def __init__(self, model_name: str = "Qwen/Qwen2.5-14B-Instruct", dtype="bfloat16", gpu_memory_utilization=0.95):
        self.model_name = model_name
        self.sampling_params = SamplingParams(temperature=0.7, top_p=0.95, max_tokens=2048)
        
        # This part requires a GPU
        try:
            self.llm = LLM(
                model=self.model_name,
                dtype=dtype,
                gpu_memory_utilization=gpu_memory_utilization,
            )
            print(f"Successfully loaded model: {self.model_name}")
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Please ensure you are running on a machine with a compatible GPU and CUDA drivers.")
            self.llm = None


    def generate(self, prompt: str):
        """
        Generates text from a prompt.
        """
        if self.llm is None:
            return "Error: Model not loaded. Cannot generate text."
            
        print(f"Generating text for prompt: {prompt[:100]}...")
        
        # This part requires a GPU
        try:
            outputs = self.llm.generate(prompt, self.sampling_params)
            return outputs[0].outputs[0].text
        except Exception as e:
            print(f"Error during text generation: {e}")
            return "Error: Text generation failed."

# Singleton instance of the model, to be initialized at startup.
# We will initialize it in the main application file to control the lifecycle.
model_instance: Model = None

def get_model():
    return model_instance

def initialize_model():
    global model_instance
    if not model_instance:
        model_instance = Model()

