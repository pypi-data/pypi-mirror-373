import datetime as dt

from anbimapy import Anbima

d = dt.datetime(2024, 10, 10, tzinfo=dt.UTC).date()


def test_curva_intradiaria(anbima: Anbima) -> None:
    anbima.titulos_publicos.curva_intradiaria(d)


def test_curvas_juros(anbima: Anbima) -> None:
    anbima.titulos_publicos.curvas_juros(d)


def test_difusao_taxas(anbima: Anbima) -> None:
    anbima.titulos_publicos.difusao_taxas(d)


def test_estimativa_selic(anbima: Anbima) -> None:
    anbima.titulos_publicos.estimativa_selic(d)


def test_mercado_secundario_tpf(anbima: Anbima) -> None:
    anbima.titulos_publicos.mercado_secundario_tpf(d)


def test_projecoes(anbima: Anbima) -> None:
    anbima.titulos_publicos.projecoes(d)


def test_pu_intradiario(anbima: Anbima) -> None:
    anbima.titulos_publicos.pu_intradiario(d)


def test_vna(anbima: Anbima) -> None:
    anbima.titulos_publicos.vna(d)
