import datetime as dt
from typing import TYPE_CHECKING, Iterable, List, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from anbimapy.anbima import Anbima


class Vertice(TypedDict):
    vertice: str
    taxa_indicativa: NotRequired[float]
    taxa_compra: NotRequired[float]
    taxa_venda: NotRequired[float]


class ModelItem(TypedDict):
    data_referencia: str
    letra_financeira: str
    emissor: str
    cnpj_emissor: str
    indexador: str
    fluxo: str
    vertices: List[Vertice]


class LetrasFinanceiras:
    def __init__(self, http: "Anbima") -> None:
        self.http = http

    def matrizes_vertices_emissor(self, data: dt.date, tipo_lf: Iterable[str] = ()) -> ...:
        response = self.http.get(
            url="/precos-indices/v1/letras-financeiras/matrizes-vertices-emissor",
            params={
                "tipo-lf": list(tipo_lf),
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()
