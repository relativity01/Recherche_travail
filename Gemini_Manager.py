import time
import genai
from ratelimit import sleep_and_retry
from ratelimit import limits
from google import genai
from google.genai import types

class GeminiManager:
    def __init__(self, api_key):
        if not api_key:
            print("⚠️ Warning: No Gemini API key provided. Check your os.getenv configuration.")
            
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemma-4-31b-it" #'gemma-3-27b-it'

    # We can keep this, but drop it to 10 to be safer on the free tier
    @sleep_and_retry
    @limits(calls=10, period=60)
    def analyze_description(self, description):
        """Asks Gemini to analyze the job description based on your criteria."""
        prompt = f"""
        Tu es un assistant qui permet de trier à ma place les offres d'emplois. A chaque offre d'emploi tu dois méticuleusement vérifier que l'offre correspond à mes critères de sélection. 
        Si c'est le cas tu écris "accepté", sinon "refusé". Attention, tu n'écris rien d'autre.

        Mes critères de sélection sont : 
        Je veux un poste d'ingénieur simulation, la spécificité scientifique ne m'intéresse pas, que ce soit thermique, électromagnétique, mécanique, vibration des ondes ou autres. 
        De même si je préfère que ce soit lié à du code (notamment python et c++), l'utilisation de logiciel (comme athéna, civa, abaqus, catia) me convient aussi. 
        Tout ce qui est lié au paramétrage/base de données/analyse d'image me convient aussi si elle est liée directement à du code.
        Je refuse catégoriquement la défense active (construction ou guidage de missile par exemple) mais accepte la défense passive (détection ovni).
        Je refuse aussi les alternances, les stages, les CDD mais accepte les CDI et thèses.
        
        Description de l'offre d'emploi :
        {description}
        """
        
        config = types.GenerateContentConfig(
            response_mime_type="text/plain",
            temperature=0.0
        )

        max_retries = 10
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config
                )
                print(f"Gemini response: {response.text.strip()}")
                return "accepté" in response.text.lower()
                
            except Exception as e:
                error_msg = str(e)
                print(f"✗ Gemini API error on attempt {attempt + 1}/{max_retries}: {error_msg}")
                
                is_retryable = any(code in error_msg for code in ["429", "500", "503", "RESOURCE_EXHAUSTED", "UNAVAILABLE"])
                
                if is_retryable and attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 20
                    print(f"⏳ Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"✗ Non-retryable error or max retries reached.")
                    return None
                        
        print("✗ Max retries reached for this description.")
        return None