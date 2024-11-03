import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

LLM_API_KEY = os.getenv('LLM_API_KEY')

def send_request_to_gemini(prompt: str):
    """
    Sends API request to Gemini-1.5-pro model and returns the response

    Parameters
    ----------
    prompt: str
        The prompt to send to the model

    Returns
    -------
    response: json
        The json response from the model
    """
    try:
        genai.configure(api_key=LLM_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt, generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            max_output_tokens=50000,
            temperature=0.1
            ))
        
        return response
    
    except Exception as e:
        print(f"An error occured while sending request to Gemini API: {e}")