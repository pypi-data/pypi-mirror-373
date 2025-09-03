import datetime as dt
from typing import TYPE_CHECKING, List, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from anbimapy.anbima import Anbima


class IdaFechado(TypedDict):
    indice: str
    numero_indice: float
    data_referencia: str
    variacao_anual: float
    variacao_diaria: float
    variacao_ult12m: float
    variacao_mensal: float
    variacao_ult24m: float
    peso: float
    valor_mercado: float
    duration: int


class Idka(TypedDict):
    data_referencia: str
    variacao_mensal: float
    numero_indice: float
    variacao_ult12m: float
    tx_compra: float
    tx_venda: float
    variacao_anual: float
    variacao_diaria: float
    volatilidade: float
    nome: str


class IhfaFechado(TypedDict):
    data_referencia: str
    numero_indice: float
    variacao_mensal: float
    variacao_anual: float
    variacao_diaria: float
    variacao_ult12m: float


Ima = TypedDict(
    "Ima",
    {
        "indice": str,
        "variacao_mensal": float,
        "variacao_diaria": float,
        "variacao_anual": float,
        "data_referencia": str,
        "numero_indice": float,
        "variacao_ult12m": float,
        "variacao_ult24m": float,
        "peso_indice": NotRequired[float],
        "quantidade_titulos": float,
        "duration": float,
        "valor_mercado": float,
        "convexidade": float,
        "pmr": float,
        "yield": NotRequired[float],
        "redemption_yield": NotRequired[float],
    },
)


class ImaIntradiarios(TypedDict):
    indice: str
    data_referencia: str
    indice_intradiario: float
    variacao_intradiaria: float


class PuIntradiario(TypedDict):
    data_referencia: str
    tipo_titulo: str
    codigo_selic: str
    data_vencimento: str
    taxa_intradiaria: float
    pu: float
    tipo_pu: str


class Resultados:
    def __init__(self, http: "Anbima") -> None:
        self.http = http

    def ida_fechado(self, data: dt.date) -> List[IdaFechado]:
        response = self.http.get(
            url="/precos-indices/v1/indices/resultados-ida-fechado",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def idka(self, data: dt.date) -> List[Idka]:
        response = self.http.get(
            url="/precos-indices/v1/indices/resultados-idka",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def ihfa_fechado(self, data: dt.date) -> List[IhfaFechado]:
        response = self.http.get(
            url="/precos-indices/v1/indices/resultados-ihfa-fechado",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def ima(self, data: dt.date) -> List[Ima]:
        response = self.http.get(
            url="/precos-indices/v1/indices/resultados-ima",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def ima_intradiarios(self, data: dt.date) -> List[ImaIntradiarios]:
        response = self.http.get(
            url="/precos-indices/v1/indices/resultados-intradiarios-ima",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()


class Indices:
    def __init__(self, http: "Anbima") -> None:
        self.http = http
        self.resultados = Resultados(http)

    def pu_intradiario(self, data: dt.date) -> List[PuIntradiario]:
        response = self.http.get(
            url="/precos-indices/v1/indices-mais/pu-intradiario",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()
