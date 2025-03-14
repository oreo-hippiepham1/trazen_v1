from calendar import c
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from langchain_core.prompts.chat import ChatPromptTemplate

from langchain_pinecone import PineconeVectorStore

from regex import D, P
from typing_extensions import TypedDict, List

from pydantic import BaseModel, Field

from langchain_core.output_parsers import JsonOutputParser


class State(TypedDict):
    """
    State for the quiz agent.
    """
    keyword: str # keyword to retrieve for context
    context: List[Document] # context
    answer: str # answer (which is a quiz) by the agent
    answer_src: list # source of the answer

class Quiz(BaseModel):
    """
    Quiz model.
    """
    question: str = Field(description="Quiz question")
    distractors: List[str] = Field(description="List of 3 incorrect answers", min_length=3, max_length=3)
    correct_answer: str = Field(description="Correct answer")
    explanation: str = Field(description="Explanation for the answer")

def get_quiz_agent(llm: ChatOpenAI, vector_store: PineconeVectorStore):
    """
    Get the quiz agent.
    """
    prompt_template = '''
    Given the following context, generate exactly 1 quiz based on the context.

    The quizzes should be in a multiple-choice format, with 4 options each,
        avoid answers like "all of the above" or "none of the above".
    The quizzes should be relevant to the content and context of the text,
        and should be in a question-answer format.
    The wrong answers should not be too obvious or easy to guess, and should attempt to
        mislead the user.

    The output should be in a JSON format, like the following example:
    {{
        "question": "Which sea animal is known for having eight arms?",
        "distractors": ["Squid", "Jellyfish", "Starfish"],
        "correct_answer": "Octopus",
        "explanation": "Octopuses are marine animals with eight arms, which they use for locomotion and capturing prey."
    }}

    Do not include any text before or after the JSON.
    Context: {context}
    '''

    prompt_template_pydantic = '''
    Given the following context, generate exactly 1 quiz based on the context.

    The quizzes should be in a multiple-choice format, with 4 options each, of which 3 are distractors (wrong answer),
        and 1 is the correct answer. Avoid answers like "all of the above" or "none of the above".
    The quizzes should be relevant to the content and context of the text.
    The wrong answers should not be too obvious or easy to guess, and should attempt to
        mislead the user.
    Make sure there is an explanation for the answer.
    Do not use phrases like "According to the context, ..." or similar.

    The output should be in a JSON format, like the following example:
    {{
        "question": "Which sea animal is known for having eight arms?",
        "distractors": ["Squid", "Jellyfish", "Starfish"],
        "correct_answer": "Octopus",
        "explanation": "Octopuses are marine animals with eight arms, which they use for locomotion and capturing prey."
    }}
    Do not include any text before or after the JSON.

    Context: {context}
    '''
    # Create the prompt
    parser = JsonOutputParser(pydantic_object=Quiz)
    prompt_pydantic = ChatPromptTemplate.from_template(prompt_template_pydantic).partial(
        format_instructions=parser.get_format_instructions() # not exactly sure if this is needed
    )

    def _retrieve(state: State):
        retrieved_docs = vector_store.similarity_search(state['keyword'], k=3)

        return {
            "context": retrieved_docs,
            "keyword": state['keyword']
        }

    def _generate(state: State):
        docs_content = "\n\n".join([doc.page_content for doc in state['context']])
        docs_source = {
            'source': [doc.metadata for doc in state['context']],
            'content': [doc.page_content for doc in state['context']]
        }

        # messages = prompt.invoke({'context': docs_content, {'question'}})
        messages = prompt_pydantic.format_messages(context=docs_content)

        response = llm.invoke(messages)

        return {
            'answer': response.content,
            'answer_src': docs_source,
            'keyword': state["keyword"],  # Ensure keyword is passed along
            'context': state["context"]  # Ensure context is passed along
        }

    # Create the state graph]
    builder = StateGraph(State).add_sequence([_retrieve, _generate])
    builder.add_edge(START, '_retrieve')
    graph = builder.compile()

    return graph