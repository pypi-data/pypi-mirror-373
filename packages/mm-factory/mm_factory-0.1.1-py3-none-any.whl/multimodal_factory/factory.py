from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    CLIPModel,
    CLIPProcessor,
    VisionEncoderDecoderModel,
    ViTImageProcessor,
)

# Registry of supported models
TEXT_MODELS = {
    "distilgpt2": "distilgpt2",        # very small
    "tiny-gpt2": "sshleifer/tiny-gpt2" # toy model for quick tests
}

VISION_MODELS = {
    "clip-vit": "openai/clip-vit-base-patch16",     # small CLIP
    "clip-vit-small": "openai/clip-vit-base-patch32", # smaller
    "tiny-vit": "WinKawaks/vit-tiny-patch16-224"    # very small ViT
}

MULTIMODAL_MODELS = {
    "vit-gpt2": "nlpconnect/vit-gpt2-image-captioning",  # vision + text
    "blip-tiny": "Salesforce/blip-image-captioning-base" # lightweight BLIP
}


def create_multimodal_model(llm_name: str = None, vision_name: str = None, multimodal_name: str = None):
    """
    Create a multimodal model based on user choice.
    - llm_name: pick from TEXT_MODELS
    - vision_name: pick from VISION_MODELS
    - multimodal_name: pick from MULTIMODAL_MODELS
    """

    if multimodal_name:
        if multimodal_name not in MULTIMODAL_MODELS:
            raise ValueError(f"Unsupported multimodal model {multimodal_name}. Available: {list(MULTIMODAL_MODELS.keys())}")
        model_id = MULTIMODAL_MODELS[multimodal_name]
        model = VisionEncoderDecoderModel.from_pretrained(model_id)
        processor = ViTImageProcessor.from_pretrained(model_id)
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        return {"model": model, "processor": processor, "tokenizer": tokenizer}

    components = {}

    if llm_name:
        if llm_name not in TEXT_MODELS:
            raise ValueError(f"Unsupported LLM {llm_name}. Available: {list(TEXT_MODELS.keys())}")
        model_id = TEXT_MODELS[llm_name]
        components["llm"] = AutoModelForCausalLM.from_pretrained(model_id)
        components["tokenizer"] = AutoTokenizer.from_pretrained(model_id)

    if vision_name:
        if vision_name not in VISION_MODELS:
            raise ValueError(f"Unsupported vision model {vision_name}. Available: {list(VISION_MODELS.keys())}")
        model_id = VISION_MODELS[vision_name]
        components["vision"] = CLIPModel.from_pretrained(model_id)
        components["processor"] = CLIPProcessor.from_pretrained(model_id)

    if not components:
        raise ValueError("You must specify at least one of llm_name, vision_name, or multimodal_name.")

    return components
