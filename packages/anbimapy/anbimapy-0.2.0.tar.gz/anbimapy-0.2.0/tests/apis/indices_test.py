import datetime as dt

from anbimapy import Anbima

d = dt.datetime(2024, 10, 10, tzinfo=dt.UTC).date()


def test_pu_intradiario(anbima: Anbima) -> None:
    anbima.indices.pu_intradiario(d)


def test_ida_fechado(anbima: Anbima) -> None:
    anbima.indices.resultados.ida_fechado(d)


def test_idka(anbima: Anbima) -> None:
    anbima.indices.resultados.idka(d)


def test_ihfa_fechado(anbima: Anbima) -> None:
    anbima.indices.resultados.ihfa_fechado(d)


def test_ida(anbima: Anbima) -> None:
    anbima.indices.resultados.ima(d)


def test_ima_intradiarios(anbima: Anbima) -> None:
    anbima.indices.resultados.ima_intradiarios(d)
