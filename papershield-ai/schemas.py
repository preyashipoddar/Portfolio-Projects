RISK_FLAG_SCHEMA = {
    "type": "object",
    "required": ["clause", "section", "risk_level", "plain_english", "legal_context", "recommendation", "disclaimer"],
    "properties": {
        "clause": {"type": "string"},
        "section": {"type": "string"},
        "risk_level": {"type": "string", "enum": ["low", "medium", "high"]},
        "plain_english": {"type": "string"},
        "legal_context": {"type": "string"},
        "recommendation": {"type": "string"},
        "disclaimer": {"type": "string"}
    },
    "additionalProperties": False
}

ASK_SCHEMA = {
    "type": "object",
    "required": ["answer", "cited_clause", "section", "disclaimer"],
    "properties": {
        "answer": {"type": "string"},
        "cited_clause": {"type": "string"},
        "section": {"type": "string"},
        "disclaimer": {"type": "string"}
    },
    "additionalProperties": False
}