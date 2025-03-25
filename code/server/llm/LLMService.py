from dotenv import load_dotenv
import os
from google import genai
from . import DataStore

class LLMService:

    def __init__(self):
        load_dotenv()  

        # API Keys 
        self.google_api_key = os.getenv("GEMINI_API_KEY")

    def _call_gemini(self, email_content):
        """Calls Google's Gemini API"""
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY is missing.")
        
        client = genai.Client(api_key=self.google_api_key)

        generation_config=genai.types.GenerateContentConfig(
        system_instruction=self.get_system_instruction(),
        candidate_count=1, # Number of response versions to return
        stop_sequences=['x'],
        max_output_tokens=500,
        temperature=0)



        response = client.models.generate_content(model="gemini-2.0-flash", contents=email_content,config=generation_config)
        return response.text
    
    def get_system_instruction(self):
        role= DataStore.ROLE
        loan_servicing_requests=DataStore.REQUEST_TYPES
        context_info=""
        for request_type, details in loan_servicing_requests.items():
           context_info += f"Request Type: {request_type}\n"
           context_info += f"Description: {details['description']}\n"
    
           if "sub_requests" in details:
            context_info += "Sub Requests:\n"
            for sub_request, sub_description in details["sub_requests"].items():
                context_info += f"- {sub_request}: {sub_description}\n"
    
        context_info += "\n"
        return role+ "\n\n"+context_info

model = LLMService()
# print(llm._call_gemini("This is a empty email"))
# print(llm.get_system_instruction())







