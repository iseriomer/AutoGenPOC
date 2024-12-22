import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import autogen
from autogen import ConversableAgent
from code.prompts import intent_detection_prompt, is_datetime, is_interval, datetime_extract
import tempfile
from .prompts import intent_detection_prompt 

# Initialize FastAPI app
app = FastAPI()

# Define the input model for the user query
class UserInput(BaseModel):
    message: str

# Define the Llama configuration
llama = {
    "config_list": [
        {
            "model": "llama-3.2-1b-instruct",
            "base_url": "http://127.0.0.1:1234/v1",
            "api_key": "lm-studio",
        },
    ],
    "cache_seed": None,  # Disable caching.
}

# Initialize the human proxy
human_proxy = ConversableAgent(
    "human_proxy",
    llm_config=False,  # no LLM used for human proxy
    human_input_mode="ALWAYS",  # always ask for human input
)

# Intent detection agent function
def detect_intent(user_text: str):
    intent_detector_agent = ConversableAgent(
        "Intent Detector",
        llm_config=llama,
        system_message=intent_detection_prompt(user_text),
        is_termination_msg=lambda msg: "good bye" in msg["content"].lower(),
    )
    
    human_proxy.initiate_chat(
        intent_detector_agent,
        message=user_text,
        max_turns=1,
    )
    
    last_message = intent_detector_agent.last_message()
    
    # Parse the JSON content and extract the 'snake_case' value
    try:
        content_dict = json.loads(last_message['content'])
        return content_dict
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Error in parsing response content")

def detect_datetime(user_text: str):
    datetime_detector_agent = ConversableAgent(
        "Datetime Detector",
        llm_config=llama,
        system_message=is_datetime(user_text),
        is_termination_msg=lambda msg: "good bye" in msg["content"].lower(),
    )

    human_proxy.initiate_chat(
        datetime_detector_agent,
        message=user_text,
        max_turns=1,
    )

    last_message = datetime_detector_agent.last_message()
    
    # Parse the JSON content and extract the 'content' value
    try:
        content_dict = json.loads(last_message['content'])
        return content_dict
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Error in parsing response content")

def extract_interval(user_text: str):
    interval_detector_agent = ConversableAgent(
        "Interval Detector",
        llm_config=llama,
        system_message=is_interval(user_text),
        is_termination_msg=lambda msg: "good bye" in msg["content"].lower(),
    )

    human_proxy.initiate_chat(
        interval_detector_agent,
        message=user_text,
        max_turns=1,
    )

    last_message = interval_detector_agent.last_message()
    # Parse the JSON content and extract the 'content' value
    try:
        content_dict = json.loads(last_message['content'])
        return content_dict
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Error in parsing response content")

def extract_datetime(user_text: str):
    datetime_extractor_agent = ConversableAgent(
        "Datetime Extractor",
        llm_config=llama,
        system_message=datetime_extract(user_text),
        is_termination_msg=lambda msg: "good bye" in msg["content"].lower(),
    )
    json_checker_agent = ConversableAgent(
        "JSON Checker",
        llm_config=llama,
        system_message= """you are a chatbot who returns only in json format. check if the given value is in a format like this:
                    {{
                    "date": "YYYY-MM-DD",
                    "time": "HH:MM:SS"
                    }} 
                    and return in the above format. DO NOT RETURN ANYTHING ELSE.
                    """
    )
    human_proxy.initiate_chat(
        datetime_extractor_agent,
        message=user_text,
        max_turns=1,
    )

    last_message = datetime_extractor_agent.last_message()
    human_proxy.initiate_chat(
        json_checker_agent,
        message=last_message,
        max_turns=1,
    )
    last_message_in_json = json_checker_agent.last_message()
    # Parse the JSON content and extract the 'content' value
    try:
        content_dict = json.loads(last_message_in_json['content'])
        return content_dict
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Error in parsing response content")

# Define the API endpoint for detecting intent
@app.post("/detect-intent")
async def detect_intent_api(input: UserInput):
    user_text = input.message
    
    # Get the snake_case value from the intent detection
    snake_case_value = detect_intent(user_text)
    
    if not snake_case_value:
        raise HTTPException(status_code=404, detail="No snake_case value found")
    
    # Return the result as a JSON response
    return {"snake_case": snake_case_value}



@app.post("/extract-datetime")
async def extract_datetime_api(input: UserInput):
    user_text = input.message
    # Get the snake_case value from the intent detection
    is_datetime = detect_datetime(user_text)
    if is_datetime["result"]:
        interval = extract_interval(user_text)
        datetime = extract_datetime(user_text)

        
    # Return the result as a JSON response
    return {"datetime_extraction": is_datetime,
            "interval": interval,
            "datetime": datetime
            }