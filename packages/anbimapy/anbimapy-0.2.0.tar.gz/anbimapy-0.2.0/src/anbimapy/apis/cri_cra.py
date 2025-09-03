import datetime as dt
from typing import TYPE_CHECKING, List, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from anbimapy.anbima import Anbima


class MercadoSecundario(TypedDict):
    data_referencia: str
    emissor: str
    originador: str
    originador_credito: str
    serie: str
    emissao: str
    codigo_ativo: str
    tipo_contrato: str
    data_vencimento: str
    taxa_compra: NotRequired[float]
    taxa_indicativa: NotRequired[float]
    desvio_padrao: NotRequired[float]
    vl_pu: NotRequired[float]
    pu: NotRequired[float]
    percent_pu_par: NotRequired[float]
    duration: NotRequired[float]
    tipo_remuneracao: str
    taxa_correcao: float
    data_finalizado: str
    taxa_venda: NotRequired[float]
    data_referencia_ntnb: NotRequired[str]
    referencia_ntnb: NotRequired[str]
    percent_reune: NotRequired[float]


class Projecao(TypedDict):
    indice: str
    tipo_projecao: str
    data_coleta: str
    mes_referencia: str
    variacao_projetada: float
    data_validade: NotRequired[str]


class CriCra:
    def __init__(self, http: "Anbima") -> None:
        self.http = http

    def mercado_secundario(self, data: dt.date) -> List[MercadoSecundario]:
        response = self.http.get(
            url="/precos-indices/v1/cri-cra/mercado-secundario",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def projecoes(self, month: dt.date) -> List[Projecao]:
        response = self.http.get(
            url="/precos-indices/v1/cri-cra/projecoes",
            params={
                "mes": month.month,
                "ano": month.year,
            },
        )
        response.raise_for_status()
        return response.json()
