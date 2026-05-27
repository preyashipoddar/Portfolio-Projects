import os
import json
import jsonschema
from openai import OpenAI
from tavily import TavilyClient
from retrieve import search_contract
from prompts import SYSTEM_PROMPT, SCAN_PROMPT, ASK_PROMPT
from schemas import RISK_FLAG_SCHEMA, ASK_SCHEMA
from dotenv import load_dotenv

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Tool definition for GPT-4o function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for legal context about a specific clause or legal standard. Use this when you need to know what is legally standard or required for a flagged clause.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query e.g. 'minimum landlord notice entry California law'"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

def web_search(query: str) -> str:
    print(f"  [TOOL CALL] web_search: {query}")
    results = tavily_client.search(query, max_results=3)
    return "\n\n".join([r["content"] for r in results["results"]])

def validate_risk_flags(risks: list) -> tuple:
    valid = []
    failures = []
    for i, risk in enumerate(risks):
        try:
            jsonschema.validate(risk, RISK_FLAG_SCHEMA)
            valid.append(risk)
        except jsonschema.ValidationError as e:
            failures.append({"index": i, "error": str(e.message), "output": risk})
    return valid, failures

def validate_ask_output(output: dict) -> tuple:
    try:
        jsonschema.validate(output, ASK_SCHEMA)
        return True, None
    except jsonschema.ValidationError as e:
        return False, str(e.message)

def run_with_tools(messages: list) -> str:
    """Handle tool calls, then make a final call to get clean JSON output."""
    # First pass — let the model call tools
    while True:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )
        msg = response.choices[0].message

        # No more tool calls — done with research phase
        if not msg.tool_calls:
            break

        # Process tool calls and add results to messages
        messages.append(msg)
        for tool_call in msg.tool_calls:
            if tool_call.function.name == "web_search":
                args = json.loads(tool_call.function.arguments)
                result = web_search(args["query"])
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

    # Second pass — force clean JSON output with no tools available
    messages.append({
        "role": "user",
        "content": "Now output a JSON object with a single key 'risks' containing an array of all risk flags you identified. Each risk flag must have: clause, section, risk_level, plain_english, legal_context, recommendation, disclaimer. Example: {\"risks\": [{...}, {...}]}"
    })
    final_response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_format={"type": "json_object"}
    )
    result = final_response.choices[0].message.content
    return result

def run_ask(doc_id: str, question: str) -> dict:
    chunks = search_contract(doc_id, question, top_k=5)
    context = "\n\n---\n\n".join(chunks)
    prompt = ASK_PROMPT.format(context=context, question=question)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]

    # Tool calling pass
    while True:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )
        msg = response.choices[0].message
        if not msg.tool_calls:
            break
        messages.append(msg)
        for tool_call in msg.tool_calls:
            if tool_call.function.name == "web_search":
                args = json.loads(tool_call.function.arguments)
                result = web_search(args["query"])
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

    # Final structured output pass
    messages.append({
        "role": "user",
        "content": "Now output a JSON object with exactly these fields: answer, cited_clause, section, disclaimer."
    })
    final_response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_format={"type": "json_object"}
    )
    output = json.loads(final_response.choices[0].message.content)

    # Sanitize null values to empty strings to maintain schema compliance
    for field in ["answer", "cited_clause", "section", "disclaimer"]:
        if output.get(field) is None:
            output[field] = "N/A"
    valid, error = validate_ask_output(output)
    if not valid:
        print(f"[VALIDATION WARNING] Ask output failed schema: {error}")
    else:
        print("[VALIDATION PASSED] Ask output matches schema.")

    return output

def run_scan(doc_id: str) -> list:
    chunks = search_contract(doc_id,
        "risky unusual one-sided unfair clause penalty termination liability deposit",
        top_k=10)
    context = "\n\n---\n\n".join(chunks)
    prompt = SCAN_PROMPT.format(context=context)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]

    raw = run_with_tools(messages)
    raw = raw.strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Could not parse response as JSON: {e}")
        print(f"Raw response: {raw[:200]}")
        return []

    # Extract the array from the risks key or find any list value
    if isinstance(parsed, dict):
        risks = parsed.get("risks") or next(
            (v for v in parsed.values() if isinstance(v, list)), []
        )
    elif isinstance(parsed, list):
        risks = parsed
    else:
        risks = []

    valid, failures = validate_risk_flags(risks)

    if failures:
        print(f"[VALIDATION WARNING] {len(failures)} risk flag(s) failed schema:")
        for f in failures:
            print(f"  Index {f['index']}: {f['error']}")
    else:
        print(f"[VALIDATION PASSED] All {len(valid)} risk flags match schema.")

    return valid