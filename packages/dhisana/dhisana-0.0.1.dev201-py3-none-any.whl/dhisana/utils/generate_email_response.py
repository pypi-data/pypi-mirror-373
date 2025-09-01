import datetime
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
from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.generate_structured_output_internal import (
    get_structured_output_with_assistant_and_vector_store,
    get_structured_output_internal
)

# ---------------------------------------------------------------------------------------
# MODEL
# ---------------------------------------------------------------------------------------
class InboundEmailTriageResponse(BaseModel):
    """
    Model representing the structured response for an inbound email triage.
    - triage_status: "AUTOMATIC" or "END_CONVERSATION"
    - triage_reason: Reason text if triage_status == "END_CONVERSATION"
    - response_action_to_take: The recommended next action (e.g. SCHEDULE_MEETING, SEND_REPLY, etc.)
    - response_message: The actual body of the email response to be sent or used for approval.
    """
    triage_status: str  # "AUTOMATIC" or "END_CONVERSATION"
    triage_reason: Optional[str]
    response_action_to_take: str
    response_message: Optional[str]
    meeting_offer_sent: Optional[bool]


# ---------------------------------------------------------------------------------------
# HELPER FUNCTION TO CLEAN CONTEXT
# ---------------------------------------------------------------------------------------
def cleanup_reply_campaign_context(campaign_context: ContentGenerationContext) -> ContentGenerationContext:
    clone_context = campaign_context.copy(deep=True)
    if clone_context.lead_info is not None:
        clone_context.lead_info.task_ids = None
        clone_context.lead_info.email_validation_status = None
        clone_context.lead_info.linkedin_validation_status = None
        clone_context.lead_info.research_status = None
        clone_context.lead_info.enchrichment_status = None
    return clone_context


