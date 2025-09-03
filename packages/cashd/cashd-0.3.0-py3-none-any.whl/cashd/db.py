import pandas as pd
from cashd import prefs
from datetime import datetime, date
from sqlalchemy import (
    ForeignKey,
    Integer,
    create_engine,
    DateTime,
    Date,
    insert,
    update,
    select,
    delete,
    case,
    text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    DeclarativeBase,
    relationship,
    Session,
    Query,
)
from copy import deepcopy
from typing import List, Literal
from time import sleep
from platform import system
import os
from os import path
import phonenumbers


####################
# VARIAVEIS DO BANCO DE DADOS
####################

SCRIPT_FOLDER = path.dirname(path.realpath(__file__))
DATA_FOLDER = SCRIPT_FOLDER + "\\data"
os.makedirs(DATA_FOLDER, exist_ok=True)
DB_ENGINE = create_engine(f"sqlite:///{DATA_FOLDER}\\database.db", echo=False)


class dec_base(DeclarativeBase):
    pass


class tbl_clientes(dec_base):
    __tablename__ = "clientes"
    SaldoTransacoes: Mapped[List["tbl_transacoes"]] = relationship()

    Id: Mapped[int] = mapped_column(primary_key=True)
    PrimeiroNome: Mapped[str] = mapped_column()
    Sobrenome: Mapped[str] = mapped_column()
    Apelido: Mapped[str] = mapped_column()
    Telefone: Mapped[str] = mapped_column()
    Cidade: Mapped[str] = mapped_column()
    Bairro: Mapped[str] = mapped_column()
    Endereco: Mapped[str] = mapped_column()
    Estado: Mapped[str] = mapped_column()


class tbl_transacoes(dec_base):
    __tablename__ = "transacoes"
    NomeCliente: Mapped["tbl_clientes"] = relationship(back_populates="SaldoTransacoes")

    Id: Mapped[int] = mapped_column(primary_key=True)
    IdCliente: Mapped[int] = mapped_column(ForeignKey("clientes.Id"))
    CarimboTempo: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    DataTransac: Mapped[date] = mapped_column(Date())
    Valor: Mapped[int] = mapped_column()  # valor em centavos


dec_base.metadata.create_all(DB_ENGINE)

SYS_NAME = system()
try:
    if SYS_NAME == "Windows":
        WORK_DIR = path.expanduser("~\\Appdata\\Roaming\\Cashd")

    elif SYS_NAME == "Darwin":
        WORK_DIR = path.expanduser("~/Library/Preferences/Cashd")

    else:
        WORK_DIR = path.expanduser("~/.local/Share/Cashd")

    os.makedirs(WORK_DIR, exist_ok=True)
    os.chdir(WORK_DIR)

except Exception as manage_dir_error:
    sleep_time = 30
    print("ERRO FATAL:\n", manage_dir_error, "\nFechando em 30 segundos...", sep="")
    sleep(30)
    quit()


####################
# FORMATACAO
####################


