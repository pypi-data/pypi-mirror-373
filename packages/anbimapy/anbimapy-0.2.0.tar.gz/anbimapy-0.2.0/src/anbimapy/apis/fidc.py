import datetime as dt
from typing import TYPE_CHECKING, List, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from anbimapy.anbima import Anbima


class MercadoSecundario(TypedDict):
    data_referencia: str
    nome: str
    serie: str
    emissor: str
    codigo_b3: str
    isin: str
    data_vencimento: str
    taxa_compra: NotRequired[float]
    taxa_venda: NotRequired[float]
    taxa_indicativa: float
    desvio_padrao: float
    pu: float
    percent_pu_par: float
    duration: float
    tipo_remuneracao: str
    taxa_correcao: float
    data_finalizado: str


class Fidc:
    def __init__(self, http: "Anbima") -> None:
        self.http = http

    def mercado_secundario(self, data: dt.date) -> List[MercadoSecundario]:
        response = self.http.get(
            url="/precos-indices/v1/fidc/mercado-secundario",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()
