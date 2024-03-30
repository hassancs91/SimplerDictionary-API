from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv
from pymongo import DESCENDING
from spellchecker import SpellChecker


load_dotenv()  # Load environment variables from .env file
auth_key = os.getenv("AUTH_KEY")

from mongo import establish_connection, mongo_db_instance, get_database


app = FastAPI()

# Add CORSMiddleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.on_event("startup")
async def startup():
    try:
        await establish_connection()
    except Exception as ex:
        pass


@app.on_event("shutdown")
async def shutdown():

    try:
        await mongo_db_instance.close()
    except Exception as e:
        pass


class DictionaryResponse(BaseModel):
    user_input: str
    corrected_word: str
    simple_meaning: str
    detailed_meaning: str
    sentence: str
    images: List[str]


@app.get("/health")
async def health_check():
    return {"status": "Healthy"}


@app.post("/report-missing-word/")
async def append_to_file(word: str):
    try:
        with open("missing_words.txt", "a", encoding="utf-8") as file:
            file.write(word.lower() + "\n")
        return {"message": "Word Added", "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/lookup", response_model=DictionaryResponse)
async def lookup_word(word: str, api_key: str = Header(None)):
    if api_key != auth_key:
        raise HTTPException(status_code=401, detail="Invalid authentication key")

    db = await get_database("simpler_dic")
    cache_collection = db["words_collection"]

    # Convert word to lowercase
    original_word = word.lower()

    # Check if the word exists
    result = await cache_collection.find_one(
        {"word": original_word}, sort=[("recorded_date", DESCENDING)]
    )

    # If the word is not found, try auto-correcting it
    if not result:
        spell = SpellChecker()
        corrected_word = spell.correction(original_word)

        # If the corrected word is different, search for it
        if corrected_word != original_word:
            result = await cache_collection.find_one(
                {"word": corrected_word}, sort=[("recorded_date", DESCENDING)]
            )

            if not result:
                raise HTTPException(status_code=404, detail="Word not found")

            return DictionaryResponse(
                user_input=original_word,
                corrected_word=corrected_word,
                simple_meaning=result["basic_meaning"],
                detailed_meaning=result["detailed_meaning"],
                sentence=result["sentence"],
                images=result["picture_urls"],
            )
        else:
            raise HTTPException(status_code=404, detail="Word not found")

    return DictionaryResponse(
        user_input=original_word,
        corrected_word=original_word,
        simple_meaning=result["basic_meaning"],
        detailed_meaning=result["detailed_meaning"],
        sentence=result["sentence"],
        images=result["picture_urls"],
    )
