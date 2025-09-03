from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any
from ..sessions import SessionStatus, SessionUpdateFields
from ..session_schedules import ScheduledMessageConfig, ScheduledNodeConfig
from datetime import datetime
from typing import Union

class SessionsCreateRequest(BaseModel):
    contact_id: str = Field(..., description="ID do contato (recomendamos usar o número do WhatsApp, @ do Instagram, etc. para facilitar identificação)")
    contact_name: str = Field(..., description="Nome do contato que será usado pelo agente de IA para personalização")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Metadados da sessão vindos do seu CRM/sistema (ex: prioridade, ticket externo, tier do cliente). Estes dados retornam via webhook e podem ser usados pelo agente de IA")
    status: Literal["closed", "open"] = Field(default="open", description="Status inicial da sessão")
    agent_id: Optional[str] = Field(default=None, description="ID do agente de IA responsável pelo atendimento")

class SessionsTransferRequest(BaseModel):
    agent_id: Optional[str] = Field(default=None, description="ID do agente de IA para transferência (null remove o agente da sessão)")
    auto_reply: Optional[bool] = Field(default=None, description="Se deve acionar resposta automática do agente após a transferência (true) ou apenas transferir (false)")

class SessionsFinishRequest(BaseModel):
    ending_survey_id: Optional[str] = Field(default=None, description="ID da pesquisa de satisfação para iniciar após o fechamento da sessão")

class SessionsUpdateRequest(BaseModel):
    fields: SessionUpdateFields = Field(..., description="Campos a serem atualizados na sessão. Pode incluir metadata, status, agent_id, etc.")

class SessionsSearchRequest(BaseModel):
    contact_id: Optional[str] = Field(default=None, description="ID do contato para buscar")
    status: Optional[SessionStatus] = Field(default=None, description="Status da sessão para buscar")
    offset: Optional[int] = Field(default=None, description="Número de registros para pular")
    limit: Optional[int] = Field(default=100, description="Limite máximo de registros retornados")

class SessionsReplyRequest(BaseModel):
    debounce_time: int = Field(default=3, ge=3, le=60, description="Tempo de debounce em segundos (3-60)")
    starting_node_id: Optional[str] = Field(default=None, description="ID do node de início")

class SessionScheduleRequest(BaseModel):
    scheduled_for: datetime = Field(..., description="When to send (UTC)")
    config: Union[ScheduledMessageConfig, ScheduledNodeConfig] = Field(..., discriminator='type')


