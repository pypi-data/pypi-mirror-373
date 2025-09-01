import torch
from transformers import AutoTokenizer, AutoConfig, AutoModelForCausalLM
from .model_hf import LilleConfig, LilleForCausalLM

class LilleHuggingFace:
    """A wrapper for the Lille-130m model using the Hugging Face backend."""

    def __init__(self, repo_id="Nikity/lille-130m-instruct"):
        AutoConfig.register("lille-130m", LilleConfig)
        AutoModelForCausalLM.register(LilleConfig, LilleForCausalLM)
        
        self.repo_id = repo_id
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.torch_dtype = self._get_torch_dtype()
        
        print(f"Loading tokenizer from '{self.repo_id}'...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.repo_id)
        
        print(f"Loading model from '{self.repo_id}' to '{self.device}'...")
        self.model = AutoModelForCausalLM.from_pretrained(
            self.repo_id,
            torch_dtype=self.torch_dtype,
            device_map=self.device,
        )
        self.model.eval()

        print("Compiling model for faster inference...")
        self.model = torch.compile(self.model, mode="reduce-overhead", fullgraph=True)
        self._warmup()

        self.history = []

    def _get_torch_dtype(self):
        if torch.cuda.is_available():
            if torch.cuda.is_bf16_supported():
                print("Hardware supports bfloat16, using it for better performance.")
                return torch.bfloat16
            else:
                print("Hardware does not support bfloat16, falling back to float16.")
                return torch.float16
        return torch.float32

    def _warmup(self):
        print("Performing a warmup run...")
        with torch.inference_mode():
            _ = self.model.generate(
                self.tokenizer("<|startoftext|>", return_tensors="pt").input_ids.to(self.device),
                max_new_tokens=2,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.pad_token_id
            )
        print("Warmup complete.")

    def generate(self, prompt: str, max_new_tokens=500, temperature=0.5, top_p=0.95, do_sample=True):
        if not prompt.startswith(self.tokenizer.bos_token):
            prompt = self.tokenizer.bos_token + prompt

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        with torch.inference_mode():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.pad_token_id,
                do_sample=do_sample,
                temperature=temperature,
                top_p=top_p,
                use_cache=True
            )
        response_ids = outputs[0][inputs['input_ids'].shape[1]:]
        return self.tokenizer.decode(response_ids, skip_special_tokens=True)

    def chat(self, user_prompt: str, max_new_tokens=500, temperature=0.5, top_p=0.95, do_sample=True):
        self.history.append({"role": "user", "content": user_prompt})
        prompt = self.tokenizer.apply_chat_template(self.history, tokenize=False, add_generation_prompt=True)
        
        response_text = self.generate(prompt, max_new_tokens, temperature, top_p, do_sample)
        
        self.history.append({"role": "assistant", "content": response_text})
        return response_text

    def reset_chat(self):
        """Clears the conversation history."""
        self.history = []
