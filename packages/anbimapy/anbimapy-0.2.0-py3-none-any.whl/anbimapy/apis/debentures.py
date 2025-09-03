import datetime as dt
from typing import TYPE_CHECKING, List, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from anbimapy.anbima import Anbima


class CurvaCredito(TypedDict):
    a: float
    aa: float
    aaa: float
    data_referencia: str
    vertice_anos: float


class MercadoSecundario(TypedDict):
    grupo: str
    codigo_ativo: str
    data_referencia: str
    emissor: str
    data_vencimento: str
    percentual_taxa: str
    taxa_compra: NotRequired[float]
    taxa_venda: NotRequired[float]
    taxa_indicativa: NotRequired[float]
    desvio_padrao: NotRequired[float]
    val_min_intervalo: NotRequired[float]
    val_max_intervalo: NotRequired[float]
    pu: NotRequired[float]
    percent_pu_par: NotRequired[float]
    duration: NotRequired[int]
    percent_reune: str
    referencia_ntnb: NotRequired[str]


class Projecao(TypedDict):
    indice: str
    tipo_projecao: str
    data_coleta: str
    mes_referencia: str
    variacao_projetada: float
    data_validade: NotRequired[str]


class Debentures:
    def __init__(self, http: "Anbima") -> None:
        self.http = http

    def curvas_credito(self, data: dt.date) -> List[CurvaCredito]:
        response = self.http.get(
            url="/precos-indices/v1/debentures/curvas-credito",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def mercado_secundario(self, data: dt.date) -> List[MercadoSecundario]:
        response = self.http.get(
            url="/precos-indices/v1/debentures/mercado-secundario",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def projecoes(self, data: dt.date) -> List[Projecao]:
        response = self.http.get(
            url="/precos-indices/v1/debentures/projecoes",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()
