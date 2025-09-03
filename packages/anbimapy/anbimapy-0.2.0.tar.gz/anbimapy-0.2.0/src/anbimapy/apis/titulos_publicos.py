import datetime as dt
from typing import TYPE_CHECKING, List, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from anbimapy.anbima import Anbima


class CurvaIntradiariaParametro(TypedDict):
    taxa: float
    vertice: int


class GrupoParametro(TypedDict):
    grupo_indexador: str
    parametros: List[CurvaIntradiariaParametro]


class CurvaIntradiaria(TypedDict):
    data_referencia: str
    grupo_parametros: List[GrupoParametro]


class CurvasJurosParametro(TypedDict):
    grupo_indexador: str
    b1: float
    b2: float
    b3: float
    b4: float
    l1: float
    l2: float


class Erro(TypedDict):
    tipo_titulo: str
    codigo_selic: str
    data_vencimento: str
    valor_erro: float


class EttjItem(TypedDict):
    vertice_du: int
    taxa_prefixadas: NotRequired[float]
    taxa_ipca: NotRequired[float]
    taxa_implicita: NotRequired[float]


class Bloco3361Item(TypedDict):
    vertice_du: int
    taxa: float


class CurvasJuros(TypedDict):
    data_referencia: str
    parametros: List[CurvasJurosParametro]
    erros: List[Erro]
    ettj: List[EttjItem]
    bloco3361: List[Bloco3361Item]


class DifusaoTaxas(TypedDict):
    tipo_titulo: str
    data_vencimento: str
    codigo_isin: str
    provedor_info: str
    data_referencia: str
    taxa_ind_d1: NotRequired[float]
    intervalo_ind_max: NotRequired[float]
    intervalo_ind_min: NotRequired[float]
    taxa_compra: NotRequired[float]
    taxa_venda: NotRequired[float]
    horario: NotRequired[str]
    taxa_negocio: NotRequired[float]


class EstimativaSelic(TypedDict):
    data_referencia: str
    estimativa_taxa_selic: float


class MercadoSecundarioTpf(TypedDict):
    tipo_titulo: str
    expressao: str
    data_vencimento: str
    data_referencia: str
    codigo_selic: str
    data_base: str
    taxa_compra: float
    taxa_venda: float
    taxa_indicativa: float
    intervalo_min_d0: float
    intervalo_max_d0: float
    intervalo_min_d1: float
    intervalo_max_d1: float
    pu: float
    desvio_padrao: float
    codigo_isin: str


class Projecao(TypedDict):
    indice: str
    tipo_projecao: str
    data_coleta: str
    mes_referencia: str
    variacao_projetada: float
    data_validade: NotRequired[str]


class PuIntradiario(TypedDict):
    data_referencia: str
    tipo_titulo: str
    codigo_selic: str
    data_vencimento: str
    taxa_intradiaria: float
    pu: float
    tipo_pu: str


class Titulo(TypedDict):
    tipo_titulo: str
    codigo_selic: str
    index: float
    tipo_correcao: str
    data_validade: str
    vna: float


class Vna(TypedDict):
    data_referencia: str
    titulos: List[Titulo]


class TitulosPublicos:
    def __init__(self, http: "Anbima") -> None:
        self.http = http

    def curva_intradiaria(self, data: dt.date) -> list[CurvaIntradiaria]:
        response = self.http.get(
            url="/precos-indices/v1/titulos-publicos/curva-intradiaria",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def curvas_juros(self, data: dt.date) -> list[CurvasJuros]:
        response = self.http.get(
            url="/precos-indices/v1/titulos-publicos/curvas-juros",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def difusao_taxas(self, data: dt.date) -> list[DifusaoTaxas]:
        response = self.http.get(
            url="/precos-indices/v1/titulos-publicos/difusao-taxas",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def estimativa_selic(self, data: dt.date) -> list[EstimativaSelic]:
        response = self.http.get(
            url="/precos-indices/v1/titulos-publicos/estimativa-selic",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def mercado_secundario_tpf(self, data: dt.date) -> list[MercadoSecundarioTpf]:
        response = self.http.get(
            url="/precos-indices/v1/titulos-publicos/mercado-secundario-TPF",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def projecoes(self, data: dt.date) -> list[Projecao]:
        response = self.http.get(
            url="/precos-indices/v1/titulos-publicos/projecoes",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def pu_intradiario(self, data: dt.date) -> list[PuIntradiario]:
        response = self.http.get(
            url="/precos-indices/v1/titulos-publicos/pu-intradiario",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()

    def vna(self, data: dt.date) -> list[Vna]:
        response = self.http.get(
            url="/precos-indices/v1/titulos-publicos/vna",
            params={
                "data": f"{data:%Y-%m-%d}",
            },
        )
        response.raise_for_status()
        return response.json()
