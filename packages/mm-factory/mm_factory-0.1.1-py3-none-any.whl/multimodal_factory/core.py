from transformers import AutoModelForCausalLM, AutoTokenizer, CLIPModel, CLIPProcessor
from datasets import load_dataset
import torch
from torch.utils.data import DataLoader
from PIL import Image
from .adapters import LinearAdapter

class MultiModalModel:
    def __init__(self, llm_name, vision_name, adapter_type="linear", device="cuda"):
        self.device = device
        
        # Load LLM
        self.tokenizer = AutoTokenizer.from_pretrained(llm_name)
        self.llm = AutoModelForCausalLM.from_pretrained(llm_name).to(device)
        
        # Load vision encoder
        self.vision_model = CLIPModel.from_pretrained(vision_name).vision_model.to(device)
        self.processor = CLIPProcessor.from_pretrained(vision_name)
        
        # Adapter
        if adapter_type == "linear":
            self.adapter = LinearAdapter(self.vision_model.config.hidden_size,
                                         self.llm.config.hidden_size).to(device)
        else:
            raise NotImplementedError("Only 'linear' adapter implemented")

    def forward(self, image_path, prompt):
        # Process image
        image = Image.open(image_path).convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        vision_embeds = self.vision_model(**inputs).last_hidden_state[:,0,:]
        vision_proj = self.adapter(vision_embeds)
        
        # Process text
        tokenized = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        llm_inputs = torch.cat([vision_proj.unsqueeze(1), 
                                self.llm.get_input_embeddings()(tokenized.input_ids)], dim=1)
        
        outputs = self.llm(inputs_embeds=llm_inputs)
        return outputs.logits

    def finetune(self, dataset_name, epochs=1, batch_size=4, lr=5e-5):
        """Fine-tune adapter using HF dataset with 'image', 'instruction', 'output' fields."""
        dataset = load_dataset(dataset_name)
        dataloader = DataLoader(dataset['train'], batch_size=batch_size, shuffle=True)

        optimizer = torch.optim.Adam(self.adapter.parameters(), lr=lr)
        self.llm.eval()
        self.vision_model.eval()

        for epoch in range(epochs):
            for batch in dataloader:
                images = [Image.open(x).convert("RGB") for x in batch['image']]
                inputs = self.processor(images=images, return_tensors="pt", padding=True).to(self.device)
                vision_embeds = self.vision_model(**inputs).last_hidden_state[:,0,:]
                vision_proj = self.adapter(vision_embeds)

                tokenized = self.tokenizer(batch['instruction'], return_tensors="pt", padding=True).to(self.device)
                target_ids = self.tokenizer(batch['output'], return_tensors="pt", padding=True).input_ids.to(self.device)

                llm_inputs = torch.cat([vision_proj.unsqueeze(1), 
                                        self.llm.get_input_embeddings()(tokenized.input_ids)], dim=1)
                outputs = self.llm(inputs_embeds=llm_inputs)
                
                loss = torch.nn.functional.cross_entropy(outputs.logits.view(-1, outputs.logits.size(-1)), target_ids.view(-1))
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
            print(f"Epoch {epoch+1}/{epochs}, Loss: {loss.item()}")
