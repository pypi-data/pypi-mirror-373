import os
from typing import Dict, Any
import openai
import requests
import tempfile
import os
from urllib.parse import urlparse
from media_agent_mcp.storage.tos_client import upload_to_tos


def openaiedit(image_url: str, prompt: str, size: str = "1024x1024") -> Dict[str, Any]:
    """
    Perform image editing using the OpenAI Images API.

    :param image_url: URL of the input image.
    :param prompt: The editing prompt.
    :param size: The size of the generated images. Must be one of "256x256", "512x512", or "1024x1024".
    :return: JSON response with status, data (image URL), and message.
    """
    try:
        client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )

        # Download the image
        response = requests.get(image_url)
        response.raise_for_status()

        # Save image to a temporary file
        parsed_url = urlparse(image_url)
        file_ext = os.path.splitext(parsed_url.path)[1]
        if not file_ext:
            # Fallback if extension is not in URL path
            content_type = response.headers.get('content-type')
            if content_type and 'image' in content_type:
                file_ext = '.' + content_type.split('/')[1]
            else:
                file_ext = '.png' # default

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
        try:
            temp_file.write(response.content)
            temp_file.close()

            # Call OpenAI API with the local file
            with open(temp_file.name, "rb") as f:
                response = client.images.edit(
                    model="gpt-image-1",
                    image=f,
                    prompt=prompt,
                    n=1,
                    size=size
                )
        finally:
            os.unlink(temp_file.name) # Clean up the temporary file

        image_url = response.data[0].url

        # Download the edited image
        edited_image_response = requests.get(image_url)
        edited_image_response.raise_for_status()

        # Save the edited image to a temporary file
        parsed_url = urlparse(image_url)
        file_ext = os.path.splitext(parsed_url.path)[1] or '.png'

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_edited_file:
            temp_edited_file.write(edited_image_response.content)
            temp_edited_file_path = temp_edited_file.name

        try:
            # Upload the edited image to TOS
            tos_url = upload_to_tos(temp_edited_file_path)
        finally:
            os.unlink(temp_edited_file_path) # Clean up the temporary file

        return {
            "status": "success",
            "data": {"image_url": tos_url},
            "message": "Image edited and uploaded to TOS successfully."
        }
    except openai.APIError as e:
        return {
            "status": "error",
            "data": None,
            "message": f"OpenAI API Error: {e}"
        }
    except requests.RequestException as e:
        return {
            "status": "error",
            "data": None,
            "message": f"Error downloading image: {e}"
        }
    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "message": f"An unexpected error occurred: {e}"
        }

if __name__ == '__main__':
    # Make sure to set your OPENAI_API_KEY environment variable
    # For example: export OPENAI_API_KEY='your-api-key'
    image_url = 'https://carey.tos-ap-southeast-1.bytepluses.com/Art%20Portrait/Art%20Portrait/Art%20Portrait/Art%20Portrait%20(1).jpg'
    prompt = 'A cute baby sea otter cooking a meal'
    result = openaiedit(image_url, prompt)
    print(result)