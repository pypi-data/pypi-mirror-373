import datetime as dt

from anbimapy import Anbima

d = dt.datetime(2024, 10, 10, tzinfo=dt.UTC).date()


def test_carteira_ida(anbima: Anbima) -> None:
    anbima.ida_liq.carteira_ida(d)


def test_carteira_ida_previa(anbima: Anbima) -> None:
    anbima.ida_liq.carteira_ida_previa(d)


def test_resultados_ida(anbima: Anbima) -> None:
    anbima.ida_liq.resultados_ida(d)
