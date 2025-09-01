from uuid import UUID
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from enum import Enum

##
# PERMISSION & ROLE
##

class PermissionBase(BaseModel):
    name: str
    label: Optional[str] = None
    description: Optional[str] = None

class PermissionCreate(PermissionBase):
    pass

class Permission(PermissionBase):
    id: int

    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    name: str
    label: Optional[str] = None
    description: Optional[str] = None

class RoleCreate(RoleBase):
    permission_ids: List[int] = []

class Role(RoleBase):
    id: int
    permissions: List[Permission] = []

    class Config:
        from_attributes = True


##
# ORGANIZATION
##

class OrganizationBase(BaseModel):
    name: str
    description: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    pass

class Organization(OrganizationBase):
    id: UUID
    # changed from datetime -> milliseconds since epoch
    created_at: Optional[int] = None

    class Config:
        from_attributes = True


##
# USER
##

class User(BaseModel):
    id: Optional[UUID] = None
    auth0_user_id: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    organization_id: Optional[UUID] = None
    created_at: Optional[int] = None
    roles: Optional[List[Role]] = []

    class Config:
        from_attributes = True

##
# AGENT + STATUSES
##

class AgentStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PUBLISHED = "PUBLISHED"

class AgentStatusUpdate(BaseModel):
    status: AgentStatus

class AgentInstanceStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ERROR = "ERROR"


##
# UI / CONFIG FIELDS
##

class SelectOption(BaseModel):
    label: str
    value: Any

class ValidationRules(BaseModel):
    required: Optional[bool] = None
    min: Optional[int] = None
    max: Optional[int] = None
    pattern: Optional[str] = None

class ConfigField(BaseModel):
    name: str
    label: str
    type: str
    sensitive: Optional[bool] = False
    default: Optional[Any] = Field(None, alias="default")
    description: Optional[str] = None
    validations: Optional[ValidationRules] = None
    options: Optional[List[SelectOption]] = None
    fields: Optional[List["ConfigField"]] = None  # for nested structures

    class Config:
        populate_by_name = True

ConfigField.model_rebuild()

class ConfigGroup(BaseModel):
    groupName: str
    fields: List[ConfigField]

class BackendDefinition(BaseModel):
    docker_image: Optional[str] = None
    environment_variables: Optional[Dict[str, str]] = None
    container_id: Optional[str] = None

class LayoutType(str, Enum):
    SINGLE_COLUMN = "single-column"
    TWO_COLUMN = "two-column"
    DASHBOARD = "dashboard"
    CHAT_INTERFACE = "chat-interface"
    SMART_LIST_BUILDER = "smart-list-builder"

class ComponentType(str, Enum):
    CHAT_WINDOW = "chat-window"
    HEADER = "header"
    FOOTER = "footer"
    SIDEBAR = "sidebar"
    MAIN_CONTENT = "main-content"
    DATA_TABLE = "data-table"
    CHART = "chart"
    FORM = "form"
    BUTTON = "button"
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    CUSTOM_COMPONENT = "custom-component"
    TABS = "tabs"
    TAB = "tab"
    FORM_ITEM = "form-item"
    INPUT = "input"
    TEXTAREA = "textarea"
    UPLOAD = "upload"

class ComponentPosition(BaseModel):
    row: Optional[int] = None
    column: Optional[int] = None
    area: Optional[str] = None

class RenderComponent(BaseModel):
    type: ComponentType
    position: Optional[ComponentPosition] = None
    properties: Optional[Dict[str, Any]] = None
    children: Optional[List["RenderComponent"]] = None
    injector: Optional[Any] = None

class ActionDefinition(BaseModel):
    type: str
    method: str
    url: str
    data: Optional[Any] = None
    state: Optional[str] = None
    onSuccess: Optional[str] = None

class RenderDefinition(BaseModel):
    layout: LayoutType
    components: List[RenderComponent]
    actions: Optional[Dict[str, ActionDefinition]] = None
    initialActions: Optional[List[str]] = None

class ConfigValue(BaseModel):
    name: str
    value: Any
    fields: Optional[List["ConfigValue"]] = None

    class Config:
        populate_by_name = True

ConfigValue.model_rebuild()

class SchemaDefinition(BaseModel):
    name: str
    version: str
    fields: List[ConfigField]
    migrations: Optional[List[Dict[str, Any]]] = None

##
# AGENT
##

