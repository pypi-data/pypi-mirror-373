# Import necessary modules
from typing import Dict, List, Optional
from pydantic import BaseModel

from dhisana.schemas.sales import CampaignContext, ContentGenerationContext, ConversationContext, Lead, MessageGenerationInstructions, MessageItem, SenderInfo
from dhisana.utils.generate_structured_output_internal import (
    get_structured_output_internal,
    get_structured_output_with_assistant_and_vector_store
)
from datetime import datetime
from pydantic import BaseModel, ConfigDict

# -----------------------------------------------------------------------------
# Email Copy schema
# -----------------------------------------------------------------------------
class EmailCopy(BaseModel):
    subject: str
    body: str
 
    model_config = ConfigDict(extra="forbid")

# -----------------------------------------------------------------------------
# Utility to Clean Up Context (if needed)
# -----------------------------------------------------------------------------
def cleanup_email_context(email_context: ContentGenerationContext) -> ContentGenerationContext:
    """
    Return a copy of ContentGenerationContext without sensitive or irrelevant fields.
    Modify or remove fields as necessary for your project.
    """
    clone_context = email_context.copy(deep=True)
    # For demonstration, no sensitive fields in new classes by default.
    # Adjust if you want to remove certain fields (like 'sender_bio', etc.).
    if clone_context.external_known_data:
        clone_context.external_known_data.external_openai_vector_store_id = None
    return clone_context

# -----------------------------------------------------------------------------
# Known Framework Variations (fallback if user instructions are not provided)
# -----------------------------------------------------------------------------
FRAMEWORK_VARIATIONS = [
    "Use PAS (Problem, Agitate, Solve) framework to write up the email.",
    "Use VETO framework (Value, Evidence, Tie, Offer). Highlight how our product addresses the company's current goals.",
    "Use AIDA framework (Attention, Interest, Desire, Action) to compose the email.",
    "Use SPIN (Situation, Problem, Implication, Need-Payoff) framework to write the email.",
    "Use BANT (Budget, Authority, Need, Timeline) framework to write the email.",
    "Use P-S-B (Pain, Solution, Benefit) with a 3-Bullet Approach. Keep it concise.",
    "Use Hook, Insight, Offer framework to write the email."
]