# ---------------------------------------------------------------------------------------
# GET INBOUND EMAIL TRIAGE ACTION (NO EMAIL TEXT)
# ---------------------------------------------------------------------------------------
async def get_inbound_email_triage_action(
    context: ContentGenerationContext,
    tool_config: Optional[List[Dict]] = None
) -> InboundEmailTriageResponse:
    """
    Analyzes the inbound email thread, and triage guidelines
    to determine triage status, reason, and the recommended action to take.
    DOES NOT generate the final email text.
    """
    allowed_actions = [
        "UNSUBSCRIBE",
        "NOT_INTERESTED",
        "SCHEDULE_MEETING",
        "SEND_REPLY",
        "OOF_MESSAGE",
        "NEED_MORE_INFO",
        "FORWARD_TO_OTHER_USER",
        "NO_MORE_IN_ORGANIZATION",
        "OBJECTION_RAISED",
        "END_CONVERSATION",
    ]
    current_date_iso = datetime.datetime.now().isoformat()
    cleaned_context = cleanup_reply_campaign_context(context)
    if not cleaned_context.current_conversation_context.current_email_thread:
        cleaned_context.current_conversation_context.current_email_thread = []
    
    if not cleaned_context.campaign_context.email_triage_guidelines:
        cleaned_context.campaign_context.email_triage_guidelines = "No specific guidelines provided."

    triage_prompt = f"""
        You are a specialized email assistant.                          
        Your task is to analyze the inbound email thread and the triage
        guidelines below to determine the correct triage action.

        allowed_actions = 
        {allowed_actions}

        1. Email thread or conversation:
        {[thread_item.model_dump() for thread_item in cleaned_context.current_conversation_context.current_email_thread]}

        2. Triage Guidelines
        -----------------------------------------------------------------
        General flow
        ------------
        • If the request is routine, non-sensitive, and clearly actionable  
        → **triage_status = "AUTOMATIC"**.  
        • If the thread contains PII, legal, NSFW, or any sensitive content  
        → **triage_status = "END_CONVERSATION"** and set a short **triage_reason**.

        Meeting & next-step logic
        -------------------------
        • Define `meeting_offer_sent` = **true** if **any** prior assistant
        message in the current thread proposed a call or meeting.

        • **First positive but non-committal reply**  
        (e.g. “Thanks”, “Sounds good”, “Will review”) **AND**
        `meeting_offer_sent` is **false**  
        → **SEND_REPLY** asking for a 15-min call, ≤ 150 words, friendly tone.  

        • **Second non-committal reply** or “Will get back” **after**
        `meeting_offer_sent` already true  
        → **END_CONVERSATION** (stop the thread unless the prospect re-engages).

        • If the prospect explicitly **asks for times / suggests times /
        requests your scheduling link**  
        → **SCHEDULE_MEETING** and include a concise reply that
        (a) confirms time or provides link,  
        (b) thanks them, and  
        (c) ends with a forward-looking statement.

        Handling interest & objections
        ------------------------------
        • If the prospect asks for **pricing, docs, case studies, or more info**  
        → **NEED_MORE_INFO** and craft a short response that promises to send
            the material (or includes it if ≤ 150 words fits).

        • If they mention **budget, timing, or competitor concerns**  
        → **OBJECTION_RAISED** and reply with a brief acknowledgement
            + single clarifying question or value statement.

        • If they request to loop in a colleague (“Please include Sarah”)  
        → **FORWARD_TO_OTHER_USER** and draft a one-liner tee-up.

        Priority order for immediate triage
        -----------------------------------
        1. “Unsubscribe”, “Remove me”, CAN-SPAM language → **UNSUBSCRIBE**  
        2. Explicit lack of interest → **NOT_INTERESTED**  
        3. Auto OOO / vacation responder → **OOF_MESSAGE**  
        4. Explicit request to meet / suggested times → **SCHEDULE_MEETING**  
        5. Prospect asks questions or raises objection → as per rules above  
        6. Apply “Meeting & next-step logic”  
        7. Default → **END_CONVERSATION**

        Reply style (when SEND_REPLY or SCHEDULE_MEETING)
        -------------------------------------------------
        • Max 150 words, clear single CTA, no jargon.  
        • Start with a thank-you, mirror the prospect’s language briefly, then
        propose next step or answer question.  
        
        If you have not proposed a meeting even once in the thread, and the user response is polite acknowledgment then you MUST request for a meeting.
         
        • Meeting ask template (use *exact* placeholder, will be filled later):
        Hi {{first_name}}, would you be open to a quick 15-min call to
        understand your use-case and share notes?

        • Competitor-stack mention template:
        Hi {{first_name}}, thanks for sharing your current stack. Would you be
        open to a 15-min call to explore where we can add value?
        
       

        Custom triage guidelines provided by the user. This takes precedence over above guidelines:
        {cleaned_context.campaign_context.email_triage_guidelines}
        
        Guard-rails
        -----------
        • Only one unsolicited follow-up per thread. If no response, stop.  
        • Never disclose PII/financial data; instead **END_CONVERSATION**.  
        • Stay friendly, concise, and on topic.


        Required JSON output
        --------------------
        {{
        "triage_status": "...",
        "triage_reason": null or "<reason>",
        "response_action_to_take": "one of {allowed_actions}",
        "response_message": "<only if SEND_REPLY/SCHEDULE_MEETING, else empty>"
        }}

        Current date is: {current_date_iso}.
        -----------------------------------------------------------------
        """


    # If there's a vector store ID, use that approach
    if (
        cleaned_context.external_known_data
        and cleaned_context.external_known_data.external_openai_vector_store_id
    ):
        triage_only, status = await get_structured_output_with_assistant_and_vector_store(
            prompt=triage_prompt,
            response_format=InboundEmailTriageResponse,
            model="gpt-4.1",
            vector_store_id=cleaned_context.external_known_data.external_openai_vector_store_id,
            tool_config=tool_config,
            use_cache=cleaned_context.message_instructions.use_cache if cleaned_context.message_instructions else True
        )
    else:
        triage_only, status = await get_structured_output_internal(
            prompt=triage_prompt,
            response_format=InboundEmailTriageResponse,
            model="gpt-4.1",
            tool_config=tool_config,
            use_cache=cleaned_context.message_instructions.use_cache if cleaned_context.message_instructions else True
        )

    if status != "SUCCESS":
        raise Exception("Error in generating triage action.")
    return triage_only


