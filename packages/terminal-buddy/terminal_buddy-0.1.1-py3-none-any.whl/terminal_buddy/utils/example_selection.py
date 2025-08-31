from langchain_community.vectorstores import Chroma
from langchain_core.example_selectors import (
    MaxMarginalRelevanceExampleSelector,
    SemanticSimilarityExampleSelector,
)
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_ollama import OllamaEmbeddings
from terminal_buddy.utils.config import config
import json



def _get_chroma_vectorstore():
    return Chroma



def _prepare_resources_for_example_selection():
    embeddings = OllamaEmbeddings(model=config.OLLAMA_EMBEDDINGS_MODEL_NAME)
    vector_store = _get_chroma_vectorstore()
    return embeddings, vector_store


def get_example_selector_template():
    

    example_prompt = PromptTemplate(
        input_variables=["user_query", "command"],
        template="User Query: {user_query}\nCommand: {command}",
    )

    # Examples of a pretend task of creating antonyms.
    with open(config.get_examples_path(),'r') as f:
        examples = json.load(f)
        # print(f"Loaded {len(examples)} Examples.")
        # print(f"Found keys: {examples[0].keys()}")
    embeddings, vector_store = _prepare_resources_for_example_selection()
    
    example_selector = SemanticSimilarityExampleSelector.from_examples(
        # The list of examples available to select from.
        examples,
        # The embedding class used to produce embeddings which are used to measure semantic similarity.
        embeddings,
        # The VectorStore class that is used to store the embeddings and do a similarity search over.
        vector_store,
        # The number of examples to produce.
        k=2
    )
    mmr_prompt = FewShotPromptTemplate(
        # We provide an ExampleSelector instead of examples.
        example_selector=example_selector,
        example_prompt=example_prompt,
        # prefix="For the given user request, generate a safe, relevant bash command:",
        suffix="User Query: {user_query}\nCommand: ",
        input_variables=["user_query"],
    )
    return mmr_prompt

mmr_prompt_template = get_example_selector_template()