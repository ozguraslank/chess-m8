import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

LLM_API_KEY = os.getenv('LLM_API_KEY')

def send_request_to_gemini(prompt: str, model_name: str):
    """
    Sends API request to Gemini-1.5-pro model and returns the response

    Parameters
    ----------
    prompt: str
        The prompt to send to the model

    model_name: str
        The name of the model to send the request to (e.g. "gemini-1.5-pro")
        
    Returns
    -------
    response: json
        The json response from the model
    """
    try:
        genai.configure(api_key=LLM_API_KEY)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt, generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            max_output_tokens=50000,
            temperature=0.1
            ))
        ai_result = None

        # Sometimes LLM API returns different formats of JSON, so let's try to scenarios
        try:
            ai_result = json.loads(response.text)
        except:
            try:
                ai_result = eval(response.text)
            except:
                pass # If it fails, it will return None
        
        return ai_result
    
    except Exception as e:
        print(f"An error occured while sending request to Gemini API: {e}")