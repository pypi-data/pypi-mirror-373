from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from enum import Enum
from typing import Optional, List, Dict, Literal


# -----------------------------
# Lead-List-Specific Schemas
# -----------------------------

class Lead(BaseModel):
    id: Optional[str] = None
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    user_linkedin_url: Optional[str] = None
    user_linkedin_salesnav_url: Optional[str] = None
    primary_domain_of_organization: Optional[str] = None
    job_title: Optional[str] = None
    phone: Optional[str] = None
    headline: Optional[str] = None
    lead_location: Optional[str] = None
    organization_name: Optional[str] = None
    organization_website: Optional[str] = None
    summary_about_lead: Optional[str] = None
    workflow_stage: Optional[str] = None
    assigned_to: Optional[str] = None
    engaged: Optional[bool] = None
    last_contact: Optional[int] = None
    additional_properties: Optional[Dict[str, Any]] = None
    research_summary: Optional[str] = None
    task_ids: Optional[List[str]] = None
    email_validation_status: Optional[
        Literal["not_started", "in_progress", "valid", "invalid"]
    ] = None
    linkedin_validation_status: Optional[
        Literal["not_started", "in_progress", "valid", "invalid"]
    ] = None
    research_status: Optional[
        Literal["not_started", "in_progress", "done", "failed"]
    ] = None
    enchrichment_status: Optional[
        Literal["not_started", "in_progress", "done", "failed"]
    ] = None

    @field_validator(
        "linkedin_validation_status",
        "email_validation_status",
        "research_status",
        "enchrichment_status",
        mode="before"
    )
    @classmethod
    def empty_string_to_none(cls, v):
        return None if v == "" else v


class LeadList(BaseModel):
    id: Optional[str] = None
    name: str
    sources: List[str]
    tags: List[str]
    category: str
    leads_count: int
    assigned_users: List[str]
    updated_at: int
    status: Literal["connected", "disconnected", "coming soon"]
    leads: Optional[List[Lead]] = None
    public: Optional[bool] = None

# -----------------------------
# Task-Specific Schemas
# -----------------------------

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"