# ---------------------------------------------------------------------------------------
# CORE FUNCTION TO GENERATE SINGLE RESPONSE (ONE VARIATION)
# ---------------------------------------------------------------------------------------
async def generate_inbound_email_response_copy(
    campaign_context: ContentGenerationContext,
    variation: str,
    tool_config: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Generate a single inbound email triage response based on the provided context and
    a specific variation prompt.
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
        "END_CONVERSATION",
    ]
    current_date_iso = datetime.datetime.now().isoformat()
    cleaned_context = cleanup_reply_campaign_context(campaign_context)
    if not cleaned_context.current_conversation_context.current_email_thread:
        cleaned_context.current_conversation_context.current_email_thread = []
    
    lead_data = cleaned_context.lead_info or Lead()
    sender_data = cleaned_context.sender_info or SenderInfo()

    prompt = f"""
        You are a specialized email assistant. 
        Your task is to analyze the user's email thread, the user/company info,
        and the provided triage guidelines to craft an appropriate response.

        Follow these instructions to generate the reply: 
        {variation}

        1. Email thread or conversation to respond to:
        {[thread_item.model_dump() for thread_item in cleaned_context.current_conversation_context.current_email_thread] 
            if cleaned_context.current_conversation_context.current_email_thread else []}

        2)  Lead Information:
            {lead_data.dict()}

            Sender Information:
            Full Name: {sender_data.sender_full_name or ''}
            First Name: {sender_data.sender_first_name or ''}
            Last Name: {sender_data.sender_last_name or ''}
            Bio: {sender_data.sender_bio or ''}
        

        3. Campaign-specific triage guidelines (user overrides always win):
        {cleaned_context.campaign_context.email_triage_guidelines}

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
        • Never contradict, trash-talk, or disparage {campaign_context.lead_info.organization_name}.  
        • Plain-text only – NO HTML tags (<a>, <b>, <i>, etc.).  
        • If a link already exists in the inbound email, include it verbatim—do not re-wrap or shorten.

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
    If there is a link provided in the email, use it as is; do not wrap it in any HTML tags.
    DO NOT make up information. Use only the information provided in the context and instructions.
    Do NOT repeat the same message sent to the user in the past.
    Keep the thread conversational and friendly as a good account executive would respond.
    Do NOT rehash/repeat the same previous message already sent. Keep the reply to the point.
    DO NOT try to spam users with multiple messages. 
    Current date is: {current_date_iso}.
    DO NOT share any link to internal or made up document. You can attach or send any document.
    If the user is asking for any additional document END_CONVERSATION and let Account executive handle it.
    - Make sure the body text is well-formatted and that newline and carriage-return characters are correctly present and preserved in the message body.

    Required JSON output
    --------------------
    {{
    "triage_status": "AUTOMATIC" or "END_CONVERSATION",
    "triage_reason": "<reason if END_CONVERSATION; otherwise null>",
    "response_action_to_take": "one of {allowed_actions}",
    "response_message": "<the reply body if response_action_to_take is SEND_REPLY or SCHEDULE_MEETING; otherwise empty>"
    }}

    Current date is: {current_date_iso}.
    -----------------------------------------------------------------
    """


    # If there's a vector store ID, use that approach
    if (
        cleaned_context.external_known_data
        and cleaned_context.external_known_data.external_openai_vector_store_id
    ):
        initial_response, status = await get_structured_output_with_assistant_and_vector_store(
            prompt=prompt,
            response_format=InboundEmailTriageResponse,
            model="gpt-4.1",
            vector_store_id=cleaned_context.external_known_data.external_openai_vector_store_id,
            tool_config=tool_config
        )
    else:
        initial_response, status = await get_structured_output_internal(
            prompt=prompt,
            response_format=InboundEmailTriageResponse,
            model="gpt-4.1",
            tool_config=tool_config
        )

    if status != "SUCCESS":
        raise Exception("Error in generating the inbound email triage response.")

    response_item = MessageItem(
        message_id="",  # or generate one if appropriate
        thread_id="",
        sender_name=campaign_context.sender_info.sender_full_name or "",
        sender_email=campaign_context.sender_info.sender_email or "",
        receiver_name=campaign_context.lead_info.full_name or "",
        receiver_email=campaign_context.lead_info.email or "",
        iso_datetime=datetime.datetime.utcnow().isoformat(),
        subject="",  # or set some triage subject if needed
        body=initial_response.response_message
    )

    # Build a MessageResponse that includes triage metadata plus your message item
    response_message = MessageResponse(
        triage_status=initial_response.triage_status,
        triage_reason=initial_response.triage_reason,
        message_item=response_item,
        response_action_to_take=initial_response.response_action_to_take
    )
    print(response_message.model_dump())
    return response_message.model_dump()


# ---------------------------------------------------------------------------------------
# MAIN ENTRY POINT - GENERATE MULTIPLE VARIATIONS
# ---------------------------------------------------------------------------------------
@assistant_tool
async def generate_inbound_email_response_variations(
    campaign_context: ContentGenerationContext,
    number_of_variations: int = 3,
    tool_config: Optional[List[Dict]] = None
) -> List[Dict[str, Any]]:
    """
    Generate multiple inbound email triage responses, each with a different 'variation'
    unless user instructions are provided. Returns a list of dictionaries conforming
    to InboundEmailTriageResponse.
    """
    # Default variation frameworks
    variation_specs = [
        "Short and friendly response focusing on quick resolution.",
        "More formal tone referencing user’s key points in the thread.",
        "Meeting-based approach if user needs further discussion or demo.",
        "Lean approach focusing on clarifying user’s questions or concerns.",
        "Solution-driven approach referencing a relevant product or case study."
    ]

    # Check if the user provided custom instructions
    message_instructions = campaign_context.message_instructions or MessageGenerationInstructions()
    user_instructions = (message_instructions.instructions_to_generate_message or "").strip()
    user_instructions_exist = bool(user_instructions)

    all_variations = []
    for i in range(number_of_variations):
        # If user instructions exist, use them for every variation
        if user_instructions_exist:
            variation_text = user_instructions
        else:
            # Otherwise, fallback to variation_specs
            variation_text = variation_specs[i % len(variation_specs)]

        try:
            triaged_response = await generate_inbound_email_response_copy(
                campaign_context=campaign_context,
                variation=variation_text,
                tool_config=tool_config
            )
            all_variations.append(triaged_response)
        except Exception as e:
            raise e

    return all_variations
