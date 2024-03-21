from dotenv import load_dotenv
import os


load_dotenv()  # Load environment variables from .env file


MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")


from pymongo import MongoClient


def record_word_to_db(
    input_word,
    basic_meaning,
    detailed_meaning,
    sentence,
    picture_url_1,
    picture_url_2,
    picture_url_3,
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
        "word": input_word,
        "basic_meaning": basic_meaning,
        "detailed_meaning": detailed_meaning,
        "sentence": sentence,
        "picture_urls": [picture_url_1, picture_url_2, picture_url_3],
    }

    # Insert the document into the collection
    collection.insert_one(word_document)

    # Close the connection
    client.close()
