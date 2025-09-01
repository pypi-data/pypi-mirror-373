from typing import Dict, List, Optional
from dhisana.schemas.sales import ChannelType, ContentGenerationContext
from dhisana.utils.generate_email_response import generate_inbound_email_response_variations
from dhisana.utils.generate_linkedin_connect_message import generate_personalized_linkedin_message
from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.generate_email import generate_personalized_email
from dhisana.utils.generate_linkedin_response_message import get_linkedin_response_message_variations


@assistant_tool
async def generate_content(
    generation_context: ContentGenerationContext,
    number_of_variations: int = 3,
    tool_config: Optional[List[Dict]] = None
):
    """
    Generate a personalized message using provided lead and campaign information.

    Parameters:
        generation_context (ContentGenerationContext): Info about the lead/campaign.
        number_of_variations (int): Number of variations to generate.
        tool_config (Optional[List[Dict]]): Configuration for the tool (default is None).

    Returns:
        List[dict]: The JSON response containing the subject/body or relevant content.

    Raises:
        ValueError: If target channel type is invalid.
    """
    if generation_context.target_channel_type == ChannelType.NEW_EMAIL.value:
        return await generate_personalized_email(generation_context, number_of_variations, tool_config)
    elif generation_context.target_channel_type == ChannelType.LINKEDIN_CONNECT_MESSAGE.value:
        return await generate_personalized_linkedin_message(generation_context, number_of_variations, tool_config)
    elif generation_context.target_channel_type == ChannelType.REPLY_EMAIL.value:
        return await generate_inbound_email_response_variations(generation_context, number_of_variations, tool_config)
    elif generation_context.target_channel_type == ChannelType.LINKEDIN_USER_MESSAGE.value:
        return await get_linkedin_response_message_variations(generation_context, number_of_variations, tool_config)
    else:
        raise ValueError("Invalid target channel type.")