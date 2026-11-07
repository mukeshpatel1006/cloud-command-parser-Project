
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "EleutherAI/pythia-70m"

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_name)

print("Loading model...")
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float32
)

model.to("cpu")
model.eval()

print("Model loaded successfully!")
print("Device:", next(model.parameters()).device)
print("Parameters:", sum(p.numel() for p in model.parameters()))

text = "Command: set an alarm for seven am tomorrow\nJSON:"
inputs = tokenizer(text, return_tensors="pt")

with torch.no_grad():
    output = model.generate(
        **inputs,
        max_new_tokens=40
    )

print("\nModel output:")
print(tokenizer.decode(output[0], skip_special_tokens=True))
