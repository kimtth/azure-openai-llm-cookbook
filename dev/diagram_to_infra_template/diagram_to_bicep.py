import os
import subprocess
import tempfile
from pathlib import Path
from openai import AzureOpenAI
from PIL import Image
import base64


AZURE_OPENAI_API_KEY = "your-api-key"  # Replace with your OpenAI API key
AZURE_OPENAI_MODEL_NAME = "your-model-name"  # Vision model for image analysis
AZURE_OPENAI_API_VERSION = "your-api-version"  # API version for OpenAI
AZURE_OPENAI_ENDPOINT = "your-endpoint"  # Azure endpoint for OpenAI


def diagram_to_bicep(image_path, api_key=None):
    """
    Convert a diagram image to Azure Bicep code using OpenAI's vision capabilities.

    Args:
        image_path: Path to the diagram image file
        api_key: OpenAI API key (defaults to OPENAI_API_KEY environment variable)

    Returns:
        Generated Bicep code as string
    """
    # Validate image path
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found at {image_path}")

    # Use environment variable if no API key provided
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY") or AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION or os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT") or AZURE_OPENAI_ENDPOINT,
    )

    # Read and encode the image
    with open(image_path, "rb") as img_file:
        img_data = base64.b64encode(img_file.read()).decode("utf-8")

    try:
        response = client.chat.completions.create(
            model=AZURE_OPENAI_MODEL_NAME or os.getenv("AZURE_OPENAI_MODEL_NAME"),
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Azure architect who converts infrastructure diagrams to Bicep code.",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Generate valid Bicep code representing the resources and their relationships shown in this diagram. Do not include any descriptive text or comments in the code.",
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{img_data}"},
                        },
                    ],
                },
            ],
            max_tokens=2000,
        )

        return response.choices[0].message.content

    except Exception as e:
        raise Exception(f"Error generating Bicep code: {str(e)}")


def validate_bicep(bicep_code):
    """
    Validate the generated Bicep code using Azure CLI.

    Args:
        bicep_code: Bicep code as string

    Returns:
        Tuple of (is_valid, validation_message)
    """
    try:
        # Create temporary file with the Bicep code
        with tempfile.NamedTemporaryFile(suffix=".bicep", delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(bicep_code.encode("utf-8"))

        # Run validation using Azure CLI
        result = subprocess.run(
            ["az", "bicep", "build", "--file", temp_path],
            capture_output=True,
            text=True,
        )

        # Check if validation was successful
        if result.returncode == 0:
            return True, "Bicep code is valid."
        else:
            return False, f"Validation failed: {result.stderr}"

    except Exception as e:
        return False, f"Validation error: {str(e)}"
    finally:
        # Clean up temporary file
        if "temp_path" in locals():
            os.unlink(temp_path)


if __name__ == "__main__":
    try:
        # Configure paths
        root_data_dir_path = os.path.join(os.path.dirname(__file__), "data")
        image_path = os.path.join(root_data_dir_path, "openai-end-to-end-basic.png")
        bicep_path = os.path.join(root_data_dir_path, "output.bicep")

        bicep_code = diagram_to_bicep(image_path)
        # Clean up the Bicep code
        cleand_bicep_code = bicep_code.replace("```bicep", "").replace("```", "")
        print(cleand_bicep_code)

        # Validate the generated code
        is_valid, validation_message = validate_bicep(cleand_bicep_code)
        print(f"\nValidation result: {validation_message}")

        # Optionally save to file
        with open(bicep_path, "w", encoding="utf-8") as f:
            f.write(bicep_code)

        if not is_valid:
            print("Warning: The generated Bicep code may have issues.")
    except Exception as e:
        print(f"Error: {e}")
