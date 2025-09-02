from ast import Dict

from pydantic import BaseModel, Field


class ArquivoDTO(BaseModel):
    SolicitacaoId: int = Field(..., description="ID da solicitação")
    Cpf: str = Field(..., description="CPF do contribuinte")
    S1200: list[Dict] | None = Field(None, description="Lista de arquivos S-1200")
    S1210: list[Dict] | None = Field(None, description="Lista de arquivos S-1210")
    S2200: list[Dict] | None = Field(None, description="Lista de arquivos S-2200")
    S2299: list[Dict] | None = Field(None, description="Lista de arquivos S-2299")
    IdeEmpregador: Dict = Field(..., description="Identificação do empregador")
    Cnpj: str = Field(..., description="CNPJ do empregador")
    DataInicio: str = Field(..., description="Data de início no formato YYYY-MM-DD")
    DataFim: str = Field(..., description="Data de fim no formato YYYY-MM-DD")
    CertificadoId: int = Field(..., description="ID do certificado")
    DataProcessamento: str = Field(
        ..., description="Data de processamento no formato YYYY-MM-DD"
    )
