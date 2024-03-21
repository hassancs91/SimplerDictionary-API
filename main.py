from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware

from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
auth_key = os.getenv("AUTH_KEY")

from mongo import establish_connection, mongo_db_instance, get_database

# implement NSFW Filter, word not suitable for children, skip
# implement caching
# implement auto correction for words
# add not found in the UI with funny image
# add detailed meaning collapsable in the frontend


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
        # record_log(ex,get_calling_module_name(),get_calling_function_name(), LogLevel.ERROR)


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


@app.post("/lookup", response_model=DictionaryResponse)
async def lookup_word(word: str, api_key: str = Header(None)):
    if api_key != auth_key:
        raise HTTPException(status_code=401, detail="Invalid authentication key")

    db = await get_database("simpler_dic")
    cache_collection = db["words_collection"]

    result = await cache_collection.find_one({"word": word})

    if not result:
        raise HTTPException(status_code=404, detail="Word not found")

    return DictionaryResponse(
        user_input=word,
        corrected_word=word,  # Assuming you handle word correction elsewhere if needed
        simple_meaning=result["basic_meaning"],
        detailed_meaning=result["detailed_meaning"],
        sentence=result["sentence"],
        images=result["picture_urls"],
    )
