
import os
import json
from dotenv import load_dotenv
import requests

# Charger les variables d'environnement
load_dotenv()

AI_API_URL = os.getenv("AI_API_URL", "https://api.groq.com/openai/v1/chat/completions")
AI_API_KEY = os.getenv("AI_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "llama3-70b-8192")

def test_groq():
    print(f"--- TEST IA GROQ ---")
    print(f"Modèle: {AI_MODEL}")
    
    if not AI_API_KEY or "YOUR_GROQ" in AI_API_KEY:
        print("[!] ERREUR: Cle API non configuree dans le fichier .env")
        return

    text_test = "Facture #INV-2024-001 de l'entreprise TechSolutions SARL domiciliee a Paris. Montant Total: 1200 EUR dont 200 EUR de TVA (20%)."
    
    prompt = f"""
    Extraits les informations suivantes du texte de facture ci-dessous en JSON :
    - invoice_number
    - supplier
    - total_amount
    - vat_amount
    
    Texte: {text_test}
    """
    
    try:
        print("Envoi de la requete a Groq...")
        response = requests.post(
            AI_API_URL,
            headers={"Authorization": f"Bearer {AI_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": AI_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            },
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print("[+] SUCCES ! L'IA a repondu :")
            print(json.dumps(json.loads(content), indent=2, ensure_ascii=False))
        else:
            print(f"[!] ERREUR API: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"[!] ERREUR CRITIQUE: {str(e)}")

if __name__ == "__main__":
    test_groq()
