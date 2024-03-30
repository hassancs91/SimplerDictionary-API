from dotenv import load_dotenv
import os
from datetime import datetime


load_dotenv()  # Load environment variables from .env file


MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")


from pymongo import MongoClient


def record_word_to_db(
    input_word: str,
    basic_meaning: str,
    detailed_meaning: str,
    sentence: str,
    picture_url_1: str,
    picture_url_2: str,
    picture_url_3: str,
):

    client_uri = MONGO_CONNECTION_STRING

    # Connect to MongoDB Atlas
    client = MongoClient(client_uri)

    # Select your database
    db = client["simpler_dic"]

    # Select the collection
    collection = db["words_collection"]

    # Create the document to be inserted
    word_document = {
        "word": input_word.lower(),
        "basic_meaning": basic_meaning,
        "detailed_meaning": detailed_meaning,
        "sentence": sentence,
        "picture_urls": [picture_url_1, picture_url_2, picture_url_3],
        "recorded_date": datetime.now(),
    }

    # Insert the document into the collection
    collection.insert_one(word_document)

    # Close the connection
    client.close()
