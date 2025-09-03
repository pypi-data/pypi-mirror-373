from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class LLMWrapper:
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.hidden_size = model.config.hidden_size

    def generate(self, prompt: str, context=None) -> str:
        if context is not None:
            prompt = f"{prompt}\n[Vision Context]: {context.detach().cpu().numpy().tolist()}"
        inputs = self.tokenizer(prompt, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_new_tokens=100)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

def load_llm(name: str) -> LLMWrapper:
    tokenizer = AutoTokenizer.from_pretrained(name)
    model = AutoModelForCausalLM.from_pretrained(name)
    return LLMWrapper(model, tokenizer)
