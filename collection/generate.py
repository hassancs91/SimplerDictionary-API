from SimplerLLM.langauge.llm import LLM, LLMProvider
from SimplerLLM.langauge.llm_addons import (
    generate_basic_pydantic_json_model as gen_json,
)
import base64

from SimplerLLM.image import stability_ai, img_helper_funcs

from pydantic import BaseModel
import helpers
from mongo import record_word_to_db


# Place the LLM instance creation here to reuse it.
llm_instance = LLM.create(provider=LLMProvider.OPENAI, model_name="gpt-4")


class WordExplanation(BaseModel):
    basic_meaning: str
    longer_meaning: str
    sentence: str


class WordFilter(BaseModel):
    safe: bool
    needed: bool


class WordCategory(BaseModel):
    Category: str


class GeneratedPrompt(BaseModel):
    Prompt: str


def write_to_file(filename, content):
    try:
        with open(filename, "a", encoding="utf-8") as file:
            file.write(content + "\n")
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")


def is_safe_and_needed(word):
    print("check if word is safe and needed...")
    prompt = """
    I am creating a simple free online dictiorary targeting kid (6-8) years old, and new english learners.

    Act as an expert in in english vocabulary. 

    I will give you an [INPUT_WORD] and your task is to check the following:
    1. Is the word safe to use in a dictionary for kids?
    2. Is the word needed in the dictionary?

    [INPUT_WORD] = {input_word}.
    

    """
    input_prompt = prompt.format(input_word=word)

    json_response = gen_json(
        model_class=WordFilter, prompt=input_prompt, llm_instance=llm_instance
    )

    print(f"Safe: {json_response.safe}, Needed: {json_response.needed}")

    return json_response


def prompt_generator(input_word: str, style: str):
    prompt = f""" 
                Act as a Stable Diffusion Art Prompt Generator specialized in generating images for dictionaries and suitable for kids.

                The formula for a prompt is made of parts as follows:
                1. The [Subject] is the person place, thing, or idea the image is focused on. 

                2. The [Emotions] is the emotional look the subject or scene might have. 

                3. The [Verb] is What the subject is doing, such as standing, jumping, working and other varied that match the subject. 

                4. The [Adjectives] like beautiful, rendered, realistic, tiny, colorful and other varied that match the subject. 

                5. The [Environment] in which the subject is in.

                6. The [Lighting] of the scene like moody, ambient, sunny, foggy and others that match the Environment and compliment the subject. 
                
                7. The [Quality] like HD, 4K, 8K, 64K UHD, SDR and other. if not specfied, always use 4K.
                
                8. The [Style] like 3d Pixar animation, 2d cartoon, realistic, cinematic, Anime, Photographic, digital painting, Watercolor Painting, Comic book, Neon Punk, low poly, isometric, origami, craft clay, 3d model, pixel art

                The subject and environment should match and have the most emphasis.

                I will give you a [Subject], you will respond with a full prompt. Present the result as one full sentence, no line breaks, no delimiters, and keep it as concise as possible while still conveying a full scene.

                Here is a sample of how it should be output: 

                "A group of joyful children, exuberant and smiling, playing tag in a sunny meadow, brightly colored clothes, vibrant summer environment with flowers and butterflies, radiant natural sunlight, 4K quality, 3d pixar animation style "

                [Subject]: {input_word}.
                [Style]: {style}.
                    """
    generated_prompt = llm_instance.generate_text(prompt)

    return generated_prompt


words = [
    "dog",
    "apple",
    "banana",
    "orange",
    "grape",
    "pear",
    "strawberry",
    "watermelon",
    "happiness",
]


for input_word in words:
    try:
        print("Processing Word: ", input_word)

        # skip words with 's
        if "'s" in input_word:
            write_to_file("skipped.txt", input_word.lower() + "-Contains 's'")
            continue

        # skip word if it contains a number
        if any(char.isdigit() for char in input_word):
            write_to_file("skipped.txt", input_word.lower() + "-Contain Digits")
            continue

        # replace _ with space
        input_word = input_word.replace("_", " ")

        safe_and_needed = is_safe_and_needed(input_word)

        if (not safe_and_needed.needed) or (not safe_and_needed.safe):
            write_to_file("skipped.txt", input_word.lower() + "-NOT NEEDED OR SAFE")
            continue

        print("Generating explanation...")

        prompt = """
        I am creating a simple free online dictiorary targeting kid (6-8) years old, and english learners.

        Act as an expert in explainig words in a very basic and simple way that even a 6 years old child can unerstand.

        I will give you an [INPUT_WORD] and your task is to generate the following:
        1. basic meaning (2-5) words max
        2. longer meaning (20 words max) if the user wants more details with other meanings for the word if exists.
        3. a simple sentence that contains the exact [INPUT_WORD] to help the user put in a context.

        [INPUT_WORD] = {input_word}

        """
        input_prompt = prompt.format(input_word=input_word)

        llm_instance = LLM.create(provider=LLMProvider.OPENAI, model_name="gpt-4")

        json_response = gen_json(
            model_class=WordExplanation, prompt=input_prompt, llm_instance=llm_instance
        )

        basic_meaining = json_response.basic_meaning
        longer_meaning = json_response.longer_meaning
        sentence = json_response.sentence

        # get word category

        # generate prompt based on category
        Image_prompt_3d = prompt_generator(input_word, "3d Pixar animation").strip('"')
        Image_prompt_colored = prompt_generator(
            input_word, "Watercolor Painting"
        ).strip('"')
        Image_prompt_clay = prompt_generator(input_word, "craft clay").strip('"')

        image1 = stability_ai.generate_images(
            model_name="stable-diffusion-v1-6", prompt=Image_prompt_clay
        )
        image2 = stability_ai.generate_images(
            model_name="stable-diffusion-v1-6", prompt=Image_prompt_3d
        )
        image3 = stability_ai.generate_images(
            model_name="stable-diffusion-v1-6", prompt=Image_prompt_colored
        )

        image_bytes1 = base64.b64decode(image1.images[0].base64_str)
        img_url1 = helpers.save_image_file_to_cloud(
            input_word, image_bytes1, "generated-images"
        )

        image_bytes2 = base64.b64decode(image2.images[0].base64_str)
        img_url2 = helpers.save_image_file_to_cloud(
            input_word, image_bytes2, "generated-images"
        )

        image_bytes3 = base64.b64decode(image3.images[0].base64_str)
        img_url3 = helpers.save_image_file_to_cloud(
            input_word, image_bytes3, "generated-images"
        )

        # save to mongo
        record_word_to_db(
            input_word,
            basic_meaining,
            longer_meaning,
            sentence,
            img_url1,
            img_url2,
            img_url3,
        )
        print("done")
    except Exception as e:
        # add to retry later text file
        write_to_file("retry.txt", input_word.lower())