class TaskBase(BaseModel):
    name: str
    task_type: str
    data_id: Optional[UUID] = None
    data_type: Optional[str] = None

    inputs: Optional[List[Dict[str, Any]]] = []
    outputs: Optional[List[Dict[str, Any]]] = []

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    logs: Optional[List[Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    outputs: Optional[List[Dict[str, Any]]] = None

class Task(TaskBase):
    id: UUID
    status: TaskStatus
    logs: List[Any] = []
    metrics: Dict[str, Any] = {}
    created_at: int                 # store as ms since epoch
    updated_at: int
    completed_at: Optional[int] = None

    class Config:
        from_attributes = True


# -----------------------------
# Campaign-Specific Schemas
# -----------------------------

class SendRules(BaseModel):
    daily_send_limit: Optional[int] = None
    concurrency_limit: Optional[int] = None
    time_window_start: Optional[str] = None  # "HH:MM" string
    time_window_end: Optional[str] = None
    block_weekends: Optional[bool] = False

class Touch(BaseModel):
    type: str            # e.g. 'email', 'linkedin', ...
    action: str          # e.g. 'view_linkedin_profile', 'send_connection_request'
    details: str
    delay_days: int
    template_id: Optional[str] = None

class PromptEngineeringGuidance(BaseModel):
    tone: str
    word_count: int
    paragraphs: int

class LeadLog(BaseModel):
    id: Optional[str] = None
    message: str
    channel: Optional[str] = None
    timestamp: int                   # ms since epoch
    status: Optional[str] = None

class CampaignLead(BaseModel):
    id: Optional[str] = None
    campaign_id: str
    lead_list_id: Optional[str] = None
    lead_id: Optional[str] = None
    lead_name: str

    status: Optional[str] = None  # 'PENDING', 'WAITING_APPROVAL', 'OUTBOUND_PENDING', 'COMPLETED'
    current_step: Optional[int] = 0
    total_steps: Optional[int] = 0
    engaged: Optional[bool] = False
    last_touch: Optional[str] = None
    created_at: Optional[int] = None      # ms since epoch
    updated_at: Optional[int] = None

    logs: Optional[List[LeadLog]] = None

class CampaignCounter(BaseModel):
    id: Optional[str] = None
    campaign_id: str
    date: str                 # "YYYY-MM-DD"
    daily_sends: int
    current_concurrency: int

class CampaignStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"

class PendingEvent(BaseModel):
    event_id: str
    lead_id: str
    touch_index: int
    channel: str
    action: str
    subject: str
    message: str
    created_at: int             # ms since epoch

class Campaign(BaseModel):
    id: str
    name: str
    description: str
    lead_lists: List[str]
    run_mode: str
    updated_at: int                       # ms since epoch

    tags: Optional[List[str]] = None
    channel: Optional[str] = None
    mission_objective: Optional[str] = None
    mission_progress: Optional[int] = None
    ai_alerts: Optional[List[str]] = None
    automatic_adjustments: Optional[List[str]] = None

    product_name: Optional[str] = None
    value_prop: Optional[str] = None
    call_to_action: Optional[str] = None
    pain_points: Optional[List[str]] = None
    proof_points: Optional[List[str]] = None
    prompt_engineering_guidance: Optional[PromptEngineeringGuidance] = None
    prompt_templates: Optional[List[Dict[str, Any]]] = None
    touches: Optional[List[Touch]] = None
    send_rules: Optional[SendRules] = None

    status: Optional[CampaignStatus] = None
    start_date: Optional[int] = None      # ms since epoch
    pause_date: Optional[int] = None
    end_date: Optional[int] = None

    leads: Optional[List[CampaignLead]] = None
    counter: Optional[CampaignCounter] = None
    pending_events: Optional[List[PendingEvent]] = None

    class Config:
        from_attributes = True

# ---------------------------------------------------------------------
# New Classes with Comments
# ---------------------------------------------------------------------
class ChannelType(str, Enum):
    """
    Enumerates the different communication channels.
    """
    NEW_EMAIL = "new_email"
    LINKEDIN_CONNECT_MESSAGE = "linkedin_connect_message"
    REPLY_EMAIL = "reply_email"
    LINKEDIN_USER_MESSAGE = "linkedin_user_message"

class SenderInfo(BaseModel):
    """
    Holds information about the sender:
      - sender_full_name: Full name of the sender.
      - sender_first_name: Sender's first name.
      - sender_last_name: Sender's last name.
      - sender_bio: Optional biography or short description of the sender.
    """
    sender_full_name: Optional[str] = None
    sender_first_name: Optional[str] = None
    sender_last_name: Optional[str] = None
    sender_email: Optional[str] = None
    sender_bio: Optional[str] = None


class MessageGenerationInstructions(BaseModel):
    """
    Holds the user-supplied instructions for generating the message:
      - instructions_to_generate_message: Plain text or template instructions from the user.
      - prompt_engineering_guidance: (Optional) Extra guidelines for structuring the prompt.
    """
    instructions_to_generate_message: Optional[str] = None
    prompt_engineering_guidance: Optional[PromptEngineeringGuidance] = None
    use_cache: Optional[bool] = True

class CampaignContext(BaseModel):
    """
    Represents the context of the campaign or marketing effort:
      - product_name: Name of the product or service.
      - value_prop: Value proposition of the product.
      - call_to_action: Suggested CTA for the user to take.
      - pain_points: List of known pain points for the lead or market.
      - proof_points: List of proof points or social proof for the product.
      - email_triage_guidelines: Guidelines for triaging or responding to emails.
      - linkedin_triage_guidelines: Guidelines for triaging or responding to LinkedIn messages.
    """
    product_name: Optional[str] = None
    value_prop: Optional[str] = None
    call_to_action: Optional[str] = None
    pain_points: Optional[List[str]] = None
    proof_points: Optional[List[str]] = None
    email_triage_guidelines: Optional[str] = None
    linkedin_triage_guidelines: Optional[str] = None

    
class MessageItem(BaseModel):
    """
    Represents a single message item in a conversation.
    """
    message_id: str = Field(
        ...,
        description="Unique identifier for the message"
    )
    thread_id: str = Field(
        ...,
        description="Unique identifier for the conversation thread"
    )
    sender_name: str = Field(
        ...,
        description="Sender's display name (if available)"
    )
    sender_email: str = Field(
        ...,
        description="Sender's email address"
    )
    receiver_name: str = Field(
        ...,
        description="Comma-separated list of receiver names"
    )
    receiver_email: str = Field(
        ...,
        description="Comma-separated list of receiver emails"
    )
    iso_datetime: str = Field(
        ...,
        description="Date/time of the message in ISO 8601 format"
    )
    subject: str = Field(
        ...,
        description="Subject of the message"
    )
    body: str = Field(
        ...,
        description="Body of the message in plain text"
    )

class MessageResponse(BaseModel):
    """
    Model representing the structured response for a LinkedIn conversation triage.
    - triage_status: "AUTOMATIC" or "REQUIRES_APPROVAL"
    - triage_reason: Optional reason text if triage_status == "REQUIRES_APPROVAL"
    - response_action_to_take: The recommended next action (e.g., SEND_REPLY, WAIT_TO_SEND, STOP_SENDING, etc.)
    - message_item: The actual message to be sent or used for approval.
    """
    triage_status: str  # "AUTOMATIC" or "REQUIRES_APPROVAL"
    triage_reason: Optional[str]
    response_action_to_take: str
    message_item: MessageItem


class ConversationContext(BaseModel):
    """
    Contains the current conversation threads for email or LinkedIn:
      - current_email_thread: Existing email thread if any.
      - current_linkedin_thread: Existing LinkedIn thread if any.
    """
    current_email_thread: Optional[List[MessageItem]] = None
    current_linkedin_thread: Optional[List[MessageItem]] = None

class ExternalDataSources(BaseModel):
    """
    Holds references to external or third-party data integrations:
      - external_openai_vector_store_id: ID for a vector store used for context retrieval.
    """
    external_openai_vector_store_id: Optional[str] = None

class ContentGenerationContext(BaseModel):
    """
    Consolidates all relevant data needed for generating content:
      1) campaign_context: Details about the current campaign or marketing approach.
      2) lead_info: The lead's basic information.
      3) sender_info: Who is sending the message.
      4) external_known_data: Any references to external data sources (e.g., vector store IDs).
      5) current_conversation_context: Current or ongoing conversation threads (email or LinkedIn).
      6) target_channel_type: Which channel we are generating content for (email, LinkedIn, etc.).
    """
    campaign_context: Optional[CampaignContext] = None
    lead_info: Optional[Lead] = None
    sender_info: Optional[SenderInfo] = None
    external_known_data: Optional[ExternalDataSources] = None
    current_conversation_context: Optional[ConversationContext] = None
    target_channel_type: Optional[ChannelType] = None
    message_instructions: MessageGenerationInstructions = None


# -----------------------------
# TOUCHPOINT + EXECUTION
# -----------------------------
class TouchPointStatus(BaseModel):
    """
    Holds the dynamic state of each lead’s progress in the campaign.
    """
    is_connected_on_linkedin: bool
    first_introduction_message_sent: bool
    got_postive_response: bool
    got_negative_response: bool

    # Logging how many total messages or touches we’ve attempted.
    messages_sent: int

    # If the lead explicitly requested no further contact.
    did_opt_out: bool

    # Specific dispositions from the lead's response (e.g. "not_interested", "schedule_demo", etc.)
    response_disposition: Optional[str] = None

    # Maximum allowed attempts (touches)
    max_touch_points: int

    likely_to_engage_score: int

    # Date/time fields
    last_profile_viewed_date: Optional[str] = None
    last_linkedin_message_sent_date: Optional[str] = None
    last_email_sent_date: Optional[str] = None
    last_email_response_received_date: Optional[str] = None
    last_post_date: Optional[str] = None
    last_linkedin_message_received_date: Optional[str] = None

    # LinkedIn Connection fields
    connection_status: Optional[str] = None            # e.g., "connected", "pending"
    connection_request_sent_date: Optional[str] = None
    connection_degree: Optional[str] = None            # "1st", "2nd", or "3rd"

    # Additional fields we want to store
    sdr_user_id: Optional[str] = None
    user_linkedin_url: Optional[str] = None
    user_linkedin_salesnav_url: Optional[str] = None
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    location: Optional[str] = None
    is_past_colleague: Optional[bool] = None
    number_of_mutual_connections: Optional[int] = None
    organization_name: Optional[str] = None


class LeadCampaignExecutionContext(BaseModel):
    """
    This is the combined object passed to run_campaign_cadence_for_lead.
    """
    campaign_context: Optional[CampaignContext] = None
    lead_info: Optional[Lead] = None
    sender_info: Optional[SenderInfo] = None
    external_known_data: Optional[ExternalDataSources] = None
    current_conversation_context: Optional[ConversationContext] = None
    message_instructions: MessageGenerationInstructions = MessageGenerationInstructions()
    touchpoint_status: Optional[TouchPointStatus] = None
    current_user_id: Optional[str] = None
    custom_instructions_for_cadence: Optional[str] = None


        
# --------------------------------------------------------------------
# 1. Define your HubSpotLeadInformation model
# --------------------------------------------------------------------
class HubSpotLeadInformation(BaseModel):
    full_name: str = Field("", description="Full name of the lead")
    first_name: str = Field("", description="First name of the lead")
    last_name: str = Field("", description="Last name of the lead")
    email: str = Field("", description="Email address of the lead")
    user_linkedin_url: str = Field("", description="LinkedIn URL of the lead")
    primary_domain_of_organization: str = Field("", description="Primary domain of the organization")
    job_title: str = Field("", description="Job Title of the lead")
    phone: str = Field("", description="Phone number of the lead")
    headline: str = Field("", description="Headline of the lead")
    lead_location: str = Field("", description="Location of the lead")
    organization_name: str = Field("", description="Current Company where lead works")
    organization_website: str = Field("", description="Current Company website of the lead")
    organization_linkedin_url : str = Field("", description="Company LinkedIn URL")
    additional_properties: Optional[Dict[str, Any]] = None

class HubSpotCompanyinformation(BaseModel):
    primary_domain_of_organization: str = Field("", description="Primary domain of the organization")
    organization_name: str = Field("", description="Current Company where lead works")
    organization_website: str = Field("", description="Current Company website of the lead")
    organization_linkedin_url : str = Field("", description="Company LinkedIn URL")
    additional_properties: Optional[Dict[str, Any]] = None


# --------------------------------------------------------------------
# 2. Map HubSpot property names -> HubSpotLeadInformation fields
# --------------------------------------------------------------------
HUBSPOT_TO_LEAD_MAPPING = {
    "firstname": "first_name",
    "lastname": "last_name",
    "email": "email",
    "phone": "phone",
    "jobtitle": "job_title",            # Default HubSpot job title property
    "company": "organization_name",     # Map "company" -> "organization_name"
    "website": "organization_website",  # Map "website" -> "organization_website"
    "address": "lead_location",         # You can choose "city", "state", etc. if you prefer
    "city": "lead_location",
    "domain": "primary_domain_of_organization",
    "hs_linkedin_url": "user_linkedin_url",
}

class SmartListStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"

class SmartListInputType(str, Enum):
    LEADS = "LEADS"
    ACCOUNTS = "ACCOUNTS"

class SmartListSourceType(str, Enum):
    SALES_NAVIGATOR = "SALES_NAVIGATOR"
    GOOGLE_SEARCH = "GOOGLE_SEARCH"
    HUBSPOT = "HUBSPOT"
    APOLLO = "APOLLO"
    CSV = "CSV"
    GOOGLE_SHEETS = "GOOGLE_SHEETS"
    CUSTOM_WEBSITE = "CUSTOM_WEBSITE"
    GITHUB = "GITHUB"
    ICP_SEARCH = "ICP_SEARCH"
    LOCAL_BUSINESS = "LOCAL_BUSINESS"
    GOOGLE_JOBS = "GOOGLE_JOBS"
    WEBHOOK = "WEBHOOK"
    GOOGLE_CUSTOM_SITE_SEARCH = "GOOGLE_CUSTOM_SITE_SEARCH"

class SourceConfiguration(BaseModel):
    """
    Defines configuration details for each source type.
    Depending on the source_type, only certain fields
    may be required or used.
    """
    # For Sales Navigator or Apollo or Google Search
    search_query: Optional[str] = None
    # For HubSpot
    list_id: Optional[str] = None
    list_name: Optional[str] = None
    # For CSV
    file_path: Optional[str] = None
    # For Google Sheets
    source_url: Optional[str] = None
    # For Github
    github_search_query: Optional[str] = None
    github_max_repos: Optional[int] = None
    github_max_contributors: Optional[int] = None
    
    # Custom website inputs 
    custom_instructions_for_doing_pagination: Optional[str] = None
    custom_instructions_for_data_extraction_from_page: Optional[str] = None
    custom_instruction_to_fetch_details_page: Optional[str] = None

class SmartListSource(BaseModel):
    """
    A single lead source definition. Contains the
    source type (e.g., 'SALES_NAVIGATOR') plus the
    relevant configuration.
    """
    source_type: SmartListSourceType
    input_type: SmartListInputType
    configuration: SourceConfiguration

class SmartList(BaseModel):
    id: Optional[UUID] = None
    name: Optional[str] = None
    description: Optional[str] = None    
    category: Optional[str] = None
    status: SmartListStatus = SmartListStatus.DRAFT
    start_date: Optional[int] = None
    end_date: Optional[int] = None

    sources: Optional[List[SmartListSource]] = None

    qualification_instructions: Optional[str] = None
    fetch_instructions: Optional[str] = None       
    max_items_to_search: Optional[int] = None
    max_items_in_qualified_results: Optional[int] = None
    enrich_information_from_online_research: bool = False
    enrich_information_from_lead_website: bool = False
    enrich_with_valid_email: bool = False
    enrich_with_phone_number: bool = False
    min_qualification_score: Optional[int] = None
    number_of_leads_per_company: Optional[int] = None

    agent_instance_id: Optional[UUID] = None
    organization_id: Optional[UUID] = None
    created_by: Optional[UUID] = None
    created_at: Optional[int] = None
    updated_by: Optional[UUID] = None
    updated_at: Optional[int] = None
    file_content: Optional[List[Any]] = None
    account_qualification_instructions: Optional[str] = None
    exclude_company_domains: Optional[List[Any]] = None
    exclude_leads: Optional[List[Any]] = None

    class Config:
        from_attributes = True

class SmartListLead(BaseModel):
    id: Optional[UUID] = None

    smart_list_id: Optional[UUID] = None

    full_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    user_linkedin_url: Optional[str] = None
    user_linkedin_salesnav_url: Optional[str] = None
    organization_linkedin_url: Optional[str] = None
    organization_linkedin_salesnav_url: Optional[str] = None
    primary_domain_of_organization: Optional[str] = None
    twitter_handle: Optional[str] = None
    github_handle: Optional[str] = None
    job_title: Optional[str] = None
    phone: Optional[str] = None
    headline: Optional[str] = None
    lead_location: Optional[str] = None
    organization_name: Optional[str] = None
    organization_website: Optional[str] = None
    summary_about_lead: Optional[str] = None
    keywords: Optional[Any] = None
    additional_properties: Optional[Dict[str, Any]] = None
    research_summary: Optional[str] = None

    qualification_score: Optional[float] = None
    qualification_reason: Optional[str] = None
    source: Optional[str] = None
    
    email_validation_status: Optional[str] = None
    linkedin_validation_status: Optional[str] = None
    research_status: Optional[str] = None
    enchrichment_status: Optional[str] = None

    agent_instance_id: Optional[UUID] = None
    organization_id: Optional[UUID] = None
    created_by: Optional[UUID] = None
    created_at: Optional[int] = None
    updated_by: Optional[UUID] = None
    updated_at: Optional[int] = None
    
    revenue: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    class Config:
        from_attributes = True


class SmartListLog(BaseModel):
    id: Optional[UUID] = None
    message: str

    smart_list_id: UUID

    agent_instance_id: Optional[UUID] = None
    organization_id: Optional[UUID] = None
    created_by: Optional[UUID] = None
    created_at: Optional[int] = None
    updated_by: Optional[UUID] = None
    updated_at: Optional[int] = None

    class Config:
        from_attributes = True

# --------------------------------------------------
# Updated LeadsQueryFilters
# --------------------------------------------------
class LeadsQueryFilters(BaseModel):
    """
    Defines the filter parameters for querying leads in the Apollo database.
    All fields are optional and default to None if not specified by user.
    """

    # CHANGED: Renamed field to be more descriptive (person's current job titles)
    person_current_titles: Optional[List[str]] = Field(
        default=None,
        description="List of job titles for the person (maps to Apollo's person_titles)."
    )

    # CHANGED: Renamed field to be more descriptive (person's locations)
    person_locations: Optional[List[str]] = Field(
        default=None,
        description="List of personal locations (city, state, country). Maps to person_locations in Apollo."
    )

    # CHANGED: Renamed to be more descriptive
    min_employees_in_organization: Optional[int] = Field(
        default=None,
        description="Minimum number of employees (>=1). Internally converted to a numeric range for Apollo."
    )
    max_employees_in_organization: Optional[int] = Field(
        default=None,
        description="Maximum number of employees (<=100000). Internally converted to a numeric range for Apollo."
    )

    filter_by_signals: Optional[List[str]] = Field(
        default=None,
        description="List of signals to filter by, e.g. ['RECENT_JOB_CHANGE']. Maps internally to search_signal_ids."
    )
    max_number_of_items_to_return: Optional[int] = Field(
        default=None,
        description="Max # of items (<=5000). Default=100."
    )

    # CHANGED: Renamed to be more descriptive
    industries: Optional[List[str]] = Field(
        default=None,
        description="List of organization industries. Maps to organization_industries in Apollo."
    )

    # Potential existing fields
    min_revenue_of_the_company: Optional[int] = Field(
        default=None,
        description="Minimum company revenue. Maps to revenueRange[min]."
    )
    max_revenue_of_the_company: Optional[int] = Field(
        default=None,
        description="Maximum company revenue. Maps to revenueRange[max]."
    )
    job_functions: Optional[List[str]] = Field(
        default=None,
        description="List of job functions (not directly used)."
    )

    # CHANGED: Renamed to be more descriptive
    search_keywords: Optional[str] = Field(
        default=None,
        description="A string of keywords to filter results. Maps to q_keywords in Apollo."
    )

    # CHANGED: Renamed to be more descriptive
    company_domains: Optional[List[str]] = Field(
        default=None,
        description="Domains of the person's employer (e.g., ['microsoft.com']). Maps to q_organization_domains."
    )

    # CHANGED: Renamed to be more descriptive
    company_hq_locations: Optional[List[str]] = Field(
        default=None,
        description="List of HQ locations for the employer. Maps to organization_locations."
    )

    contact_email_status: Optional[List[str]] = Field(
        default=None,
        description="Email statuses, e.g. ['verified', 'unavailable']. Maps to contact_email_status."
    )

    # CHANGED: Renamed to be more descriptive
    company_ids: Optional[List[str]] = Field(
        default=None,
        description="Apollo IDs for the companies (string IDs). Maps to organization_ids."
    )

    person_seniorities: Optional[List[str]] = Field(
        default=None,
        description=(
            "List of job seniorities, e.g. ['manager', 'director', 'vp']. "
            "Apollo supports: owner, founder, c_suite, partner, vp, head, "
            "director, manager, senior, entry, intern."
        )
    )

    # CHANGED: This replaces the old 'organization_job_titles' field
    job_openings_with_titles: Optional[List[str]] = Field(
        default=None,
        description="List of job titles for posted positions in the organization. Maps to q_organization_job_titles."
    )

    # CHANGED: We no longer expose organization_num_employee_ranges to the user;
    # we will build that internally from min_employees_in_organization & max_employees_in_organization.

    latest_funding_stages: Optional[List[str]] = Field(
        default=None,
        description="List of funding stage codes, e.g. ['2', '3', '10']. Maps to organization_latest_funding_stage_cd."
    )

    # CHANGED: Renamed for consistency
    company_industry_tag_ids: Optional[List[str]] = Field(
        default=None,
        description="List of industry tag IDs, e.g. ['5567cd4773696439b10b0000']. Maps to organization_industry_tag_ids."
    )

    q_organization_search_list_id: Optional[str] = Field(
        default=None,
        description="Include only organizations in a specific search list. Maps to qOrganizationSearchListId."
    )
    q_not_organization_search_list_id: Optional[str] = Field(
        default=None,
        description="Exclude organizations in a specific search list. Maps to qNotOrganizationSearchListId."
    )
    currently_using_any_of_technology_uids: Optional[List[str]] = Field(
        default=None,
        description="Technology UIDs used by the organization, e.g. ['google_font_api']."
    )
    sort_by_field: Optional[str] = Field(
        default=None,
        description="Sort field, e.g. '[none]', 'last_name', etc. Maps to sortByField."
    )
    sort_ascending: Optional[bool] = Field(
        default=None,
        description="Sort ascending or descending (maps to sortAscending)."
    )
    
    organization_num_employees_ranges: Optional[List[str]] = Field(
        default=None,
        description="Ranges for organization number of employees."
    )


class CompanyQueryFilters(BaseModel):
    """
    Defines the filter parameters for querying companies/organizations in the Apollo database.
    All fields are optional and default to None if not specified by user.
    """

    # Core company search parameters
    organization_locations: Optional[List[str]] = Field(
        default=None,
        description="List of organization headquarters locations (city, state, country)."
    )

    organization_num_employees_ranges: Optional[List[str]] = Field(
        default=None,
        description="Employee count ranges, e.g. ['1,10', '11,50', '51,200']. Use specific ranges."
    )

    min_employees: Optional[int] = Field(
        default=None,
        description="Minimum number of employees (>=1). Internally converted to a numeric range."
    )
    
    max_employees: Optional[int] = Field(
        default=None,
        description="Maximum number of employees (<=100000). Internally converted to a numeric range."
    )

    organization_industries: Optional[List[str]] = Field(
        default=None,
        description="List of organization industries."
    )

    organization_industry_tag_ids: Optional[List[str]] = Field(
        default=None,
        description="List of industry tag IDs, e.g. ['5567cd4773696439b10b0000']."
    )

    # Revenue filters
    revenue_range_min: Optional[int] = Field(
        default=None,
        description="Minimum company revenue in USD."
    )
    
    revenue_range_max: Optional[int] = Field(
        default=None,
        description="Maximum company revenue in USD."
    )

    # Funding and growth
    organization_latest_funding_stage_cd: Optional[List[str]] = Field(
        default=None,
        description="List of funding stage codes, e.g. ['2', '3', '10']."
    )

    # Technology and keywords
    currently_using_any_of_technology_uids: Optional[List[str]] = Field(
        default=None,
        description="Technology UIDs used by the organization, e.g. ['google_font_api']."
    )

    q_keywords: Optional[str] = Field(
        default=None,
        description="Keywords to search for in company descriptions, names, etc."
    )

    q_organization_domains: Optional[List[str]] = Field(
        default=None,
        description="Specific company domains to search for, e.g. ['microsoft.com', 'google.com']."
    )

    # Company-specific filters
    organization_ids: Optional[List[str]] = Field(
        default=None,
        description="Specific Apollo organization IDs to include."
    )

    not_organization_ids: Optional[List[str]] = Field(
        default=None,
        description="Apollo organization IDs to exclude from results."
    )

    # Search lists
    q_organization_search_list_id: Optional[str] = Field(
        default=None,
        description="Include only organizations in a specific search list."
    )
    
    q_not_organization_search_list_id: Optional[str] = Field(
        default=None,
        description="Exclude organizations in a specific search list."
    )

    # Sorting
    sort_by_field: Optional[str] = Field(
        default=None,
        description="Sort field, e.g. 'name', 'employee_count', 'last_updated', etc."
    )
    
    sort_ascending: Optional[bool] = Field(
        default=None,
        description="Sort ascending (True) or descending (False)."
    )

    # Additional filters that might be useful
    organization_founded_year_min: Optional[int] = Field(
        default=None,
        description="Minimum founding year for the organization."
    )
    
    organization_founded_year_max: Optional[int] = Field(
        default=None,
        description="Maximum founding year for the organization."
    )

