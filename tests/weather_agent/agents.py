import json

import bs4
from langchain import hub
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from swarm import Agent


def get_weather(location, time="now"):
    """Get the current weather in a given location. Location MUST be a city."""
    return json.dumps({"location": location, "temperature": "65", "time": time})


# def get_weather_from_llm(location, time="now"):


#     llm = ChatOpenAI(model="gpt-3.5-turbo-0125")

#     # Load, chunk and index the contents of the blog.
#     loader = WebBaseLoader(
#         web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
#         bs_kwargs=dict(
#             parse_only=bs4.SoupStrainer(
#                 class_=("post-content", "post-title", "post-header")
#             )
#         ),
#     )
#     docs = loader.load()

#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#     splits = text_splitter.split_documents(docs)
#     vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())

#     # Retrieve and generate using the relevant snippets of the blog.
#     retriever = vectorstore.as_retriever()
#     prompt = hub.pull("rlm/rag-prompt")

#     def format_docs(docs):
#         return "\n\n".join(doc.page_content for doc in docs)


#     rag_chain = (
#         {"context": retriever | format_docs, "question": RunnablePassthrough()}
#         | prompt
#         | llm
#         | StrOutputParser()
#     )

#     result =  rag_chain.invoke(f"What is weather in {location}?")

#     print(result)

def send_email(recipient, subject, body):
    print("Sending email...")
    print(f"To: {recipient}")
    print(f"Subject: {subject}")
    print(f"Body: {body}")
    return "Sent!"


weather_agent = Agent(
    name="Weather Agent",
    instructions="You are a helpful agent.",
    functions=[get_weather, send_email],
)
