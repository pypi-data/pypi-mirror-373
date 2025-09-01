import pickle
import torch
import torch.nn.functional as F
import numpy as np
import onnxruntime
from onnxruntime import OrtValue
import tiktoken
from huggingface_hub import hf_hub_download
from typing import Optional

def _apply_sampling(logits: torch.Tensor, temp: float, top_p: Optional[float], top_k: Optional[int]) -> int:
    if temp == 0.0:
        return torch.argmax(logits, dim=-1).item()
    logits /= temp
    if top_p is not None:
        probs = F.softmax(logits, dim=-1)
        sorted_probs, sorted_indices = torch.sort(probs, descending=True)
        cumulative_probs = torch.cumsum(sorted_probs, dim=-1)
        sorted_indices_to_remove = cumulative_probs > top_p
        sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
        sorted_indices_to_remove[..., 0] = 0
        indices_to_remove = sorted_indices_to_remove.scatter(0, sorted_indices, sorted_indices_to_remove)
        logits[indices_to_remove] = -float('Inf')
    elif top_k is not None:
        v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
        logits[logits < v[-1]] = -float('Inf')

    probs = F.softmax(logits, dim=-1)
    return torch.multinomial(probs, num_samples=1).item()

class LilleONNX:
    """A wrapper for the Lille-130m model using the ONNX Runtime backend."""

    def __init__(self, repo_id="Nikity/lille-130m-instruct"):
        self.repo_id = repo_id
        self.device = 'cuda' if 'CUDAExecutionProvider' in onnxruntime.get_available_providers() else 'cpu'
        
        print("Downloading and loading tokenizer and ONNX model...")
        tokenizer_path = hf_hub_download(repo_id=self.repo_id, filename="tokenizer/Hastings.pkl")
        onnx_model_path = hf_hub_download(repo_id=self.repo_id, filename="lille-130m_fp16_kv.onnx")
        
        with open(tokenizer_path, 'rb') as f:
            hastings = pickle.load(f)
        self.tokenizer = tiktoken.core.Encoding(hastings.pop('name'), **hastings)

        providers = ['CPUExecutionProvider']
        if self.device == 'cuda':
            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        
        self.session = onnxruntime.InferenceSession(onnx_model_path, providers=providers)
        print(f"ONNX model loaded successfully on provider: {self.session.get_providers()[0]}")

        num_outputs = len(self.session.get_outputs())
        if (num_outputs - 1) % 2 != 0:
            raise RuntimeError(f"Unexpected number of outputs ({num_outputs}) in the ONNX model.")
        self.n_layers = (num_outputs - 1) // 2

        model_inputs = self.session.get_inputs()
        past_key_input = next((inp for inp in model_inputs if inp.name == 'past_key_0'), None)
        if past_key_input is None:
            raise RuntimeError("Could not find 'past_key_0' in the model's inputs.")
        
        shape = past_key_input.shape
        self.n_kv_heads = shape[1]
        self.head_dim = shape[3]
        
        self.history = []

    def generate(self, prompt: str, max_new_tokens=500, temperature=0.5, top_p=0.95, do_sample=True, top_k=None):
        if not do_sample:
            temperature = 0.0
        
        prompt_ids = self.tokenizer.encode(prompt, allowed_special="all")
        input_ids = np.array([prompt_ids], dtype=np.int64)
        
        ort_inputs = {'input_ids': input_ids}
        for i in range(self.n_layers):
            empty_past = np.zeros((1, self.n_kv_heads, 0, self.head_dim), dtype=np.float16)
            ort_inputs[f'past_key_{i}'] = empty_past
            ort_inputs[f'past_value_{i}'] = empty_past

        output_names = [out.name for out in self.session.get_outputs()]
        logits_numpy, *past_key_values_np = self.session.run(output_names, ort_inputs)
        
        last_token_logits = torch.from_numpy(logits_numpy[0, -1, :])
        next_token_id = _apply_sampling(last_token_logits, temperature, top_p, top_k)
        
        stop_ids = [self.tokenizer.encode_single_token(t) for t in ["<|endoftext|>", "<|user|>"]]
        generated_ids = []
        
        past_key_values = [OrtValue.ortvalue_from_numpy(v, self.device) for v in past_key_values_np]
        
        binding = self.session.io_binding()
        
        single_token_input_ort = OrtValue.ortvalue_from_numpy(
            np.array([[next_token_id]], dtype=np.int64), self.device
        )

        for _ in range(max_new_tokens):
            if next_token_id in stop_ids:
                break
            generated_ids.append(next_token_id)
            
            binding.bind_ortvalue_input('input_ids', single_token_input_ort)
            for i in range(self.n_layers):
                binding.bind_ortvalue_input(f'past_key_{i}', past_key_values[i*2])
                binding.bind_ortvalue_input(f'past_value_{i}', past_key_values[i*2+1])
            
            binding.bind_output('logits', self.device)
            for i in range(self.n_layers):
                binding.bind_output(f'present_key_{i}', self.device)
                binding.bind_output(f'present_value_{i}', self.device)
            
            self.session.run_with_iobinding(binding)
            
            outputs = binding.get_outputs()
            logits_ort, past_key_values = outputs[0], outputs[1:]
            
            next_token_logits = torch.from_numpy(logits_ort.numpy()[0, 0, :])
            next_token_id = _apply_sampling(next_token_logits, temperature, top_p, top_k)
            
            single_token_input_ort.update_inplace(np.array([[next_token_id]], dtype=np.int64))

        return self.tokenizer.decode(generated_ids)

    def chat(self, user_prompt: str, max_new_tokens=500, temperature=0.5, top_p=0.95, do_sample=True, top_k=None):
        self.history.append({"role": "user", "content": user_prompt})
        
        prompt_parts = ["<|startoftext|>"]
        for msg in self.history:
            if msg['role'] == 'user':
                prompt_parts.append(f"<|user|>{msg['content']}<|assistant|>")
            else:
                prompt_parts.append(f"{msg['content']}<|endoftext|>")

        if self.history[-1]['role'] == 'user':
            full_prompt = "".join(prompt_parts)
        else:
            full_prompt = "".join(prompt_parts[:-1])

        response_text = self.generate(full_prompt, max_new_tokens, temperature, top_p, do_sample, top_k)
        
        self.history.append({"role": "assistant", "content": response_text})
        return response_text

    def reset_chat(self):
        """Clears the conversation history."""
        self.history = []
