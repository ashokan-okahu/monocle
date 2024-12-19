import os
import uuid
from operator import itemgetter

import bs4
from langchain import hub
from langchain.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from monocle_apptrace.instrumentation.common.instrumentor import (
    set_context_properties,
    setup_monocle_telemetry,
)

os.environ["USER_AGENT"]="langchain-python-app"

setup_monocle_telemetry(
            workflow_name="raanne_rag_ltom",
            span_processors=[BatchSpanProcessor(ConsoleSpanExporter())],
            wrapper_methods=[])

set_context_properties({"session_id": f"{uuid.uuid4().hex}"})


# Load, chunk and index the contents of the blog.
loader = WebBaseLoader(
    web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
    bs_kwargs=dict(
        parse_only=bs4.SoupStrainer(
            class_=("post-content", "post-title", "post-header")
        )
    ),
)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)
vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())

# Retrieve and generate using the relevant snippets of the blog.
retriever = vectorstore.as_retriever()
print(f"retriever tags:{retriever.tags}")


decompostion_prompt = ChatPromptTemplate.from_template(
    """
    You are a helpful assistant that can break down complex questions into simpler parts. \n
        Your goal is to decompose the given question into multiple sub-questions that can be answerd in isolation to answer the main question in the end. \n
        Provide these sub-questions separated by the newline character. \n
        Original question: {question}\n
        Output (3 queries): 
    """
)

query_generation_chain = (
    {"question": RunnablePassthrough()}
    | decompostion_prompt
    | ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0.7)
    | StrOutputParser()
    | (lambda x: x.split("\n"))
)

query = "What is Task Decomposition?"
questions = query_generation_chain.invoke(query) #What are the benefits of QLoRA


#print(questions)

# Create the final prompt template to answer the question with provided context and background Q&A pairs
template = """Here is the question you need to answer:

\n --- \n {question} \n --- \n

Here is any available background question + answer pairs:

\n --- \n {q_a_pairs} \n --- \n

Here is additional context relevant to the question: 

\n --- \n {context} \n --- \n

Use the above context and any background question + answer pairs to answer the question: \n {question}
"""

least_to_most_prompt = ChatPromptTemplate.from_template(template) 
llm = ChatOpenAI(model='gpt-4', temperature=0)

least_to_most_chain = (
        {'context': itemgetter('question') | retriever,
        'q_a_pairs': itemgetter('q_a_pairs'),
        'question': itemgetter('question'),
        }
        | least_to_most_prompt
        | llm
        | StrOutputParser()
    )

q_a_pairs = ""
for q in questions:
    
    answer = least_to_most_chain.invoke({"question": q, "q_a_pairs": q_a_pairs})
    q_a_pairs+=f"Question: {q}\n\nAnswer: {answer}\n\n"

#final RAG step
response = least_to_most_chain.invoke({"question": query, "q_a_pairs": q_a_pairs})

print("*************** OUTPUT ********************")
print("\n")
print(f"query: {query}")
print("\n")
print(f"response: {response}")
print("\n")
print(f"q_and_a:\n[{q_a_pairs}]")
print("*************** END ********************")
print(least_to_most_chain)