# -----------------------------------------------------------------------------
# Core function to generate an email copy
# -----------------------------------------------------------------------------
async def generate_personalized_email_copy(
    email_context: ContentGenerationContext,
    message_instructions: MessageGenerationInstructions,
    variation_text: str,
    tool_config: Optional[List[Dict]] = None,
) -> dict:
    """
    Generate a personalized email using the provided context and instructions.

    Steps:
      1. Build a prompt referencing 6 main info:
          (a) Lead Info
          (b) Sender Info
          (c) Campaign Info
          (d) Messaging Instructions
          (e) Additional Data (vector store) if any
          (f) Current Conversation Context
      2. Generate an initial draft with or without vector store usage.
      3. Optionally refine if a vector store was used and user instructions were not provided.
      4. Return the final subject & body.
    """
    cleaned_context = cleanup_email_context(email_context)

    # Check if user provided custom instructions
    user_custom_instructions = (message_instructions.instructions_to_generate_message or "").strip()
    use_custom_instructions = bool(user_custom_instructions)

    # Decide final instructions: user-provided or fallback variation
    if use_custom_instructions:
        selected_instructions = user_custom_instructions
    else:
        selected_instructions = variation_text

    # Pull out fields or fallback to empty if None
    lead_data = cleaned_context.lead_info or Lead()
    sender_data = cleaned_context.sender_info or SenderInfo()
    campaign_data = cleaned_context.campaign_context or CampaignContext()
    conversation_data = cleaned_context.current_conversation_context or ConversationContext()

    # Construct the consolidated prompt
    initial_prompt = f"""
        Hi AI Assistant,

        Below is the context in 6 main sections. Use it to craft a concise, professional email:

        1) Lead Information:
        {lead_data.dict()}

        2) Sender Information:
        Full Name: {sender_data.sender_full_name or ''}
        First Name: {sender_data.sender_first_name or ''}
        Last Name: {sender_data.sender_last_name or ''}
        Bio: {sender_data.sender_bio or ''}

        3) Campaign Information:
        Product Name: {campaign_data.product_name or ''}
        Value Proposition: {campaign_data.value_prop or ''}
        Call To Action: {campaign_data.call_to_action or ''}
        Pain Points: {campaign_data.pain_points or []}
        Proof Points: {campaign_data.proof_points or []}
        Triage Guidelines (Email): {campaign_data.email_triage_guidelines or ''}
        Triage Guidelines (LinkedIn): {campaign_data.linkedin_triage_guidelines or ''}

        4) Messaging Instructions (template/framework):
        {selected_instructions}

        5) External Data / Vector Store:
        (I will be provided with file_search tool if present.)

        6) Current Conversation Context:
        Email Thread: {conversation_data.current_email_thread or ''}
        LinkedIn Thread: {conversation_data.current_linkedin_thread or ''}

        IMPORTANT REQUIREMENTS:
        - Output must be JSON with "subject" and "body" fields only.
        - In the subject or body DO NOT include any HTML tags like <a>, <b>, <i>, etc.
        - The body and subject should be in plain text.
        - If there is a link provided in email use it as is. dont wrap it in any HTML tags.
        - Keep it concise and relevant. No placeholders or extra instructions.
        - Do not include PII or internal references, guids or content identifiers in the email.
        - User conversational name for company name if used.
        - Email has saluation Hi <First Name>, unless otherwise specified.
        - <First Name> is the first name of the lead. Its conversational name. It does not have any special characters or spaces.
        - Make sure the signature in body has the sender_first_name is correct and in the format user has specified.
        - Do Not Make up information. use the information provided in the context and instructions only.
        - Make sure the body text is well-formatted and that newline and carriage-return characters are correctly present and preserved in the message body.
        
    """

    # Check if a vector store is available
    vector_store_id = (email_context.external_known_data.external_openai_vector_store_id
                       if email_context.external_known_data else None)

    initial_response = None
    initial_status = ""

    # Generate initial draft
    if vector_store_id:
        initial_response, initial_status = await get_structured_output_with_assistant_and_vector_store(
            prompt=initial_prompt,
            response_format=EmailCopy,
            vector_store_id=vector_store_id,
            model="gpt-4.1",
            tool_config=tool_config,
            use_cache=email_context.message_instructions.use_cache if email_context.message_instructions else True
        )
    else:
        # Otherwise, generate the initial draft internally
        initial_response, initial_status = await get_structured_output_internal(
            prompt=initial_prompt,
            response_format=EmailCopy,
            model="gpt-4.1",
            tool_config=tool_config,
            use_cache=email_context.message_instructions.use_cache if email_context.message_instructions else True
        )

    if initial_status != "SUCCESS":
        raise Exception("Error: Could not generate initial draft for the personalized email.")
    response_item = MessageItem(
        message_id="",  # or some real ID if you have it
        thread_id="",
        sender_name=email_context.sender_info.sender_full_name or "",
        sender_email=email_context.sender_info.sender_email or "",
        receiver_name=email_context.lead_info.full_name or "",
        receiver_email=email_context.lead_info.email or "",
        iso_datetime=datetime.utcnow().isoformat(),
        subject=initial_response.subject,
        body=initial_response.body
    )
    return response_item.model_dump()

# -----------------------------------------------------------------------------
# Primary function to generate multiple variations
# -----------------------------------------------------------------------------
async def generate_personalized_email(
    generation_context: ContentGenerationContext,
    number_of_variations: int = 3,
    tool_config: Optional[List[Dict]] = None
) -> List[dict]:
    """
    Generates multiple personalized email variations based on the given context and instructions.

    Parameters:
        - email_context: The consolidated context for email generation.
        - message_instructions: User-supplied instructions or templates for generating the message.
        - number_of_variations: How many email variations to produce.
        - tool_config: Optional tool configuration for the LLM calls.

    Returns:
        A list of dictionaries, each containing:
          {
            "subject": "string",
            "body": "string"
          }
    """
    email_variations = []
    message_instructions = generation_context.message_instructions 
    user_instructions_exist = bool(
        (message_instructions.instructions_to_generate_message or "").strip()
    )

    for i in range(number_of_variations):
        try:
            # If user provided instructions, use them for each variation
            # (skip the internal frameworks).
            if user_instructions_exist:
                variation_text = message_instructions.instructions_to_generate_message or ""
            else:
                # Otherwise, pick from known frameworks (circular indexing)
                variation_text = FRAMEWORK_VARIATIONS[i % len(FRAMEWORK_VARIATIONS)]

            email_copy = await generate_personalized_email_copy(
                email_context=generation_context,
                message_instructions=message_instructions,
                variation_text=variation_text,
                tool_config=tool_config
            )
            email_variations.append(email_copy)

        except Exception as e:
            raise e
    return email_variations
