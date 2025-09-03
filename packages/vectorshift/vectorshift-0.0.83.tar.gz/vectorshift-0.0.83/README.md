# VectorShift SDK
Python SDK in development for VS pipeline creation and interaction

## Documentation

The VectorShift SDK provides a Python interface for creating, managing, and executing AI pipelines on the VectorShift platform.

For comprehensive API documentation, visit: [https://docs.vectorshift.ai/api-reference/overview](https://docs.vectorshift.ai/api-reference/overview)

## Installation

```
pip install vectorshift
```


## Usage

### Autnethication
Set api key in code
```python
vectorshift.api_key = 'sk-****'
```
or set as environement variable
```bash
export VECTORSHIFT_API_KEY='sk-***'
```


Create a new pipeline
```python
import vectorshift
from vectorshift.pipeline import Pipeline, InputNode, OutputNode, LlmNode
# Set API key
vectorshift.api_key = "your api key here"

input_node = InputNode(node_name="input_0")

llm_node = LlmNode(
    node_name="llm_node",
    system="You are a helpful assistant.",
    prompt=input_node.text,
    provider="openai",
    model="gpt-4o-mini",
    temperature=0.7
)

output_node = OutputNode(
    node_name="output_0",
    value=llm_node.response
)

pipeline = Pipeline.new(
    name="basic-llm-pipeline",
    nodes=[input_node, llm_node, output_node]
)
```

Basic Rag Pipeline

```python
import vectorshift
from vectorshift.pipeline import Pipeline, InputNode, KnowledgeBaseNode, OutputNode, LlmNode
from vectorshift import KnowledgeBase

# Set API key
vectorshift.api_key = "your api key here"

# Create input node for user query
input_node = InputNode(
    node_name="Query",
)

# Fetch knowledge base
knowledge_base = KnowledgeBase.fetch(name="your knowledge base name here")

# Create knowledge base node to retrieve relevant documents
knowledge_base_node = KnowledgeBaseNode(
    query=input_node.text,
    knowledge_base=knowledge_base,
    format_context_for_llm=True,
)

# Create LLM node that uses both the query and retrieved documents
llm_node = LlmNode(
    system="You are a helpful assistant that answers questions based on the provided context documents.",
    prompt=f"Query: {input_node.text}\n\nContext: {knowledge_base_node.formatted_text}",
    provider="openai",
    model="gpt-4o-mini",
    temperature=0.7
)

# Create output node for the LLM response
output_node = OutputNode(
    node_name="Response",
    value=llm_node.response
)

# Create the RAG pipeline
rag_pipeline = Pipeline.new(
    name="rag-pipeline",
    nodes=[input_node, knowledge_base_node, llm_node, output_node],
)
```


### Pipeline List Mode
Specify execution mode = `batch` to run a node in list mode. The node will now take in lists of inputs and execute it's task in parallel over the inputs. In this example the input will be split by newlines and the sub pipeline will execute over each part of the input in parallel.
```python
import vectorshift

from vectorshift import Pipeline
from vectorshift.pipeline import InputNode, OutputNode, PipelineNode, SplitTextNode


vectorshift.api_key = 'your api key '


sub_pipeline = Pipeline.fetch(name="your sub pipeline")

print(sub_pipeline)

input_node = InputNode(node_name="input_0")

split_text_node = SplitTextNode(
    node_name="split_text_node",
    text=input_node.text,
    delimiter="newline"
)

pipeline_node = PipelineNode(pipeline_id=sub_pipeline.id, 
    node_name="sub_pipeline", 
    input_0 = split_text_node.processed_text,
    execution_mode="batch"
)

output_node = OutputNode(node_name="output_0", value=pipeline_node.output_0)

main_pipeline = Pipeline.new(
    name="batched-pipeline",
    nodes=[input_node, split_text_node, pipeline_node, output_node]
)
```

### Streaming

```python
import vectorshift
from vectorshift.pipeline import Pipeline, InputNode, OutputNode, LlmNode

# Set API key
vectorshift.api_key = 'your api key here'

# Create input node
input_node = InputNode(node_name="input_0")

# Create LLM node that will stream responses
llm_node = LlmNode(
    node_name="llm_node",
    system="You are a helpful assistant.",
    prompt=input_node.text,
    provider="openai", 
    model="gpt-4o-mini",
    temperature=0.7,
    stream=True  # Enable streaming
)

# Create output node connected to LLM response
output_node = OutputNode(
    node_name="output_0",
    value=llm_node.response,
    output_type="stream<string>"
)

# Create and save the pipeline
pipeline = Pipeline.new(
    name="streaming-llm-pipeline-1",
    nodes=[input_node, llm_node, output_node]
)

# Run pipeline with streaming enabled
input_data = {"input_0": "Tell me a story about a brave adventurer"}

# Stream the response chunks
for chunk in pipeline.run(input_data, stream=True):
    try:
        # Parse the chunk as a JSON line
        chunk_str = chunk.decode('utf-8') if isinstance(chunk, bytes) else str(chunk)
        if chunk_str.startswith('data: '):
            json_str = chunk_str[6:]  # Remove 'data: ' prefix
            import json
            data = json.loads(json_str)
            if data.get('output_name') == 'output_0':
                print(data.get('output_value', ''), end="", flush=True)
    except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
        # If parsing fails, just continue to next chunk
        continue
```

### Async Usage

Call the async sdk methods by prefixing the sdk method with `a`. Here we can fetch a pipeline by name, run it with a particular input and await the pipeline results.
```python
import asyncio
import vectorshift

from vectorshift.pipeline import Pipeline, InputNode, OutputNode, LlmNode


vectorshift.api_key = "your api key here"


pipeline = Pipeline.fetch(name="your pipeline name here")

input_data = {"input_0": "Hello, how are you?"}

result  = asyncio.run(pipeline.arun(input_data))
print(result)
```

### Parallel Knowledge Base Upload
We can use the async methods to parallelize bulk upload of the files in a directory to a knowledge base. Here we have a script that takes in a vectorstore name and a local diretory to upload. 

```python
import asyncio
import os
import argparse
import vectorshift
from vectorshift.knowledge_base import KnowledgeBase, IndexingConfig
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

def upload_documents(vectorstore_name, upload_dir, max_concurrent=16):
    vectorshift.api_key = 'your api key here'
    vectorstore = KnowledgeBase.fetch(name=vectorstore_name)

    num_files = sum([len(files) for r, d, files in os.walk(upload_dir)])
    print(f'Number of files in the upload directory: {num_files}')
    
    async def upload_document(semaphore, script_path, document_title, dirpath):
        async with semaphore:
            try:
                # Create indexing configuration
                indexing_config = IndexingConfig(
                    chunk_size=512,
                    chunk_overlap=0,
                    file_processing_implementation='Default',
                    index_tables=False,
                    analyze_documents=False
                )
                response = await vectorstore.aindex_document(
                    document_type='file',
                    document=script_path,
                    indexing_config=indexing_config
                )
                return f"Response for {document_title} in directory {dirpath}: {response}"
            except Exception as e:
                return f"Response for {document_title} in directory {dirpath}: Failed due to {e}"

    async def upload_all_documents():
        # Create semaphore to limit concurrent uploads
        semaphore = asyncio.Semaphore(max_concurrent)
        
        all_files = []
        for dirpath, dirnames, filenames in os.walk(upload_dir):
            for script_file in filenames:
                script_path = os.path.join(dirpath, script_file)
                document_title = os.path.basename(script_path)
                all_files.append((script_path, document_title, dirpath))
        
        # Create tasks for all files
        tasks = []
        for script_path, document_title, dirpath in all_files:
            task = upload_document(semaphore, script_path, document_title, dirpath)
            tasks.append(task)
        
        # Process all tasks with progress bar
        with tqdm(total=len(all_files), desc="Uploading documents") as pbar:
            for coro in asyncio.as_completed(tasks):
                result = await coro
                if "Failed due to" in result:
                    print(f"Error: {result}")
                else:
                    print(result)
                pbar.update(1)
    
    asyncio.run(upload_all_documents())

if __name__ == "__main__":
    # Setup command line argument parsing
    parser = argparse.ArgumentParser(description='Upload documents to a VectorStore.')
    parser.add_argument('--vectorstore_name', type=str, required=True, help='Name of the VectorStore to upload documents to.')
    parser.add_argument('--upload_dir', type=str, required=True, help='Directory path of documents to upload.')
    parser.add_argument('--max_concurrent', type=int, default=16, help='Maximum number of concurrent uploads.')
    args = parser.parse_args()

    upload_documents(args.vectorstore_name, args.upload_dir, args.max_concurrent)
```

## Version Control 
The sdk can be used to version control and manage updates to pipelines defined in code.

Lets say we created a pipeline
```python
import vectorshift
from vectorshift.pipeline import Pipeline, InputNode, OutputNode, LlmNode
# Set API key
vectorshift.api_key = "your api key here"

input_node = InputNode(node_name="input_0")

llm_node = LlmNode(
    node_name="llm_node",
    system="You are a helpful assistant.",
    prompt=input_node.text,
    provider="openai",
    model="gpt-4o-mini",
    temperature=0.7
)

output_node = OutputNode(
    node_name="output_0",
    value=llm_node.response
)

pipeline = Pipeline.new(
    name="basic-llm-pipeline",
    nodes=[input_node, llm_node, output_node]
)
```
If we  want to update the llm used to gpt4o we can change the LLM in the node and save the pipeline with the new node definitions. The deployed pipeline will automatically be updated. 

```python
import vectorshift
from vectorshift.pipeline import Pipeline, InputNode, OutputNode, LlmNode

input_node = InputNode(node_name="input_0")

llm_node = LlmNode(
    node_name="llm_node",
    system="You are a helpful assistant.",
    prompt=input_node.text,
    provider="openai",
    model="gpt-4o",
    temperature=0.7
)

output_node = OutputNode(
    node_name="output_0",
    value=llm_node.response
)

pipeline = Pipeline.fetch(name="basic-llm-pipeline")

output = pipeline.save(
    nodes=[input_node, llm_node, output_node]
)
print(output)
```

## Chatbots

Run a chatbot. This code allows you to chat with your chatbot in your terminal. Since we provide conversation_id = None in the initial run the chatbot will start a new conversation. Note how by entering the conversation id returned by chatbot.run we can continue the conversation and have the chatbot see previous repsponses. 
```python 

from vectorshift import Chatbot
chatbot = Chatbot.fetch(name = 'your chatbot name')

conversation_id = None
while True:
    user_input = input("User: ")
    if user_input.lower() == "quit":
        break
    response = chatbot.run(input=user_input, input_type="text", conversation_id=conversation_id)
    conversation_id = response['conversation_id']
    print(response['output_message'])
```

Streaming Chatbot


```python

from vectorshift import Chatbot
chatbot = Chatbot.fetch(name = 'your chatbot name')

conversation_id = None
while True:
    user_input = input("User: ")
    if user_input.lower() == "quit":
        break
    response_stream = chatbot.run(input=user_input, input_type="text", conversation_id=conversation_id, stream=True)
    conversation_id = None
    for chunk in response_stream:
        try:
            chunk_str = chunk.decode('utf-8') if isinstance(chunk, bytes) else str(chunk)
            if chunk_str.startswith('data: '):
                json_str = chunk_str[6:]  # Remove 'data: ' prefix
                import json
                data = json.loads(json_str)
                if data.get('conversation_id'):
                    conversation_id = data.get('conversation_id')
                elif data.get('output_value') and data.get('type') == 'stream':
                    print(data.get('output_value', ''), end="", flush=True)
        except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
            continue
    print()  # Add newline after streaming is complete
```

Chatbot File Upload

```python
from vectorshift import Chatbot
import os
import json
chatbot = Chatbot.fetch(name='your chatbot name')

conversation_id = None
while True:
    user_input = input("User: ")
    if user_input.lower() == "quit":
        break
    
    # Handle file upload
    if user_input.startswith("add_file "):
        file_path = user_input[9:]  # Remove "add_file " prefix
        if os.path.isfile(file_path):
            try:
                upload_response = chatbot.upload_files(file_paths=[file_path], conversation_id=conversation_id)
                conversation_id = upload_response.get('conversation_id')
                print(f"File uploaded successfully: {upload_response.get('uploaded_files', [])}")
            except Exception as e:
                print(f"Error uploading file: {e}")
        else:
            print(f"File not found: {file_path}")
        continue
    
    # Handle text input with streaming
    response_stream = chatbot.run(input=user_input, input_type="text", conversation_id=conversation_id, stream=True)
    
    for chunk in response_stream:
        try:
            chunk_str = chunk.decode('utf-8') if isinstance(chunk, bytes) else str(chunk)
            if not chunk_str.startswith('data: '):
                continue
                
            data = json.loads(chunk_str[6:])  # Remove 'data: ' prefix
            
            # Update conversation_id if present
            if data.get('conversation_id'):
                conversation_id = data.get('conversation_id')
            
            # Print streaming output
            if data.get('output_value') and data.get('type') == 'stream':
                print(data.get('output_value', ''), end="", flush=True)
                
        except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
            continue
    
    print()  # Add newline after streaming
```

## Integrations
Integration nodes accept an integration object that include the id of your integration

```python
from vectorshift.pipeline import IntegrationSlackNode, InputNode, Pipeline
from vectorshift.integrations import IntegrationObject
input_node = InputNode(node_name="input_0", description = 'Gmail Message to Send')

integration_id = 'your integration id'
integration = IntegrationObject(object_id = integration_id)
gmail_node = IntegrationGmailNode(
    integration = integration,
    node_name="gmail_node",
    action="send_email",
    recipients="recipient@gmail.com",
    subject="Test Email from Pipeline",
    body=input_node.text,
    format="text"
)

gmail_pipeline = Pipeline.new(
    name="gmail-pipeline",
    nodes=[input_node, gmail_node]
)
```

To use the slack node specify the channel and team id accessible from the slack app
```python
from vectorshift.pipeline import IntegrationSlackNode, InputNode, Pipeline
from vectorshift.integrations import IntegrationObject
input_node = InputNode(node_name="input_0", description = 'Slack Message to Send')


integration_id = 'your_integration_id'
slack_node = IntegrationSlackNode(
    node_name="slack_node", 
    integration = IntegrationObject(object_id = integration_id),
    action = 'send_message',
    channel = 'your_channel_id',
    message = input_node.text,
    team = 'your_team_id'
)

slack_pipeline = Pipeline.new(
    name = 'slack-pipeline',
    nodes = [input_node, slack_node]
)
```