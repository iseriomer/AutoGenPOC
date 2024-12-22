import datetime


def intent_detection_prompt(text):
    prompt =  f"""
            You should classify the intent from the given text into one of the given categories, with also including it as snake case.     
            If it is irrelevant to the below types, just return "".

            Request Types:
            Time Event = A Time Event in an SAP system refers to the daily logging of an employee's working hours. 
            For example Clock In, Clock Out, Breaks, Overtime, Attendance, Off-site Works etc. 
            Users can also request to view their time event entries.
            Leave Request = A Leave Request in an SAP system is used to manage an employee's request for time off. 
            Users can also request to view their leave request entries.
            This could include vacation days, sick leave, personal days, or any other type of leave, or home offices. 
            View Balances = view the remaining leave days 
            View Entitlement = view the entitlement list 
            Download Time Statement = download time statement 

            Also return what type of request is being made, in the "type" field. 
            If the given text is about creating an entry, return "create" in the "type" field. 
            If the given text is about viewing the entries, return "view" in the "type" field. 
            If the given text is about deleting the entries, return "delete" in the "type" field. 
            If the given text is about editing the entries, return "edit" in the "type" field. 
            If the given text is about downloading, return "download" in the "type" field.

            Also, if the user writes things that intend to being in the or leaving the office, it is probably a time event. 
            If the user writes things that intend to being in the doctor, in the beach, or in the university it is probably a leave request.

            Return a JSON. Here are some examples: 

            Text: I want to clock in now. {{"type": "create", "intent": "Time Event", "snake_case": "time_event"}}
            Text: I want to delete my clock in. {{"type": "delete", "intent": "Time Event", "snake_case": "time_event"}}
            Text: I need to see my doctor. {{"type": "create", "intent": "Leave Request", "snake_case": "leave_request"}}
            Text: I want to make a vacation next week. {{"type": "create", "intent": "Leave Request", "snake_case": "leave_request"}}
            Text: I want to view my leave requests. {{"type": "view", "intent": "Leave Request", "snake_case": "leave_request"}}
            Text: I want to edit my leave requests. {{"type": "edit", "intent": "Leave Request", "snake_case": "leave_request"}}
            Text: timeslip. {{"type": "download", "intent": "Download Time Statement", "snake_case": "download_time_statement"}}
            Text: I want to view my entitlements. {{"type": "view", "intent": "View Entitlement", "snake_case": "view_entitlement"}}
            
            Provide the answer as a JSON-based response, without adding any explanation.

            Text: {text}

            """
    return prompt

def is_interval(text):
    includes_interval_prompt = f"""
    I will provide you with a text in English or German.
    The text includes either a single datetime or an interval of datetimes.

    Examples of dates:
    "10.10.2024"
    "first day of the month"
    "Christmas Day"

    Examples of intervals:
    "this week"
    "until the end of this year"
    "next month"
    "Christmas season"
    "from now until tomorrow"
    "from 15:00 to 16:00"

    Rules:

    If the text includes a single day (e.g., "today", "tomorrow", "15th of July") without time information, it is not an interval.
    If the text includes a time (e.g., "15:00", "next Friday at 16:00"), it is not an interval.
    If the text includes a timespan (e.g., "from 13:00 to 16:00", "from now until 18:00"), it is an interval.

    Output:
    Return a JSON object with a single field:
    "result": a boolean value.
    true if the given text represents an interval.
    false if it represents a single datetime.

    Strict: Do not include any explanations.

    Text: {text}

    """
    return includes_interval_prompt

def is_datetime(text):
    includes_temporal_reference_prompt = f"""
    I will give you a text in English or German.

    Determine if this text includes specific temporal references.

    Specific temporal references can be expressed as:
    Words like "now", "tomorrow", "next month", "Christmas", "since this month".
    Specific datetime formats like "10.02.2024" or "10:30".
    In german they can be "anfang des jahres", "seit letzte Jahr", "heute", "jetzt".

    Examples of texts that do NOT include specific temporal references are:

    "view your time events"
    "clock in"
    "leave"
    "view entitlements"

    Note: The presence of the words "time" or "date" alone does not count as including specific temporal references.

    Strict: Return a JSON object with a boolean field result, set to true if the text includes specific temporal references, and false if it does not.
    Strict: Do not give any explanation.

    Text: {text}
    """
    return includes_temporal_reference_prompt

def datetime_extract(text):
    now = datetime.datetime.now()  # Get the current datetime once

    extract_datetime_prompt = f"""
    I will provide you with a text in English or German that includes a datetime.

    Task:
    Extract the date and time from the given text.

    Return the result in the following format:
    Date: "YYYY-MM-DD"
    Time: "HH:MM:SS"

    Output Format:
    Strict: return a JSON object with the following fields:
    {{
      "date": "YYYY-MM-DD",
      "time": "HH:MM:SS"
    }}

    Rules:
    Base all interpretations on the reference datetime, consider that it is now: {now}.
    Consider datetime references such as today, tomorrow and now, and use the given reference time to answer.
    Strict: Return a date and time in all conditions.
    Strict: Do not give any explanation.
    Strict: If no datetime is found, return the current datetime (now).

    Text: {text}
    """
    return extract_datetime_prompt