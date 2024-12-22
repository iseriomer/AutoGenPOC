import autogen
from autogen import ConversableAgent

# Create a temporary directory to store the code files.
temp_dir = tempfile.TemporaryDirectory()

# Create a Docker command line code executor.
executor = DockerCommandLineCodeExecutor(
    image="python:3.12-slim",  # Execute code using the given docker image name.
    timeout=10,  # Timeout for each code execution in seconds.
    work_dir=temp_dir.name,  # Use the temporary directory to store the code files.
)

# Create an agent with code executor configuration that uses docker.
code_executor_agent_using_docker = ConversableAgent(
    "code_executor_agent_docker",
    llm_config=False,  # Turn off LLM for this agent.
    code_execution_config={"executor": executor},  # Use the docker command line code executor.
    human_input_mode="ALWAYS",  # Always take human input for this agent for safety.
)

llama = {
    "config_list": [
        {
            "model": "llama-3.2-1b-instruct",
            "base_url": "http://localhost:1234/v1",
            "api_key": "lm-studio",
        },
    ],
    "cache_seed": None,  # Disable caching.
}

omer = ConversableAgent(
    "Omer",
    llm_config=llama,  # Use llama 
    system_message="Your name is Ömer and you are boyfriend of neva. You suggest only very good movies to neva when she asks",
    is_termination_msg=lambda msg: "good bye" in msg["content"].lower(),
)

neva = ConversableAgent(
    "Neva",
    llm_config=llama,  # Use llama
    system_message="Your name is Neva and you are girlfriend of Omer",
)

human_proxy = ConversableAgent(
    "human_proxy",
    llm_config=False,  # no LLM used for human proxy
    human_input_mode="ALWAYS",  # always ask for human input
)


#reply = neva.generate_reply(messages=[{"content": "who are you?", "role": "user"}])
#print(reply)


#conversation = omer.initiate_chat(neva, message="How are today darling Neva, do you have any plans for tonight", max_turns=2)
#print(conversation)

# Start a chat with the agent with number with an initial guess.
result = human_proxy.initiate_chat(
    omer,  # this is the same agent with the number as before
    message="10",
)