class ErroCampoVazio(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ErroDeFormatacao(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def fmt_moeda(inp: str | int, para_mostrar: bool = False) -> str | int:
    """
    ### `para_mostrar == False`:

    Retorna `inp` como um número `int`, ou levanta um `ErroDeFormatacao`.
    - 100000 -> 100000
    - -5254 -> -5254
    - 0 -> ErroDeFormatacao
    - 58/66 -> ErroDeFormatacao

    ### `para_mostrar == True`:

    Formata números inteiros (em centavos) para R$, retornando `str`.
    - 100000 ->  `'1 000,00'`
    - -5254 -> `'-52,54'`
    - 0 -> `'0,00'`
    - 58/66 -> `'0,00'`
    """
    if para_mostrar:
        try:
            return f"{int(inp)/100:_.2f}".replace("_", " ").replace(".", ",")

        except ValueError:
            return "0,00"

    else:
        try:
            out = int(inp)
            if out == 0:
                raise ErroDeFormatacao("Valor não pode ser zero")

        except ValueError:
            raise ErroDeFormatacao("Valor deve conter apenas números")

    return out


def fmt_telefone(inp: str, para_mostrar: bool = False) -> str:
    """"""
    try:
        return phonenumbers.format_number(
            numobj=phonenumbers.parse(inp, "BR"),
            num_format=phonenumbers.PhoneNumberFormat.NATIONAL,
        )

    except phonenumbers.NumberParseException:
        if para_mostrar:
            return "Número inválido"
        else:
            raise ErroDeFormatacao("Número de telefone inválido")


def fmt_nome_proprio(
    inp: str,
    permitido_vazio: bool = False,
) -> str:

    if not permitido_vazio and len(inp) == 0:
        raise ErroCampoVazio("Nome obrigatório não pode ficar vazio")

    return inp.title()


####################
# FORMULARIOS
####################


class NomeObrigatorio(str):
    def __init__(self) -> None:
        super().__init__()


class NomeOpcional(str):
    def __init__(self) -> None:
        super().__init__()


class NumeroTelefone(str):
    def __init__(self) -> None:
        super().__init__()


class NomeObrigatorioMaiusculo(str):
    def __init__(self) -> None:
        super().__init__()


class NumeroMoeda(int):
    def __init__(self) -> None:
        super().__init__()


class FormObj:
    def format_vars(self):
        _types = self.__init__.__annotations__

        for var in _types.keys():
            value = getattr(self, var)

            if _types[var] == NomeObrigatorio:
                try:
                    setattr(self, var, fmt_nome_proprio(value, False))
                except Exception as msg_erro:
                    raise ErroDeFormatacao(f"Erro em '{var}':\n{str(msg_erro)}")

            if _types[var] == NomeOpcional:
                try:
                    setattr(self, var, fmt_nome_proprio(value, True))
                except Exception as msg_erro:
                    raise ErroDeFormatacao(f"Erro em '{var}':\n{str(msg_erro)}")

            elif _types[var] == NumeroTelefone:
                try:
                    setattr(self, var, fmt_telefone(value))
                except Exception as msg_erro:
                    raise ErroDeFormatacao(f"Erro em '{var}':\n{str(msg_erro)}")

            elif _types[var] == NumeroMoeda:
                try:
                    setattr(self, var, fmt_moeda(value))
                except Exception as msg_erro:
                    raise ErroDeFormatacao(f"Erro em '{var}':\n{str(msg_erro)}")

            elif _types[var] == NomeObrigatorioMaiusculo:
                try:
                    setattr(self, var, fmt_nome_proprio(value, False).upper())
                except Exception as msg_erro:
                    raise ErroDeFormatacao(f"Erro em '{var}':\n{str(msg_erro)}")

    def despejar(self) -> dict:
        self.format_vars()
        return deepcopy(vars(self))


class FormContas(FormObj):
    def __init__(
        self,
        PrimeiroNome: NomeObrigatorio = "",
        Sobrenome: NomeObrigatorio = "",
        Apelido: NomeOpcional = "",
        Telefone: NumeroTelefone = "81900000000",
        Cidade: NomeObrigatorio = prefs.settings.read_main_city(),
        Bairro: NomeOpcional = "",
        Endereco: NomeOpcional = "",
        Estado: NomeObrigatorioMaiusculo = prefs.settings.read_main_state(),
    ):

        self.PrimeiroNome = PrimeiroNome
        self.Sobrenome = Sobrenome
        self.Apelido = Apelido
        self.Telefone = Telefone
        self.Cidade = Cidade
        self.Bairro = Bairro
        self.Endereco = Endereco
        self.Estado = Estado

    def carregar_valores(self, tbl: tbl_clientes):
        self.PrimeiroNome = tbl.PrimeiroNome
        self.Sobrenome = tbl.Sobrenome
        self.Apelido = tbl.Apelido
        self.Telefone = tbl.Telefone
        self.Cidade = tbl.Cidade
        self.Bairro = tbl.Bairro
        self.Endereco = tbl.Endereco
        self.Estado = tbl.Estado

    def __str__(self):
        return ""

    def __repr__(self):
        return (
            "cashd.db.FormContas object. Fields:\n"
            + f"{self.PrimeiroNome=}\n"
            + f"{self.Sobrenome=}\n"
            + f"{self.Apelido=}\n"
            + f"{self.Telefone=}\n"
            + f"{self.Cidade=}\n"
            + f"{self.Bairro=}\n"
            + f"{self.Endereco=}\n"
            + f"{self.Estado=}"
        )

    def despejar(self) -> dict:
        form = super().despejar()
        self.__init__()
        return form


class FormTransac(FormObj):
    def __init__(
        self, IdCliente, DataTransac: date = date.today(), Valor: NumeroMoeda = ""
    ):

        self.IdCliente = IdCliente
        self.DataTransac = DataTransac
        self.Valor = Valor

    def carregar_valores(self, tbl: tbl_transacoes):
        self.IdCliente = tbl.IdCliente
        self.DataTransac = tbl.DataTransac
        self.Valor = fmt_moeda(tbl.Valor, True)

    def __repr__(self):
        return f"{self.IdCliente=}\n" + f"{self.DataTransac=}\n" + f"{self.Valor=}\n"


####################
# QUERRIES
####################


def listar_clientes() -> None:
    with Session(DB_ENGINE) as ses:
        stmt = select(tbl_clientes)
        res = ses.execute(stmt).scalars()
        max_id = ses.execute(text("SELECT MAX(Id) FROM clientes;")).scalar()
        n_digits = len(str(max_id))
        output = []
        for r in res:
            linha = {
                "id": str(r.Id).zfill(n_digits),
                "nome": f"{str(r.Id).zfill(n_digits)}, {r.PrimeiroNome} {r.Sobrenome}",
            }

            if r.Apelido != "":
                linha["nome"] = linha["nome"] + f" ({r.Apelido})"
            elif r.Apelido == "" and r.Bairro != "":
                linha["nome"] = linha["nome"] + f", {r.Bairro}"

            output.append(linha)

    return output


def listar_transac_cliente(Id: int, para_mostrar: bool = True) -> dict | list:
    Id = int(Id)

    stmt = select(
        tbl_transacoes.Id, tbl_transacoes.DataTransac, tbl_transacoes.Valor
    ).where(tbl_transacoes.IdCliente == Id)

    with Session(DB_ENGINE) as ses:
        res = ses.execute(stmt).all()

        if para_mostrar:
            df = pd.DataFrame([row[1:] for row in res], columns=["Data", "Valor R$"])
            df["Valor R$"] = list(map(lambda x: fmt_moeda(x, True), df["Valor R$"]))
            df = df.loc[::-1].sort_values("Data", axis=0, ascending=False)
            saldo = fmt_moeda(sum(r.Valor for r in res), para_mostrar=True)
            local = local_por_id(Id=Id)
            return {"df": df, "saldo": saldo, "local": local}

        return list(
            reversed(
                [
                    (
                        str(row[0]),
                        f"{row[1].strftime('%d/%m/%Y')} | {fmt_moeda(row[2], True)}",
                    )
                    for row in res
                ]
            )
        )


def adicionar_cliente(cliente: tbl_clientes) -> None:
    with Session(DB_ENGINE) as ses:
        ses.add(cliente)
        ses.commit()


def atualizar_cliente(Id: int, form: FormContas) -> None:
    Id = int(Id)
    table_values = form.despejar()

    with Session(DB_ENGINE) as ses:
        stmt = update(tbl_clientes).where(tbl_clientes.Id == Id).values(**table_values)
        ses.execute(stmt)
        ses.commit()


def adicionar_transac(transac: tbl_transacoes) -> None:
    with Session(DB_ENGINE) as ses:
        ses.add(transac)
        ses.commit()


def remover_transac(Id: int) -> None:
    with Session(DB_ENGINE) as ses:
        stmt = delete(tbl_transacoes).where(tbl_transacoes.Id == Id)
        ses.execute(stmt)
        ses.commit()


def cliente_por_id(Id: int) -> tbl_clientes:
    """retorna um objeto `db.tbl_clientes` com o id especificado."""
    Id = int(Id)
    with Session(DB_ENGINE) as ses:
        stmt = select(tbl_clientes).where(tbl_clientes.Id == Id)
        return ses.execute(stmt).first()[0]


def transac_por_id(Id: int) -> tbl_transacoes:
    """retorna um objeto `db.tbl_transacoes` com o id especificado."""
    Id = int(Id)
    with Session(DB_ENGINE) as ses:
        stmt = select(tbl_transacoes).where(tbl_transacoes.Id == Id)
        return ses.execute(stmt).first()[0]


def id_transac_pertence_a_cliente(IdTransac: int, IdCliente: int) -> bool:
    """Retorna `True` se a transacao pertence ao cliente, `False` em qualquer outro caso."""
    IdTransac, IdCliente = int(IdTransac), int(IdCliente)
    stmt = select(tbl_transacoes).filter_by(Id=IdTransac, IdCliente=IdCliente)
    with Session(DB_ENGINE) as ses:
        if ses.execute(stmt).first() is None:
            return False
        return True


def saldos_transac_periodo(
    periodo: Literal["mes", "sem", "dia"] = "mes", n: int | None = None
) -> pd.DataFrame:
    """
    Retorna um `pandas.DataFrame` com três colunas:
    - Data
    - Somas
    - Abatimentos

    `n` indica a quantidade de linhas que devem ser retornadas, começando pela
    última, se `n=None`, retornará todas as linhas.
    """
    formato = "%Y-%m"
    if periodo == "sem":
        formato = "%Y-%W"
    if periodo == "dia":
        formato = "%Y-%m-%d"

    stmt = f"""
    select
        STRFTIME('{formato}', "DataTransac") AS MesTransac,
        SUM(CASE WHEN Valor>0 THEN Valor ELSE 0 END)*1.0/100 AS Somas,
        SUM(CASE WHEN Valor<0 THEN Valor ELSE 0 END)*1.0/100 AS Abatimentos
    from transacoes
    group by STRFTIME('{formato}', "DataTransac");
    """

    with Session(DB_ENGINE) as ses:
        result = ses.execute(text(stmt)).all()
        tbl = pd.DataFrame(
            [res for res in result], columns=["Data", "Somas", "Abatimentos"]
        )
        if n:
            tbl = tbl.tail(n)
        return tbl


def ultimas_transac(n: int | None = prefs.settings.read_last_transacs_limit()):
    """
    Lista as ultimas `n` transacoes, comecando pela mais recente.
    Se `n=None`, retorna todas as transacoes.

    Nome das colunas:

    - `Data`
    - `Valor`
    - `Id do cliente`
    """

    stmt = f"""
    SELECT DataTransac, Valor, IdCliente
    FROM transacoes
    ORDER BY Id desc;
    """

    if n is not None:
        stmt = stmt.replace(";", f" LIMIT {n};")

    with Session(DB_ENGINE) as ses:
        result = ses.execute(text(stmt)).all()
        return pd.DataFrame(
            [res for res in result], columns=["Data", "Valor", "Id do cliente"]
        )


def nome_por_id(Id: int):
    c = cliente_por_id(Id=Id)
    if c.Apelido != "":
        return f"{c.PrimeiroNome} {c.Sobrenome} ({c.Apelido})"
    if c.Bairro != "":
        return f"{c.PrimeiroNome} {c.Sobrenome}, {c.Bairro}"
    return f"{c.PrimeiroNome} {c.Sobrenome}"


def local_por_id(Id: int) -> str:
    """Retorna um texto com informacoes de localizacao da conta selecionada"""
    try:
        c = cliente_por_id(Id=Id)
    except TypeError:
        # retorna string vazia se nao houverem cadastros
        return ""

    logradouro = ""
    if c.Endereco != "":
        logradouro = logradouro + f"{c.Endereco}, "
    if c.Bairro != "":
        logradouro = logradouro + f"{c.Bairro} - "
    return logradouro + f"{c.Cidade}/{c.Estado}"


def ultimas_transac_displ(n: int | None = prefs.settings.read_last_transacs_limit()):
    tbl = ultimas_transac(n=n)
    tbl["Cliente"] = pd.Series(map(nome_por_id, tbl["Id do cliente"]))
    tbl["Valor"] = tbl["Valor"].apply(lambda x: fmt_moeda(x, para_mostrar=True))
    tbl.drop("Id do cliente", axis="columns", inplace=True)
    return tbl


def rank_maiores_saldos(n=prefs.settings.read_highest_balaces_limit()):
    stmt = """
    SELECT IdCliente, SUM(Valor) AS Saldo
    FROM transacoes
    GROUP BY IdCliente
    ORDER BY Saldo DESC;
    """
    if n:
        stmt = stmt.replace(";", f" LIMIT {n};")

    with Session(DB_ENGINE) as ses:
        result = ses.execute(text(stmt)).all()

    tbl = pd.DataFrame([res for res in result], columns=["Cliente", "Saldo"])
    tbl["Cliente"] = pd.Series(map(nome_por_id, tbl["Cliente"]))
    tbl["Saldo"] = tbl["Saldo"].apply(lambda x: fmt_moeda(x, True))
    return tbl
