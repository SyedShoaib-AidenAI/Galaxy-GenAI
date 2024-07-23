from langchain_openai import ChatOpenAI
import os
import bs4
from langchain import hub

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import FileResponse
import os 
import json
from fastapi.middleware.cors import CORSMiddleware
import os
from langchain_community.document_loaders import UnstructuredPowerPointLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import CSVLoader, PyPDFLoader
from dotenv import load_dotenv
from starlette.requests import Request
load_dotenv()
cwd = os.getcwd()

app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

class SaveContext:
    def __init__(self, fileName=""):
        self.fileName = fileName


state = SaveContext()
CHROMA_PATH = os.path.join(cwd, "chromaDB")
FILE_DIR =  os.path.join(cwd, "fileDirectory")
@app.post("/ask")
async def upload_file_n_ask(file: UploadFile = File(...)):
    state.fileName = file.filename
    persist_dir_path = os.path.join(CHROMA_PATH, state.fileName.split("/")[-1].split(".")[0])

    file_location = os.path.join(FILE_DIR, file.filename)
    try:
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())
    except IOError as e:
        print(f"Error saving file: {e}")

    vectorstore = []
    print(persist_dir_path)
    print(os.path.exists(persist_dir_path))
    if os.path.exists(persist_dir_path):
        from langchain_chroma import Chroma
        vectorstore = Chroma(persist_directory=persist_dir_path, embedding_function=OpenAIEmbeddings())
        print("Existing vector store loaded")
    else:
        from langchain.vectorstores.chroma import Chroma
        csv_docs = []
        pdf_docs = []
        ppt_docs = []
        word_docs = []
        file_path = os.path.join(os.path.join(FILE_DIR), state.fileName)
        if state.fileName.endswith(".csv"):
            loader = CSVLoader(file_path)
            csv_docs.extend(loader.load())
        if state.fileName.endswith(".pdf"):
            loader = PyPDFLoader(file_path)# Assume PDFLoader exists
            pdf_docs.extend(loader.load())  
        elif state.fileName.endswith(".pptx"):
            loader = UnstructuredPowerPointLoader(file_path)
            ppt_docs.extend(loader.load())
        elif state.fileName.endswith(".docx"):
            loader = Docx2txtLoader(file_path)
            word_docs.extend(loader.load())
        elif state.fileName.endswith(".txt"):
            loader = TextLoader(file_path)
            word_docs.extend(loader.load())
        doc = csv_docs + pdf_docs + word_docs + ppt_docs
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=400)
        splits = text_splitter.split_documents(doc)
        vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings(), persist_directory=persist_dir_path)
        vectorstore.persist()
        print("New vector store created")
    return {"Status": "Success", "Response": [f"file '{file.filename}' saved at '{file_location}'"]}

"""
{
  "Question": [
    "What is AI?",
    "How does FastAPI work?"
  ]
}
"""



@app.get("/custom-ask")
# async def process_json(fileName = state.fileName):
async def process_json(request: Request, fileName = state.fileName):
    request_json = await request.json()
    print(request_json)
    questions = request_json.get("Question", [])
    print(questions)
    print(fileName)
    persist_dir_path = os.path.join(CHROMA_PATH, fileName.split("/")[-1].split(".")[0])
    print("persist dir: ", persist_dir_path)
    print(os.path.exists(persist_dir_path))
    vectorstore = []
    llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"),model="gpt-4o")
    if os.path.exists(persist_dir_path):
        from langchain_chroma import Chroma
        vectorstore = Chroma(persist_directory=persist_dir_path, embedding_function=OpenAIEmbeddings())
        print("Existing vector store loaded")
    else:
        return {"Status": "Failed", "Response": ["The file doesn't exist"]}
    retriever = vectorstore.as_retriever()
    prompt = hub.pull("rlm/rag-prompt")
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    responses = []
    print(questions)
    for question in questions:
       responses.append(rag_chain.invoke(question))
    return {"Status": "Success", "Response": responses}

"""
{
  "Question": [
    "What is AI?",
    "How does FastAPI work?"
  ]
}
"""

if __name__ == "__main__":
    import uvicorn
    os.makedirs(FILE_DIR)
    os.makedirs(CHROMA_PATH)
    uvicorn.run(app, host="0.0.0.0", port=7000)
    # allow_origin