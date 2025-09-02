import re
from datetime import date, datetime, timedelta

from pydantic import BaseModel, Field, field_validator

from libretificacaotjcore.enums.e_eventos import EEventos


class SolicitacaoDTO(BaseModel):
    SolicitacaoId: int = Field(..., description="ID da solicitação")
    Cnpj: str = Field(..., description="CNPJ da empresa")
    DataInicio: date = Field(..., description="Data de início no formato YYYY-MM-DD")
    DataFim: date = Field(..., description="Data de fim no formato YYYY-MM-DD")
    CertificadoId: int = Field(..., description="ID do certificado")
    Evento: str | None = Field(None, description="Evento de retificação")

    @field_validator("SolicitacaoId")
    @classmethod
    def validar_solicitacao_id(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("O solicitacaoId deve ser um inteiro positivo.")
        return v

    @field_validator("CertificadoId")
    @classmethod
    def validar_certificado_id(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("O certificadoId deve ser um inteiro positivo.")
        return v

    @field_validator("Cnpj")
    @classmethod
    def validar_cnpj(cls, v: str) -> str:
        cnpj_limpo = re.sub(r"\D", "", v)
        if len(cnpj_limpo) != 14 or not cnpj_limpo.isdigit():
            raise ValueError("O CNPJ deve conter 14 dígitos numéricos.")
        return cnpj_limpo

    @field_validator("DataInicio", mode="before")
    @classmethod
    def formatar_data_inicio(cls, value: str) -> date:
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError as ve:
            raise ValueError("A dataInicio deve estar no formato YYYY-MM-DD.") from ve

    @field_validator("DataFim", mode="before")
    @classmethod
    def ajustar_data_fim(cls, value: str) -> date:
        ano, mes = map(int, value.split("-")[:2])
        if mes < 1 or mes > 12:
            raise ValueError(
                "A dataFim deve estar no formato YYYY-MM-DD e conter um mês válido."
            )
        if mes == 12:
            proximo_mes = datetime(ano + 1, 1, 1)
        else:
            proximo_mes = datetime(ano, mes + 1, 1)
        return (proximo_mes - timedelta(days=1)).date()
    
    @field_validator("Evento")
    @classmethod
    def validar_eventos(cls, v: str) -> str | None:
        if v is None:
            return v
        
        if v not in EEventos:
            raise ValueError(f"Evento '{v}' não é válido.")
        return v
