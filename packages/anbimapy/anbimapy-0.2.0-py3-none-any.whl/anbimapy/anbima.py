from typing import Literal

import httpx

from anbimapy.apis.cri_cra import CriCra
from anbimapy.apis.debentures import Debentures
from anbimapy.apis.fidc import Fidc
from anbimapy.apis.ida_liq import IdaLiq
from anbimapy.apis.indice_mais import IndicesMais
from anbimapy.apis.indices import Indices
from anbimapy.apis.letras_financeiras import LetrasFinanceiras
from anbimapy.apis.reune import Reune
from anbimapy.apis.titulos_publicos import TitulosPublicos
from anbimapy.auth import AnbimaAuth


class Anbima(httpx.Client):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        *,
        host: Literal["api.anbima.com.br", "api-sandbox.anbima.com.br"] = "api.anbima.com.br",
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.host = host

        auth = AnbimaAuth(self.client_id, self.client_secret)
        super().__init__(
            base_url=f"https://{host}/feed",
            timeout=30,
            auth=auth,
        )

        self.cri_cra = CriCra(self)
        self.debentures = Debentures(self)
        self.fidc = Fidc(self)
        self.ida_liq = IdaLiq(self)
        self.indices = Indices(self)
        self.indices_mais = IndicesMais(self)
        self.letras_financeiras = LetrasFinanceiras(self)
        self.reune = Reune(self)
        self.titulos_publicos = TitulosPublicos(self)
