from typing_extensions import TypedDict, Any
from typing import Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

from ..key_manager import KeyManager


# Class for Input/Output files
class FILES(TypedDict):
    Folder: str           #project folder
    data_description: str #name of the file with the data description
    LLM_calls: str        #name of the file with the calls to the LLM
    Temp: str             #name of the folder with the temporary LaTeX files
    idea: str             #name of the file to write the final idea
    methods: str          #name of the file to write the methods
    idea_log: str         #name of the file to write generated ideas and critics
    Error: str            #name of the error file
    module_folder: str    #name of the folder containing the results from the considered module
    f_stream: str         #name of the file to stream the results

# Token class
class TOKENS(TypedDict):
    ti: int #total input tokens
    to: int #total output tokens 
    i:  int #input tokens (just for individual calls or functions)
    o:  int #output tokens (just for individual calls or functions)

# LLM class
class LLM(TypedDict):
    model: str
    max_output_tokens: int
    llm: Any
    temperature: float
    stream_verbose: bool

# Idea class
class IDEA(TypedDict):
    iteration: int
    previous_ideas: str
    idea: str
    criticism: str
    total_iterations: int

# Graph state class
class GraphState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    idea: IDEA
    tokens: TOKENS
    llm: LLM
    files: FILES
    keys: KeyManager
    data_description: str
    task: str
