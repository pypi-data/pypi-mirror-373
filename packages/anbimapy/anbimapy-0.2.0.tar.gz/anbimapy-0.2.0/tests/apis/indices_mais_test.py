import datetime as dt

from anbimapy import Anbima

d = dt.datetime(2024, 10, 10, tzinfo=dt.UTC).date()


def test_resultados_ida(anbima: Anbima) -> None:
    anbima.indices_mais.resultados.ida(d)


def test_resultados_idka(anbima: Anbima) -> None:
    anbima.indices_mais.resultados.idka(d)


def test_resultados_ihfa(anbima: Anbima) -> None:
    anbima.indices_mais.resultados.ihfa(d)


def test_resultados_ihfa_fechado(anbima: Anbima) -> None:
    anbima.indices_mais.resultados.ima(d)


def test_resultados_ima_intradiarios(anbima: Anbima) -> None:
    anbima.indices_mais.resultados.ima_intradiarios(d)


def test_carteiras_ida_previa(anbima: Anbima) -> None:
    anbima.indices_mais.carteiras.ida_previa(d)


def test_carteiras_ida(anbima: Anbima) -> None:
    anbima.indices_mais.carteiras.ida(d)


def test_carteiras_ihfa(anbima: Anbima) -> None:
    anbima.indices_mais.carteiras.ihfa(d)


def test_carteiras_ima(anbima: Anbima) -> None:
    anbima.indices_mais.carteiras.ima(d)


def test_carteiras_ima_previa(anbima: Anbima) -> None:
    anbima.indices_mais.carteiras.ima_previa(d)
