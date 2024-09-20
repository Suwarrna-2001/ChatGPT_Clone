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
        You are a friendly and intelligent assistant here to help users with any questions they might have. Your goal is to provide clear, concise, and helpful responses.
        **INSTRUCTIONS:**
        1. Respond in a maximum of 50 words when possible.
        2. Answer only the questions related to the user's needs or data provided. If you don’t know the answer or if the information is not available, politely inform the user and suggest further help or support.
        3. Provide relevant information when users ask about their orders, such as tracking details, medications, or status updates, if the order details are available.
    """
}

def prepare_prompt_and_chain(session_id, behavior_config=None, include_realtime=False):
    os.environ["AZURE_OPENAI_API_KEY"] = AZURE_OPENAI_API_KEY
    os.environ["AZURE_OPENAI_ENDPOINT"] = AZURE_OPENAI_ENDPOINT
    llm = AzureChatOpenAI(azure_deployment="gpt4o", api_version="2024-02-15-preview")
    
    # Use default behavior config if no custom config is provided
    behavior_config = behavior_config or DEFAULT_BEHAVIOR_CONFIG

    # Dynamically decide whether to include realtime data in the user message
    if include_realtime:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", behavior_config['system_prompt']),
                MessagesPlaceholder(variable_name="history"),
                ("user", "{input}\n\n{realtime}"),  # Include realtime data
            ]
        )
    else:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", behavior_config['system_prompt']),
                MessagesPlaceholder(variable_name="history"),
                ("user", "{input}"),  # Exclude realtime data
            ]
        )

    with_message_history = RunnableWithMessageHistory(
    prompt | llm,  # Ensure prompt and llm are properly defined elsewhere in your code
    lambda session_id: PostgresChatMessageHistory(
        connection_string=CONNECTION_STRING,  # Quotation marks added
        session_id=session_id
    ),
    input_messages_key="input",  # Ensure this key matches the input field you're working with
    history_messages_key="history",  # Ensure this key matches the history field you're working with
    history_factory_config=[
        ConfigurableFieldSpec(
            id="session_id",
            annotation=str,
            name="Session ID",
            description="Unique identifier for the conversation.",
            default="",  # Ensure this fits your desired default behavior
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

    

def test_invoke(session_id, user_input, tone):

    os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
    retriever = TavilySearchAPIRetriever(k=2)
    
    real = ""  # Initialize real-time data as empty
    include_realtime = False  # Flag to include realtime data in prompt
    
    if tone == "real-time":
        real = retriever.invoke(user_input)##here I will have the long retrieved long data and I waill give it to llm
        include_realtime = True

    # Fetch behavior config for the session_id
    behavior_config = behavior_configs.get(tone, "DEFAULT_BEHAVIOR_CONFIG")

    if not isinstance(behavior_config, dict):
          behavior_config = DEFAULT_BEHAVIOR_CONFIG

    # Prepare the chain with dynamic behavior
    chain = prepare_prompt_and_chain(session_id, behavior_config, include_realtime)
    
    # Prepare input for the chain
    input_data = {"input": user_input}
    if include_realtime:
        input_data["realtime"] = real  # Include real-time data if needed
    
    # Invoke the chain with a test input
    result = chain.invoke(input_data, config={"configurable": {"session_id": session_id}})
    
    # Print the result
    print("Result:", result)


'''
if __name__ == "__main__":  
    # Testing with default behavior
    print("\nTesting with default behavior:")
    test_invoke("2", "What is the weather like?","default")

'''
