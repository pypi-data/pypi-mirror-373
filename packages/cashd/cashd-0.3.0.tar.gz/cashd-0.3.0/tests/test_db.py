import pytest
from cashd.db import (
    fmt_moeda,
    fmt_telefone,
    fmt_nome_proprio,
    ErroDeFormatacao,
    ErroCampoVazio
)


@pytest.mark.parametrize(
    "val,expected",
    [
        (10000, "100,00"),
        ("999900", "9 999,00"),
        ("12,50", "0,00"),
        ("", "0,00"),
        ("texto", "0,00"),
    ],
)
def test_fmt_moeda_mostrar(val, expected):
    assert fmt_moeda(val, para_mostrar=True) == expected

@pytest.mark.parametrize(
    "val,iserror,error",
    [
        (10000, False, None),
        ("999900", False, None),
        ("12,50", True, ErroDeFormatacao),
        ("", True, ErroDeFormatacao),
        ("texto", True, ErroDeFormatacao),
    ]
)
def test_fmt_moeda_validar(val, iserror, error):
    if iserror:
        with pytest.raises(error):
            fmt_moeda(val)
    
    else:
        assert fmt_moeda(val) == int(val)