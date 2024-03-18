from SimplerLLM.langauge.llm import LLM, LLMProvider
from SimplerLLM.langauge.llm_addons import generate_basic_pydantic_json_model as gen_json

from pydantic import BaseModel

class WordExplanation(BaseModel):
    basic_meaning: str
    longer_meaning: str
    sentence: str

input_word = "mountain"


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

json_response = gen_json(model_class=WordExplanation,prompt=input_prompt, llm_instance=llm_instance)
                                
basic_meaining = json_response.basic_meaning
longer_meaning  = json_response.longer_meaning
sentence = json_response.sentence


Image_prompt_cartoon = f"photo of a {input_word}, suitable for a children's dictionary, cartoon style"
Image_prompt_3d = f"photo of a {input_word}, suitable for a children's dictionary, 3d pixar style"
Image_prompt_real = f"photo of a {input_word}, suitable for a children's dictionary, real style"



print(sentence)