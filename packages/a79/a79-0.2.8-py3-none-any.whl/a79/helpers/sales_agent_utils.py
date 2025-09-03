import json
import re
import sys
from difflib import SequenceMatcher


def call_llm_with_template_and_set_variable(
    llm, model_name, prompt_template, variable_name, parse_json=True
):
    print(f"Calling LLM with template: {prompt_template}")
    # Call LLM for analysis
    analysis_result = llm.chat(model=model_name, prompt_str=prompt_template)

    analysis_content = analysis_result.content
    if parse_json:
        # Extract JSON content from markdown code blocks
        json_match = re.search(r"```json\s*([\s\S]*?)\s*```", analysis_content, re.DOTALL)
        if json_match:
            json_content = json_match.group(1).strip()
        else:
            # Try to find JSON without code blocks
            json_match = re.search(r"({[\s\S]*})", analysis_content)
            if json_match:
                json_content = json_match.group(1).strip()
            else:
                print(
                    f"Invalid JSON in analysis content {analysis_content} "
                    f"and {variable_name}",
                    file=sys.stderr,
                )
                raise ValueError(
                    f"No JSON found in content {analysis_content} and {variable_name}"
                )

        try:
            from json_repair import repair_json

            json_content = repair_json(json_content)
            parsed_json = json.loads(json_content)
        except json.JSONDecodeError as e:
            print(
                f"Invalid JSON in analysis content {json_content} "
                f"and {variable_name}: {e}",
                file=sys.stderr,
            )
            raise ValueError(
                f"Invalid JSON in  content {json_content} and {variable_name}: {e}"
            ) from e

        # Return the parsed JSON so it can be assigned to a variable in the calling code
        globals()[variable_name] = parsed_json
        return parsed_json
    else:
        globals()[variable_name] = analysis_content
        return analysis_content


def find_best_transcript_message(
    quote: str, transcript_messages: list[dict]
) -> dict | None:
    """Find the best matching message for a given quote.

    Args:
        quote: The quote to find the best match for.
        transcript_messages: The list of messages to search through.
        example:
            quote: "Do you want a CRM?"
            transcript_messages: [
                {
                    "message": "Do you want a CRM?"
                    start_seconds: 0
                    end_seconds: 5
                    role: "sales guy"
                },
                {
                    "message": "LOL no!"
                    start_seconds: 5
                    end_seconds: 10
                    role: "customer"
                }
            ]

    Returns:
        The best matching message dict.
    """
    best_match = None
    best_ratio = 0.0

    # Clean the quote for better matching
    clean_quote = quote.strip().lower()

    for msg in transcript_messages:
        if not isinstance(msg, dict):
            continue
        if "message" not in msg:
            continue

        message_text = msg["message"].strip().lower()

        # Calculate similarity ratio
        ratio = SequenceMatcher(None, clean_quote, message_text).ratio()

        # Also check if quote is a substring (for partial quotes)
        if clean_quote in message_text or message_text in clean_quote:
            ratio = max(ratio, 0.8)  # Boost similarity for substring matches

        if ratio > best_ratio and ratio > 0.6:  # Minimum threshold
            best_ratio = ratio
            best_match = msg

    return best_match
