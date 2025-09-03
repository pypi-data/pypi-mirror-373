import datetime as dt

from anbimapy import Anbima

d = dt.datetime(2024, 10, 10, tzinfo=dt.UTC).date()


def test_fidc(anbima: Anbima) -> None:
    anbima.fidc.mercado_secundario(d)
