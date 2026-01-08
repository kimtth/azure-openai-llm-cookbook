import os
import requests
import hashlib
import torch
import re
import jaconv
import numpy as np
from PIL import Image
from ultralytics import YOLO
from transformers import (
    ViTImageProcessor,
    AutoTokenizer,
    VisionEncoderDecoderModel,
    GenerationMixin,
)
from openai import AzureOpenAI

AZURE_OPENAI_API_KEY = "<your-api-key>"  # Replace with your OpenAI API key
AZURE_OPENAI_MODEL_NAME = "<your-value>"  # Vision model for image analysis
AZURE_OPENAI_API_VERSION = "<your-value>"  # API version for OpenAI
AZURE_OPENAI_ENDPOINT = "https://<your-value>.openai.azure.com"


# Define base directory for models
models_base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
os.makedirs(models_base_dir, exist_ok=True)

# Define model data
manga_ocr_data = {
    "url": "https://huggingface.co/kha-white/manga-ocr-base/resolve/main/",
    "files": [
        "pytorch_model.bin",
        "config.json",
        "preprocessor_config.json",
        "README.md",
        "special_tokens_map.json",
        "tokenizer_config.json",
        "vocab.txt",
    ],
    "sha256_pre_calculated": [
        "c63e0bb5b3ff798c5991de18a8e0956c7ee6d1563aca6729029815eda6f5c2eb",
        "8c0e395de8fa699daaac21aee33a4ba9bd1309cfbff03147813d2a025f39f349",
        "af4eb4d79cf61b47010fc0bc9352ee967579c417423b4917188d809b7e048948",
        "32f413afcc4295151e77d25202c5c5d81ef621b46f947da1c3bde13256dc0d5f",
        "303df45a03609e4ead04bc3dc1536d0ab19b5358db685b6f3da123d05ec200e3",
        "d775ad1deac162dc56b84e9b8638f95ed8a1f263d0f56f4f40834e26e205e266",
        "344fbb6b8bf18c57839e924e2c9365434697e0227fac00b88bb4899b78aa594d",
    ],
    "save_dir": os.path.join(models_base_dir, "ocr", "manga-ocr-base"),
}

comic_text_segmenter_data = {
    "url": "https://huggingface.co/ogkalu/comic-text-segmenter-yolov8m/resolve/main/",
    "files": ["comic-text-segmenter.pt"],
    "sha256_pre_calculated": [
        "f2dded0d2f5aaa25eed49f1c34a4720f1c1cd40da8bc3138fde1abb202de625e",
    ],
    "save_dir": os.path.join(models_base_dir, "detection"),
}

comic_bubble_detector_data = {
    "url": "https://huggingface.co/ogkalu/comic-speech-bubble-detector-yolov8m/resolve/main/",
    "files": ["comic-speech-bubble-detector.pt"],
    "sha256_pre_calculated": [
        "10bc9f702698148e079fb4462a6b910fcd69753e04838b54087ef91d5633097b"
    ],
    "save_dir": os.path.join(models_base_dir, "detection"),
}


class MangaOcrModel(VisionEncoderDecoderModel, GenerationMixin):
    pass


class MangaOcr:
    def __init__(self, pretrained_model_name_or_path, device="cpu"):
        self.processor = ViTImageProcessor.from_pretrained(
            pretrained_model_name_or_path
        )
        self.tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path)
        self.model = MangaOcrModel.from_pretrained(pretrained_model_name_or_path)
        self.to(device)

    def to(self, device):
        self.model.to(device)

    @torch.no_grad()
    def __call__(self, img: np.ndarray):
        # Make sure image has the right format (RGB if grayscale)
        if len(img.shape) == 2:  # Grayscale image
            img = np.stack([img, img, img], axis=2)  # Convert to 3-channel
        elif len(img.shape) == 3 and img.shape[2] == 1:  # Grayscale with channel
            img = np.concatenate([img, img, img], axis=2)  # Convert to 3-channel
        elif len(img.shape) == 3 and img.shape[2] == 4:  # RGBA image
            img = img[:, :, :3]  # Remove alpha channel

        # Process the image
        inputs = self.processor(images=img, return_tensors="pt")
        x = inputs.pixel_values.squeeze()

        # Generate text
        x = self.model.generate(x[None].to(self.model.device))[0].cpu()
        x = self.tokenizer.decode(x, skip_special_tokens=True)
        x = post_process(x)
        return x


def post_process(text):
    text = "".join(text.split())
    text = text.replace("…", "...")
    text = re.sub("[・.]{2,}", lambda x: (x.end() - x.start()) * ".", text)
    # 「ひらがな」以外全角文字を半角に変換
    # Convert full-width characters to half-width characters except for "hiragana"
    text = jaconv.h2z(text, ascii=True, digit=True)

    return text


