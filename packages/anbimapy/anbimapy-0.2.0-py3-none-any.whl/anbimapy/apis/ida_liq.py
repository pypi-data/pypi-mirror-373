import datetime as dt
from typing import TYPE_CHECKING, Any, List, TypedDict

if TYPE_CHECKING:
    from anbimapy.anbima import Anbima


class Referencia(TypedDict):
    codigo_titulo: str
    emissor: str
    codigo_isin_titulo: str
    data_vencimento: str
    indexador: str
    quantidade: int
    pu: float
    peso: float
    peso_emissor: float
    quantidade_teorica: float


class CarteiraIda(TypedDict):
    indice: str
    data_inicio: str
    data_fim: str
    referencias: List[Referencia]


class Componente(TypedDict):
    codigo: str
    emissor: str
    codigo_isin: str
    data_vencimento: str
    grupo: str
    taxa_indicativa: float
    pu: float
    pu_juros: float
    eventos: str
    peso: float
    quantidade_teorica: float
    valor_mercado: float
    duration: int


class ResultadoIda(TypedDict):
    numero_indice: float
    variacao_anual: float
    indice: str
    variacao_ult24m: float
    variacao_ult12m: float
    variacao_diaria: float
    data_referencia: str
    peso: float
    valor_mercado: float
    variacao_mensal: float
    duration: int
    componentes: List[Componente]


class IdaLiq:
    def __init__(self, http: "Anbima") -> None:
        self.http = http

    def carteira_ida(self, month: dt.date) -> List[CarteiraIda]:
        response = self.http.get(
            url="/precos-indices/v1/ida-liq/carteira-teorica-ida",
            params={
                "mes": month.month,
                "ano": month.year,
            },
        )
        response.raise_for_status()
        return response.json()

    def carteira_ida_previa(self, month: dt.date) -> List[Any]:  # TODO: typing
        response = self.http.get(
            url="/precos-indices/v1/ida-liq/previa-carteira-teorica-ida",
            params={
                "mes": month.month,
                "ano": month.year,
            },
        )
        response.raise_for_status()
        return response.json()

    def resultados_ida(self, data: dt.date) -> List[ResultadoIda]:
        response = self.http.get(
            url="/precos-indices/v1/ida-liq/resultados-ida",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()
