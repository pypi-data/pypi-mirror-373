from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from dhisana.schemas.sales import (
    ContentGenerationContext,
    Lead,
    MessageItem,
    MessageResponse,
    MessageGenerationInstructions,
    SenderInfo
)
from dhisana.utils.generate_structured_output_internal import (
    get_structured_output_internal,
    get_structured_output_with_assistant_and_vector_store
)
from dhisana.utils.assistant_tool_tag import assistant_tool
import datetime

# ---------------------------------------------------------------------------------------
# MODEL
# ---------------------------------------------------------------------------------------
class LinkedInTriageResponse(BaseModel):
    """
    Model representing the structured response for a LinkedIn conversation triage.
    - triage_status: "AUTOMATIC" or "REQUIRES_APPROVAL"
    - triage_reason: Optional reason text if triage_status == "REQUIRES_APPROVAL"
    - response_action_to_take: The recommended next action (e.g., SEND_REPLY, WAIT_TO_SEND, STOP_SENDING, etc.)
    - response_message: The actual message (body) to be sent or used for approval.
    """
    triage_status: str  # "AUTOMATIC" or "REQUIRES_APPROVAL"
    triage_reason: Optional[str]
    response_action_to_take: str
    response_message: str
    meeting_offer_sent: Optional[bool]


# ---------------------------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------------------------
def cleanup_reply_linkedin_context(linkedin_context: ContentGenerationContext) -> ContentGenerationContext:
    """
    Create a copy of the context and remove unneeded or sensitive fields.
    """
    clone_context = linkedin_context.copy(deep=True)
    
    # Example: removing tasks or statuses that are not needed for triage
    clone_context.lead_info.task_ids = None
    clone_context.lead_info.research_status = None
    clone_context.lead_info.email_validation_status = None
    clone_context.lead_info.linkedin_validation_status = None
    clone_context.lead_info.enchrichment_status = None
    
    return clone_context


