from SimplerLLM.langauge.llm import LLM, LLMProvider
from SimplerLLM.langauge.llm_addons import (
    generate_basic_pydantic_json_model as gen_json,
)
import base64

from SimplerLLM.image import stability_ai, img_helper_funcs

from pydantic import BaseModel
import helpers
from mongo import record_word_to_db


class WordExplanation(BaseModel):
    basic_meaning: str
    longer_meaning: str
    sentence: str


def is_word_safe_for_children(word):
    return True


# Reading words from the file
with open("splits/test.txt", "r") as file:
    words = file.read().splitlines()

for input_word in words:

    print("Generating explanation for:", input_word)

    if not is_word_safe_for_children(input_word):
        continue  # Skip words that are not safe for children

    prompt = """
    I am creating a simple free online dictiorary targeting kid (6-8) years old, and english learners.

    Act as an expert in explainig words in a very basic and simple way that even a 6 years old child can unerstand.

    I will give you an [INPUT_WORD] and your task is to generate the following:
    1. basic meaning (2-5) words max
    2. longer meaning if the user wants more details (10-20) words max
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

    print("Generating Images for:", input_word)

    Image_prompt_cartoon = f"photo of a {input_word}, , cartoon style"
    Image_prompt_3d = f"photo of a {input_word}, 3d pixar style"
    Image_prompt_real = (
        f"photo that represents the following sentence: {sentence}, real style"
    )

    image1 = stability_ai.generate_images(
        model_name="stable-diffusion-v1-6", prompt=Image_prompt_cartoon
    )
    image2 = stability_ai.generate_images(
        model_name="stable-diffusion-v1-6", prompt=Image_prompt_3d
    )
    image3 = stability_ai.generate_images(
        model_name="stable-diffusion-v1-6", prompt=Image_prompt_real
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

    # save datetime 0
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
