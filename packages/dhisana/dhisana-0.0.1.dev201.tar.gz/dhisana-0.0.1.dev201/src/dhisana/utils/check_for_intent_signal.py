import datetime
import logging
from typing import Any, Dict, List, Optional, cast

from pydantic import BaseModel
from dhisana.utils.generate_structured_output_internal import get_structured_output_internal
from dhisana.utils.compose_search_query import (
    get_search_results_for_insights
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class IntentSignalScoring(BaseModel):
    score_based_on_intent_signal: int
    reasoning_for_score_being_high: str
    summary_of_lead_and_company: str


async def check_for_intent_signal(
    lead: Dict[str, Any],
    signal_to_look_for_in_plan_english: str,
    intent_signal_type: str,
    add_search_results: Optional[bool] = False,
    tool_config: Optional[List[Dict[str, Any]]] = None
) -> int:
    """
    Evaluate a 'lead' for a specific intent signal and return an integer score from 0–5.
    """

    logger.info("check_for_intent_signal called with lead=%s, intent_signal_type=%s", lead.get("full_name"), intent_signal_type)

    search_results_text = ""
    if add_search_results:
        logger.info("Fetching search results for lead='%s' with signal='%s'", lead.get("full_name"), intent_signal_type)
        search_results = await get_search_results_for_insights(
            lead=lead,
            english_description=signal_to_look_for_in_plan_english,
            intent_signal_type=intent_signal_type,
            tool_config=tool_config
        )
        logger.info("Received search results count: %d", len(search_results))

        for item in search_results:
            query_str = item.get("query", "")
            results_str = item.get("results", "")
            logger.info("Search query: %s", query_str)
            logger.info("Search results snippet: %s", results_str[:100])  # Show partial snippet
            search_results_text += f"Query: {query_str}\nResults: {results_str}\n\n"
    datetime.datetime.now().isoformat()
    user_prompt = f"""
    Hi AI Assistant,
    You are an expert in scoring leads based on intent signals.
    You have the following lead and user requirements to provide a  qulifying lead score score between 0 and 5 
    based on the intent signal the user is looking for.
    Do the following step by step:
    1. This about the summary of the lead and the company lead is working for.
    2. Create a summary of the search results obtained.     
    3. Think about the signal user is looking for to qualify and score the lead. 
    4. Use the lead information, summary of search results and signal user is looking for to score the lead.
    5. Go back and check if the score makes sense. Score between 0-5 based on the confidence of the signal.
    
    Lead Data:
    {lead}

    Description of the signal user is looking for:
    {signal_to_look_for_in_plan_english}
    
    Following is some search results I found online. Use them if they are relevant for scoring:
    {search_results_text}
    

    Return your answer in valid JSON with the key 'score_based_on_intent_signal'.
    Make sure it is an integer between 0 and 5.
    Add small reasoning_for_score_bing_high describing why you gave the score score_based_on_intent_signal as high if you are giving high score.
    in summary_of_lead_and_company field provide a summary of the lead (like role, experience, tenure, locaion) and details about the company lead is working for currently.
    """
    logger.info("Constructed user prompt for LLM.")

    response_any, status = await get_structured_output_internal(
        user_prompt,
        IntentSignalScoring,
        effort="low",
        tool_config=tool_config
    )
    logger.info("Intent signal scoring call completed with status=%s", status)

    if status != "SUCCESS" or response_any is None:
        logger.error("Failed to generate an intent signal score from the LLM.")
        raise Exception("Failed to generate an intent signal score from the LLM.")

    response = cast(IntentSignalScoring, response_any)
    score = response.score_based_on_intent_signal
    reasoning = response.reasoning_for_score_being_high[:100]  # Show partial if very long
    lead["qualification_score"] = score
    lead["qualification_reason"] = response.reasoning_for_score_being_high
    lead["summary_about_lead"] = response.summary_of_lead_and_company

    logger.info(
        "Lead '%s' scored %d for intent signal '%s'. Reason partial: %s",
        lead.get("full_name", "Unknown"),
        score,
        intent_signal_type,
        reasoning
    )
    return score