async def generate_linkedin_response_message_copy(
    linkedin_context: ContentGenerationContext,
    variation: str,
    tool_config: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Generates a single variation of a triaged LinkedIn response using the provided context.
    Returns a structured result conforming to LinkedInTriageResponse.
    """
    allowed_actions = [
        "SCHEDULE_MEETING",
        "SEND_REPLY",
        "UNSUBSCRIBE",
        "OOF_MESSAGE",
        "NOT_INTERESTED",
        "NEED_MORE_INFO",
        "FORWARD_TO_OTHER_USER",
        "NO_MORE_IN_ORGANIZATION",
        "OBJECTION_RAISED",
        "END_CONVERSATION"
    ]
    
    cleaned_context = cleanup_reply_linkedin_context(linkedin_context)
    
    # Safely handle the current_conversation_context if it exists.
    if cleaned_context.current_conversation_context:
        if not cleaned_context.current_conversation_context.current_email_thread:
            cleaned_context.current_conversation_context.current_email_thread = []
        
        if not cleaned_context.current_conversation_context.current_linkedin_thread:
            cleaned_context.current_conversation_context.current_linkedin_thread = []
        
        # Safely extract the conversation thread for prompt formatting.
        conversation_thread_dump = [
            thread_item.model_dump()
            for thread_item in cleaned_context.current_conversation_context.current_linkedin_thread
        ]
    else:
        # If current_conversation_context is None, use an empty thread.
        conversation_thread_dump = []
    
    current_date_iso = datetime.datetime.now().isoformat()
    lead_data = linkedin_context.lead_info or Lead()
    sender_data = linkedin_context.sender_info or SenderInfo()
    campaign_context = linkedin_context.campaign_context or CampaignContext()

    prompt = f"""
        You are a specialized linkedin message reply assistant. 
        Your task is to analyze the user's linkedin message thread, the user/company info,
        and the provided triage guidelines to craft an appropriate response.

        Follow these instructions to generate the reply: 
        {variation}

        1. Message thread or conversation to respond to:
        {conversation_thread_dump}

        2.
        Lead Information:
        {lead_data.dict()}

        Sender Information:
        Full Name: {sender_data.sender_full_name or ''}
        First Name: {sender_data.sender_first_name or ''}
        Last Name: {sender_data.sender_last_name or ''}
        Bio: {sender_data.sender_bio or ''}

        3. Campaign-specific triage guidelines (user overrides always win):
        {campaign_context.linkedin_triage_guidelines}

        -----------------------------------------------------------------
        Core decision logic
        -----------------------------------------------------------------
        • If the request is routine, non-sensitive, and clearly actionable  
        → **triage_status = "AUTOMATIC"**.  
        • If the thread contains PII, finance, legal, or any sensitive/NSFW content  
        → **triage_status = "END_CONVERSATION"** and give a concise **triage_reason**.

        4. Choose exactly ONE of: {allowed_actions}

        -----------------------------------------------------------------
        Response best practices
        -----------------------------------------------------------------
        • MAX 150 words, friendly & concise, single clear CTA.  
        • Begin with a thank-you, mirror the prospect’s wording briefly, then answer /
        propose next step.  
        • Never contradict, trash-talk, or disparage {lead_data.organization_name}.  
        • Plain-text only – NO HTML tags (<a>, <b>, <i>, etc.).  
        • If a link already exists in the inbound message, include it verbatim—do not re-wrap or shorten.

        Meeting & follow-up rules
        -------------------------
        1. Let `meeting_offer_sent` = **true** if any earlier assistant message offered a
        meeting.  
        2. If First “Thanks / Sounds good” & *no* prior meeting offer  
            → **SEND_REPLY** asking for a 15-min call (≤150 words).  
        3. If Second non-committal reply *after* meeting_offer_sent, or explicit “not interested”  
            → **END_CONVERSATION**.  
        4. If prospect explicitly asks for times / requests your link  
            → **SCHEDULE_MEETING** and confirm or propose times.  
        5. If One unsolicited follow-up maximum; stop unless prospect re-engages.

        If you have not proposed a meeting even once in the thread, and the user response is polite acknowledgment then you MUST request for a meeting.


        Objections & info requests
        --------------------------
        • Pricing / docs / case-studies request → **NEED_MORE_INFO**.  
        • Budget, timing, or competitor concerns → **OBJECTION_RAISED**  
        (acknowledge + one clarifying Q or concise value point).  
        • “Loop in {{colleague_name}}” → **FORWARD_TO_OTHER_USER**.

        Unsubscribe & priority handling
        -------------------------------
        1. “Unsubscribe / Remove me” → **UNSUBSCRIBE**  
        2. Clear lack of interest → **NOT_INTERESTED**  
        3. Auto OOO reply → **OOF_MESSAGE**  
        4. Explicit meeting request → **SCHEDULE_MEETING**  
        5. Otherwise follow the Meeting & follow-up rules above  
        6. Default → **END_CONVERSATION**

        Style guard-rails
        -----------------
        • Plain language; no jargon or filler.  
        • Do **not** repeat previous messages verbatim.  
        • Signature must include sender_first_name exactly as provided.  
        • Check UNSUBSCRIBE / NOT_INTERESTED first before other triage.

        If you have not proposed a meeting even once in the thread, and the user response is polite acknowledgment then you MUST request for a meeting.
         
        • Meeting ask template example:
        Hi {{lead_first_name}}, would you be open to a quick 15-min call to
        understand your use-case and share notes?

        • Competitor-stack mention template example:
        Hi {{lead_first_name}}, thanks for sharing your current stack. Would you be
        open to a 15-min call to explore where we can add value?
        
    Use conversational name for company name.
    Use conversational name when using lead first name.
    Do not use special characters or spaces when using lead’s first name.
    In the subject or body DO NOT include any HTML tags like <a>, <b>, <i>, etc.
    The body and subject should be in plain text.
    If there is a link provided in the message, use it as is; do not wrap it in any HTML tags.
    DO NOT make up information. Use only the information provided in the context and instructions.
    Do NOT repeat the same message sent to the user in the past.
    Keep the thread conversational and friendly as a good account executive would respond.
    Do NOT rehash/repeat the same previous message already sent. Keep the reply to the point.
    DO NOT try to spam users with multiple messages. 
    Current date is: {current_date_iso}.
    DO NOT share any link to internal or made up document. You can attach or send any document.
    If the user is asking for any additional document END_CONVERSATION and let Account executive handle it.
    Make sure the body text is well-formatted and that newline and carriage-return characters are correctly present and preserved in the message body.

    Required JSON output
    --------------------
    {{
    "triage_status": "AUTOMATIC" or "END_CONVERSATION",
    "triage_reason": "<reason if END_CONVERSATION; otherwise null>",
    "response_action_to_take": "one of {allowed_actions}",
    "response_message": "<the reply body if response_action_to_take is SEND_REPLY or SCHEDULE_MEETING; otherwise empty>"
    }}
    """

    # Decide if we use a vector store
    if (
        cleaned_context.external_known_data 
        and cleaned_context.external_known_data.external_openai_vector_store_id
    ):
        initial_response, status = await get_structured_output_with_assistant_and_vector_store(
            prompt=prompt,
            response_format=LinkedInTriageResponse,
            model="gpt-4.1",
            vector_store_id=cleaned_context.external_known_data.external_openai_vector_store_id,
            tool_config=tool_config,
            use_cache=linkedin_context.message_instructions.use_cache if linkedin_context.message_instructions else True
        )
    else:
        initial_response, status = await get_structured_output_internal(
            prompt,
            LinkedInTriageResponse,
            model="gpt-4.1",
            tool_config=tool_config,
            use_cache=linkedin_context.message_instructions.use_cache if linkedin_context.message_instructions else True
        )

    if status != 'SUCCESS':
        raise Exception("Error in generating the triaged LinkedIn message.")
    
    response_item = MessageItem(
        message_id="",  # or generate one if appropriate
        thread_id="",
        sender_name=linkedin_context.sender_info.sender_full_name or "",
        sender_email=linkedin_context.sender_info.sender_email or "",
        receiver_name=linkedin_context.lead_info.full_name or "",
        receiver_email=linkedin_context.lead_info.email or "",
        iso_datetime=datetime.datetime.utcnow().isoformat(),
        subject="",  # or set a triage subject if needed
        body=initial_response.response_message
    )

    # Build a MessageResponse that includes triage metadata plus your message item
    response_message = MessageResponse(
        triage_status=initial_response.triage_status,
        triage_reason=initial_response.triage_reason,
        message_item=response_item,
        response_action_to_take=initial_response.response_action_to_take
    )
    return response_message.model_dump()


# ---------------------------------------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------------------------------------
@assistant_tool
async def get_linkedin_response_message_variations(
    linkedin_context: ContentGenerationContext,
    number_of_variations: int = 3,
    tool_config: Optional[List[Dict]] = None
) -> List[Dict[str, Any]]:
    """
    Generates multiple variations of a triaged LinkedIn message and returns them all.
    Each variation is a dict conforming to LinkedInTriageResponse with keys:
        - triage_status
        - triage_reason
        - response_action_to_take
        - response_message
    """
    variation_specs = [
        "Friendly, short response with empathetic tone.",
        "Direct response referencing user’s last message or question.",
        "Meeting-oriented approach if the user seems interested in a deeper discussion.",
        "Longer, more detailed approach – reference relevant success stories or context.",
        "Minimalistic approach focusing on primary CTA only."
    ]

    # Check if the user provided custom instructions
    message_instructions = linkedin_context.message_instructions or MessageGenerationInstructions()
    user_instructions = (message_instructions.instructions_to_generate_message or "").strip()
    user_instructions_exist = bool(user_instructions)

    triaged_responses = []
    for i in range(number_of_variations):
        try:
            # If user has instructions, use those for every variation
            if user_instructions_exist:
                variation_style = user_instructions
            else:
                # Otherwise, fallback to variation_specs
                variation_style = variation_specs[i % len(variation_specs)]

            triaged_response = await generate_linkedin_response_message_copy(
                linkedin_context=linkedin_context,
                variation=variation_style,
                tool_config=tool_config
            )
            triaged_responses.append(triaged_response)
        except Exception as e:
            # You may want to log or handle the error
            raise e

    return triaged_responses