class Agent(BaseModel):
    id: Optional[UUID] = None
    name: str
    description: str
    image_url: str
    expertise: List[str]
    version: str
    schema_definition: Optional[List[SchemaDefinition]] = None
    config_definition: List[ConfigGroup]
    agent_config_definition: Optional[List[ConfigGroup]] = None
    agent_configuration: Optional[List[ConfigValue]] = None
    render_definition: RenderDefinition
    backend: BackendDefinition
    repository_url: Optional[str] = None
    status: Optional[AgentStatus] = AgentStatus.PENDING

    organization_id: Optional[UUID] = None
    created_by: Optional[UUID] = None
    created_at: Optional[int] = None
    updated_by: Optional[UUID] = None
    updated_at: Optional[int] = None

    class Config:
        from_attributes = True
        populate_by_name = True

##
# AGENT INSTANCE
##

class AgentInstance(BaseModel):
    id: Optional[UUID] = None
    published_agent_id: UUID
    name: str
    description: str
    image_url: str
    expertise:  Optional[List[str]] = None
    version: str
    schema_definition: Optional[List[SchemaDefinition]] = None
    configuration: List[ConfigValue]
    render_definition: RenderDefinition = None
    backend: BackendDefinition = None
    status: AgentInstanceStatus = AgentInstanceStatus.INACTIVE
    status_message: Optional[str] = None
    service_url: Optional[str] = None
    port: Optional[int] = None

    organization_id: Optional[UUID] = None
    created_by: Optional[UUID] = None    
    created_at: Optional[int] = None
    updated_by: Optional[UUID] = None
    updated_at: Optional[int] = None

    class Config:
        from_attributes = True
        populate_by_name = True


##
# AGENT INSTANCE DATA
##

class AgentInstanceData(BaseModel):
    id: Optional[UUID] = None
    type: str
    version: str
    agent_instance_id: UUID
    organization_id: UUID
    data: Dict[str, Any]
    created_by: Optional[UUID] = None    
    created_at: Optional[int] = None
    updated_by: Optional[UUID] = None
    updated_at: Optional[int] = None

    class Config:
        populate_by_name = True


##
# SOURCE
##

class SourceType(str, Enum):
    FILE = "file"
    GOOGLE_DOC = "google_doc"
    WEBSITE = "website"
    YOUTUBE = "youtube"
    TEXT = "text"

class SourceBase(BaseModel):
    source_type: SourceType
    title: Optional[str] = None
    source_metadata: Optional[dict] = None
    blob_url: Optional[HttpUrl] = None
    content: Optional[str] = None

class SourceCreate(SourceBase):
    pass

class SourceUpdate(SourceBase):
    pass

class Source(SourceBase):
    id: UUID
    agent_instance_id: UUID
    # changed from datetime -> milliseconds
    created_at: Optional[int] = None
    created_by: Optional[UUID] = None

    class Config:
        populate_by_name = True

##
# INTEGRATION
##

class IntegrationStatus(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    COMING_SOON = "coming soon"

class IntegrationBase(BaseModel):
    name: str
    label: str
    icon: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    status: IntegrationStatus = IntegrationStatus.DISCONNECTED
    configuration: Optional[List["ConfigValue"]] = None

class IntegrationCreate(IntegrationBase):
    agent_instance_id: UUID
    organization_id: UUID

class IntegrationUpdate(BaseModel):
    name: Optional[str] = None
    label: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[IntegrationStatus] = None
    configuration: Optional[List["ConfigValue"]] = None

class Integration(IntegrationBase):
    id: UUID
    agent_instance_id: UUID
    organization_id: UUID    
    created_at: Optional[int] = None
    created_by: Optional[UUID] = None

    class Config:
        from_attributes = True
        populate_by_name = True

Integration.model_rebuild()
IntegrationUpdate.model_rebuild()

class SendEmailContext(BaseModel):
    recipient: str
    subject: str
    body: str
    sender_name: str
    sender_email: str
    labels: Optional[List[str]]
    
class QueryEmailContext(BaseModel):
    start_time: str
    end_time: str
    sender_email: str
    unread_only: bool = True
    labels: Optional[List[str]] = None
    

class ReplyEmailContext(BaseModel):
    message_id: str
    reply_body: str
    sender_email: str
    sender_name: str
    mark_as_read: str = "True"
    add_labels: Optional[List[str]] = None