def verify_and_download_models():
    """Download and verify model files if necessary"""
    for model_data in [
        manga_ocr_data,
        comic_text_segmenter_data,
        comic_bubble_detector_data,
    ]:
        os.makedirs(model_data["save_dir"], exist_ok=True)

        for i, file_name in enumerate(model_data["files"]):
            file_path = os.path.join(model_data["save_dir"], file_name)
            expected_hash = model_data["sha256_pre_calculated"][i]

            # Check if file exists and has correct hash
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                if file_hash == expected_hash:
                    print(f"File {file_name} already exists with correct checksum")
                    continue

            # Download file
            print(f"Downloading {file_name}...")
            url = model_data["url"] + file_name
            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Downloaded {file_name}")


def load_models():
    """Load all required models"""
    # Load text segmenter model
    text_segmenter_path = os.path.join(
        comic_text_segmenter_data["save_dir"], comic_text_segmenter_data["files"][0]
    )
    text_model = YOLO(text_segmenter_path)

    # Load bubble detector model
    bubble_detector_path = os.path.join(
        comic_bubble_detector_data["save_dir"], comic_bubble_detector_data["files"][0]
    )
    bubble_model = YOLO(bubble_detector_path)

    # Load manga OCR model
    ocr_model_path = manga_ocr_data["save_dir"]
    manga_ocr = MangaOcr(pretrained_model_name_or_path=ocr_model_path)

    return text_model, bubble_model, manga_ocr


def detect_text_and_bubbles(image_path, text_model, bubble_model):
    """Detect text and speech bubbles in image"""
    image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), image_path)
    image = Image.open(image_path)

    # Run text detection
    text_results = text_model(image)
    text_boxes = []
    for result in text_results:
        for box in result.boxes.data.cpu().numpy():
            x1, y1, x2, y2, conf, _ = box
            if conf > 0.5:  # Confidence threshold
                text_boxes.append((int(x1), int(y1), int(x2), int(y2)))

    # Run bubble detection
    bubble_results = bubble_model(image)
    bubble_boxes = []
    for result in bubble_results:
        for box in result.boxes.data.cpu().numpy():
            x1, y1, x2, y2, conf, _ = box
            if conf > 0.5:  # Confidence threshold
                bubble_boxes.append((int(x1), int(y1), int(x2), int(y2)))

    return image, text_boxes, bubble_boxes


def perform_ocr(image, boxes, manga_ocr):
    """Extract text from detected regions using OCR"""
    results = []
    for box in boxes:
        x1, y1, x2, y2 = box
        cropped = image.crop((x1, y1, x2, y2))

        # Convert PIL image to numpy array for the manga_ocr model
        cropped_array = np.array(cropped)

        # Perform OCR using the new manga_ocr model
        text = manga_ocr(cropped_array)

        if text:
            results.append({"box": box, "text": text})

    return results


def translate_with_azure_openai(texts):
    """Translate detected text using Azure OpenAI"""
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY") or AZURE_OPENAI_API_KEY,
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", AZURE_OPENAI_API_VERSION),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", AZURE_OPENAI_ENDPOINT),
    )

    translated_texts = []
    for item in texts:
        original_text = item["text"]

        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", AZURE_OPENAI_MODEL_NAME),
            messages=[
                {
                    "role": "system",
                    "content": "Translate Japanese manga text to English.",
                },
                {"role": "user", "content": f"Translate: {original_text}"},
            ],
        )

        translation = response.choices[0].message.content
        translated_texts.append(
            {"box": item["box"], "original": original_text, "translation": translation}
        )

    return translated_texts


def main(image_path):
    # Download models if needed
    print("Verifying and downloading models...")
    verify_and_download_models()

    # Load models
    print("Loading models...")
    text_model, bubble_model, manga_ocr = load_models()

    # Detect text and bubbles
    print("Detecting text and bubbles...")
    image, text_boxes, bubble_boxes = detect_text_and_bubbles(
        image_path, text_model, bubble_model
    )
    print(
        f"Detected {len(text_boxes)} text regions and {len(bubble_boxes)} speech bubbles"
    )

    # Perform OCR on detected regions
    print("Performing OCR...")
    ocr_results = perform_ocr(image, text_boxes, manga_ocr)
    print(f"OCR succeeded on {len(ocr_results)} text regions")

    # Translate text with Azure OpenAI
    print("Translating text...")
    translations = translate_with_azure_openai(ocr_results)

    # Print results
    print("\nTranslation Results:")
    for item in translations:
        print(f"Original: {item['original']}")
        print(f"Translation: {item['translation']}")
        print("-" * 40)

    return translations


if __name__ == "__main__":
    print("Manga text detection and translation")
    image_path = "manga.png"

    main(image_path)
