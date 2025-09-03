import datetime as dt
from typing import TYPE_CHECKING, List, Literal, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from anbimapy.anbima import Anbima


class DetalhesAtivo(TypedDict):
    codigo: str
    codigo_isin: NotRequired[str]
    codigo_bvmf: NotRequired[str]


class TotaisAtivo(TypedDict):
    preco_unitario_minimo: str
    preco_unitario_medio: str
    preco_unitario_maximo: str
    faixa_volume_negociacoes: str


class SubtotaisAtivo(TypedDict):
    preco_unitario_minimo: NotRequired[str]
    preco_unitario_medio: NotRequired[str]
    preco_unitario_maximo: NotRequired[str]
    faixa_volume_negociacoes: NotRequired[str]


class InformacoesPreviaItem(TypedDict):
    detalhes_ativo: DetalhesAtivo
    totais_ativo: TotaisAtivo
    subtotais_ativo: SubtotaisAtivo


class Previas(TypedDict):
    faixa_horario: str
    data_referencia: str
    instrumento_financeiro: str
    informacoes_previa: List[InformacoesPreviaItem]


class Reune:
    def __init__(self, http: "Anbima") -> None:
        self.http = http

    def previas(
        self,
        data: dt.date,
        instrumento: Literal["debenture", "cri", "cra", "cff"],
        faixa: str = "24:00",
    ) -> Previas:
        response = self.http.get(
            url="/precos-indices/v1/reune/previas-do-reune",
            params={
                "data": f"{data:%Y-%m-%d}",
                "instrumento": instrumento,
                "faixa": faixa,
            },
        )
        response.raise_for_status()
        return response.json()
