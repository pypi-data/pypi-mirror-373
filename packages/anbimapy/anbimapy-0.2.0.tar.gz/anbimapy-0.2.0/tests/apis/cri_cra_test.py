import datetime as dt

from anbimapy import Anbima

d = dt.datetime(2024, 10, 10, tzinfo=dt.UTC).date()


def test_mercado_secundario(anbima: Anbima) -> None:
    anbima.cri_cra.mercado_secundario(d)


def test_projecoes(anbima: Anbima) -> None:
    anbima.cri_cra.projecoes(d)
