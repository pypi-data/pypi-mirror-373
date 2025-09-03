import datetime as dt
from typing import TYPE_CHECKING, List, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from anbimapy.anbima import Anbima


class Componente(TypedDict):
    tipo_titulo: str
    data_vencimento: str
    codigo_selic: str
    codigo_isin: str
    taxa_indicativa: NotRequired[float]
    pu: float
    pu_juros: float
    quantidade_componentes: float
    quantidade_teorica: float
    valor_mercado: NotRequired[float]
    peso_componente: NotRequired[float]
    prazo_vencimento: NotRequired[int]
    duration: NotRequired[float]
    pmr: float
    convexidade: float


ResultadoIma = TypedDict(
    "ResultadoIma",
    {
        "indice": str,
        "data_referencia": str,
        "variacao_ult12m": float,
        "variacao_ult24m": float,
        "numero_indice": float,
        "variacao_diaria": float,
        "variacao_anual": float,
        "variacao_mensal": float,
        "peso_indice": NotRequired[float],
        "quantidade_titulos": float,
        "valor_mercado": float,
        "pmr": float,
        "convexidade": NotRequired[float],
        "duration": float,
        "yield": NotRequired[float],
        "redemption_yield": NotRequired[float],
        "componentes": List[Componente],
    },
)


class ResultadosMais:
    def __init__(self, http: "Anbima") -> None:
        self.http = http

    def ida(self, data: dt.date) -> ...:
        response = self.http.get(
            url="/precos-indices/v1/indices-mais/resultados-ida",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def idka(self, data: dt.date) -> ...:
        response = self.http.get(
            url="/precos-indices/v1/indices-mais/resultados-idka",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def ihfa(self, data: dt.date) -> ...:
        response = self.http.get(
            url="/precos-indices/v2/indices-mais/resultados-ihfa",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def ima(self, data: dt.date) -> ResultadoIma:
        response = self.http.get(
            url="/precos-indices/v1/indices-mais/resultados-ima",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def ima_intradiarios(self, data: dt.date) -> ...:
        response = self.http.get(
            url="/precos-indices/v1/indices-mais/resultados-intradiarios-ima",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()


class CarteirasMais:
    def __init__(self, http: "Anbima") -> None:
        self.http = http

    def ida_previa(self, month: dt.date) -> ...:
        response = self.http.get(
            url="/precos-indices/v1/indices-mais/previa-carteira-teorica-ida",
            params={
                "month": month.month,
                "year": month.year,
            },
        )
        response.raise_for_status()
        return response.json()

    def ida(self, month: dt.date) -> ...:
        response = self.http.get(
            url="/precos-indices/v1/indices-mais/carteira-teorica-ida",
            params={
                "month": month.month,
                "year": month.year,
            },
        )
        response.raise_for_status()
        return response.json()

    def ihfa(self, month: dt.date) -> ...:
        response = self.http.get(
            url="/precos-indices/v2/indices-mais/carteira-teorica-ihfa",
            params={
                "month": month.month,
                "year": month.year,
            },
        )
        response.raise_for_status()
        return response.json()

    def ima(self, month: dt.date) -> ...:
        response = self.http.get(
            url="/precos-indices/v1/indices-mais/carteira-teorica-ima",
            params={
                "month": month.month,
                "year": month.year,
            },
        )
        response.raise_for_status()
        return response.json()

    def ima_previa(self, month: dt.date) -> ...:
        response = self.http.get(
            url="/precos-indices/v1/indices-mais/previa-carteira-teorica-ima",
            params={
                "month": month.month,
                "year": month.year,
            },
        )
        response.raise_for_status()
        return response.json()


class IndicesMais:
    def __init__(self, http: "Anbima") -> None:
        self.http = http
        self.resultados = ResultadosMais(http)
        self.carteiras = CarteirasMais(http)
