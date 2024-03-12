from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

class DictionaryResponse(BaseModel):
    user_input: str
    corrected_word: str
    simple_meaning: str
    detailed_meaning: str
    sentence: str
    images: List[str]

@app.post("/lookup", response_model=DictionaryResponse)
async def lookup_word(word: str):
    # Here you would have logic to process the word, check for corrections, lookup meanings, sentences, and images
    # For the sake of example, I'm returning some dummy data

    # Dummy images URLs
    images = [
        "https://storage.freeaikit.com/ai-images/generated/st/2024/03/06b99eca-3658-4058-b246-eaf4bf0db92c.png",
        "https://storage.freeaikit.com/ai-images/generated/st/2024/03/a561fe73-5482-4371-9031-a9ce24563255.png",
        "https://storage.freeaikit.com/ai-images/generated/st/2024/03/7389158e-9837-471d-816a-892538ac3a95.png"
    ]

    return DictionaryResponse(
        user_input=word,
        corrected_word=word, 
        simple_meaning="water falling from clouds",
        detailed_meaning="Rain, a form of precipitation, consists of water droplets falling from clouds.",
        sentence="The sound of rain against the windows was soothing",
        images=images
    )

