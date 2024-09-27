import os
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import (ConfigurableFieldSpec)
from langchain_community.vectorstores import PGEmbedding
from langchain_openai import OpenAIEmbeddings
from langchain_community.chat_message_histories import (
    PostgresChatMessageHistory,
)
from langchain_community.retrievers import TavilySearchAPIRetriever
from dotenv import load_dotenv
import pdb
load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
CONNECTION_STRING = os.getenv('CONNECTION_STRING')

behavior_configs = {
    "funny": {
        'system_prompt': """
            You are a humorous assistant. Please include a touch of humor in your responses.
        """
    },
    "formal": {
        'system_prompt': """
            You are a very formal assistant. Provide responses in a formal tone.
        """
    },
    "casual": {
        'system_prompt': """
            You are a casual and friendly assistant. Your responses should be informal and relaxed.
        """
    },
    "sports": {
        'system_prompt': """
            You are a sports enthusiast. Provide responses with enthusiasm and use sports-related terminology where appropriate.
        """
    },
    "science": {
        'system_prompt': """
            You are a knowledgeable science advisor. Provide detailed and accurate scientific information in your responses.
        """
    },
    "history": {
        'system_prompt': """
            You are a history expert. Provide detailed historical context and information in your responses.
        """
    },
    "technology": {
        'system_prompt': """
            You are a tech-savvy assistant. Provide responses with a focus on technology and use relevant technical terms where appropriate.
        """
    },
    "entertainment": {
        'system_prompt': """
            You are an entertainment expert. Your responses should be engaging and cover various aspects of entertainment, including movies, music, and more.
        """
    },
    "education": {
        'system_prompt': """
            You are an educational assistant. Provide informative and educational responses to support learning and understanding.
        """
    },
    "real-time": {
        'system_prompt': """you are an intelligent agent use the data you get effectivelu and get the very consised answer.
        """
    }
}




DEFAULT_BEHAVIOR_CONFIG = {
    'system_prompt': """
        You are a friendly and intgpt4o50 words when possible.
        2. Answer only the questions related to the user's needs or data provided. If you don’t know the answer or if the information is not available, politely inform the user and suggest further help or support.
        3. Provide relevant information when users ask about their orders, such as tracking details, medications, or status updates, if the order details are available.
    """
}

def prepare_prompt_and_chain(session_id, behavior_config=None, include_realtime=False):
    os.environ["AZURE_OPENAI_API_KEY"] = AZURE_OPENAI_API_KEY
    os.environ["AZURE_OPENAI_ENDPOINT"] = AZURE_OPENAI_ENDPOINT
    llm = AzureChatOpenAI(azure_deployment="gpt4o", api_version="2024-02-15-preview")
    
    
    behavior_config = behavior_config or DEFAULT_BEHAVIOR_CONFIG

    
    if include_realtime:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", behavior_config['system_prompt']),
                MessagesPlaceholder(variable_name="history"),
                ("user", "{input}\n\n{realtime}"),  
            ]
        )
    else:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", behavior_config['system_prompt']),
                MessagesPlaceholder(variable_name="history"),
                ("user", "{input}"),  
            ]
        )

    with_message_history = RunnableWithMessageHistory(
    prompt | llm,  
    lambda session_id: PostgresChatMessageHistory(
        connection_string=CONNECTION_STRING,  
        session_id=session_id
    ),
    input_messages_key="input",  
    history_messages_key="history",  
    history_factory_config=[
        ConfigurableFieldSpec(
            id="session_id",
            annotation=str,
            name="Session ID",
            description="Unique identifier for the conversation.",
            default="",  
            is_shared=True,
        ),
    ],
    verbose=True,
    )
    return with_message_history



def get_context(user_query, collection_name):
    openai_ef = OpenAIEmbeddings(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version="2024-02-15-preview"
    )
    store = PGEmbedding(
        connection_string=CONNECTION_STRING,
        embedding_function=openai_ef,
        collection_name=collection_name,
    )
    context = ""
    docs_with_score = store.similarity_search_with_score(user_query, k=3)
    for doc, score in docs_with_score:
        context += doc.page_content + " "
    return context

    

def test_invoke(session_id, user_input, tone, context):

    os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
    retriever = TavilySearchAPIRetriever(k=2)
    
    real = ""  
    include_realtime = False  
    
    if tone == "real-time":
        real = retriever.invoke(user_input)
        include_realtime = True

    behavior_config = behavior_configs.get(tone, "DEFAULT_BEHAVIOR_CONFIG")

    if not isinstance(behavior_config, dict):
          behavior_config = DEFAULT_BEHAVIOR_CONFIG

    chain = prepare_prompt_and_chain(session_id, behavior_config, include_realtime)
    
    input_data = {"input": user_input}
    if include_realtime:
        input_data["realtime"] = real  
    input_data["context"] = context
    
    result = chain.invoke(input_data, config={"configurable": {"session_id": session_id}})
    return result.content


