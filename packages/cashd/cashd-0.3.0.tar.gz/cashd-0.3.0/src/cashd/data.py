from sqlalchemy import (
    Column,
    Engine,
    ForeignKey,
    Select,
    create_engine,
    DateTime,
    Date,
    Numeric,
    Integer,
    String,
    cast,
    update,
    select,
    insert,
    delete,
    or_,
    case,
    text,
    func,
    types,
)
from sqlalchemy.orm import (
    Mapped,
    DeclarativeBase,
    relationship,
    Session,
)
from typing import List, Iterable, Literal, Any, Self, Dict
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from copy import copy
from sys import platform
import phonenumbers
import re

from cashd import prefs
from cashd.db import DB_ENGINE


####################
# CONSTANTS
####################

"""
if platform == "win32":
    CASHD_FILES_PATH = Path.home().joinpath("AppData", "Local", "Cashd")
    CONFIG_PATH = Path(CASHD_FILES_PATH, "configs")
    LOG_PATH = Path(CASHD_FILES_PATH, "logs")
else:
    CASHD_FILES_PATH = Path.home().joinpath(".local", "share", "Cashd")
    CONFIG_PATH = Path.home().joinpath(".config", "Cashd")
    LOG_PATH = Path.home().joinpath(".local", "state", "Cashd", "logs")

DATA_PATH = Path(CASHD_FILES_PATH, "data")
DATA_PATH.mkdir(exist_ok=True)
DB_ENGINE = create_engine(
    f"sqlite:///{Path(DATA_PATH, 'database.db')}", echo=False)
"""

NA_VALUE = "N/D"

####################
# VALIDATION
####################


class RequiredText(types.TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return fmt_text(value, required=True)

    def process_result_value(self, value, dialect):
        return value


class NotRequiredText(types.TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return fmt_text(value, required=False)

    def process_result_value(self, value, dialect):
        return value


class RequiredStateAcronym(types.TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return fmt_text(value, required=True).upper()

    def process_result_value(self, value, dialect):
        return value


class PhoneNumberText(types.TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return fmt_phonenumber(value)

    def process_result_value(self, value, dialect):
        return value


class CurrencyAmount(types.TypeDecorator):
    impl = Numeric
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return fmt_currency(value)

    def process_result_value(self, value, dialect):
        if value:
            return round(Decimal(value), 2)


REQUIRED_TYPES = [RequiredStateAcronym, RequiredText, PhoneNumberText]


def fmt_text(inp: str | None, required: bool = False) -> str:
    """Coerces input into a title cased string.

    :param inp: Input value
    :param required: Boolean value indicating if it is allowed to be empty.
    :raises ValueError: If it cannot be coerced to expected format.
    """
    if inp is None:
        inp = ""
    if required and (len(inp) == 0):
        raise ValueError("Campo obrigatório não pode ficar vazio")
    return inp.title()


def fmt_phonenumber(inp: str) -> str:
    """Coerces input into a formatted phone number.

    :param inp: Input value
    :raises ValueError: If it cannot be coerced to expected format.
    """
    try:
        return phonenumbers.format_number(
            numobj=phonenumbers.parse(inp, "BR"),
            num_format=phonenumbers.PhoneNumberFormat.NATIONAL,
        )
    except phonenumbers.NumberParseException:
        raise ValueError("Número de telefone inválido")


def fmt_currency(inp: Any) -> int:
    """Coerces input into a non-zero integer value used to store currency in db.

    :param inp: Input value
    :raises ValueError: If it cannot be coerced to expected format.
    """
    if isinstance(inp, (str)):
        inp = inp.replace(",", "").replace(".", "")
    if isinstance(inp, (Decimal, float)):
        inp = inp * 100
    return int(inp)


####################
# STRUCTURE + INTERACTION
####################


class dec_base(DeclarativeBase):
    Id = Column("Id", Integer, primary_key=True)

    @staticmethod
    def _display_name(name: str):
        """Wrapper to generate the *display name* of any data scalar in `self.data`."""
        return name

    @property
    def data(self) -> dict[str, Any]:
        return {
            colname: getattr(self, colname, None)
            for colname in self.__table__.c.keys()
            if colname != "Id"
        }

    @property
    def display_names(self) -> dict[str, Any]:
        return {
            colname: self._display_name(colname)
            for colname in self.__table__.c.keys()
            if colname != "Id"
        }

    @property
    def types(self) -> dict[str, Any]:
        return {
            colname: type(self.__table__.c[colname].type)
            for colname in self.__table__.c.keys()
            if colname != "Id"
        }

    def read(self, row_id: int, engine: Engine = DB_ENGINE):
        """
        Fetches one row of data from the database and loads into this instance.

        :param row_id: Primary key integer value to look for in the table.
        :param engine: `sqlalchemy.Engine` reflecting the database that will be read.

        :raises ValueError: If `row_id` is not present in the table.
        """
        cls = type(self)
        stmt = select(cls).where(cls.Id == row_id)
        with Session(bind=engine) as ses:
            res = ses.execute(stmt).first()
            if res is None:
                raise ValueError(
                    f"{row_id=} not present in '{
                        self.__tablename__}.Id'."
                )
            row = res[0]
            for col in self.__table__.columns:
                value = getattr(row, col.name, None)
                setattr(self, col.name, value)

    def clear(self):
        """Returns all dataclass fields to their defaults, and `Id=None`."""
        self.Id = None
        for name in self.data.keys():
            default_value = self.__table__.c[name].default
            setattr(self, name, default_value)

    def fill(self, tbl_obj: Self):
        """Fills own mapped columns with the custom values provided by `tbl_obj`."""
        self.Id = tbl_obj.Id
        for name, value in tbl_obj.data.items():
            setattr(self, name, value)

    def update(self, engine: Engine = DB_ENGINE):
        """If `self.Id` is defined, validates and updates the corresponding row in the
        database with it's own values.

        :raises AttributeError: If `self.Id` is None or not defined.
        """
        if not self.Id:
            raise AttributeError(f"Expected `self.Id` to be integer, got {self.Id=}.")
        cls = type(self)
        with Session(bind=engine) as ses:
            stmt = update(cls).where(cls.Id == self.Id).values(**self.data)
            ses.execute(stmt)
            ses.commit()
        self.read(row_id=self.Id, engine=engine)

    def write(self, engine: Engine = DB_ENGINE):
        """Validates and adds a new row in the database with it's own data."""
        cls = type(self)
        with Session(bind=engine) as ses:
            stmt = insert(cls).values(**self.data)
            ses.execute(stmt)
            ses.commit()

    def delete(self, engine: Engine = DB_ENGINE):
        """If `self.Id` is present in the database, attempts to delete it.

        :raises AttributeError: If `self.Id` is None or not defined.
        :raises sqlalchemy.exc.IntegrityError: If this deletion would leave orphaned
          foreign keys.
        """
        cls = type(self)
        with Session(bind=engine) as ses:
            stmt = delete(cls).where(cls.Id == self.Id)
            ses.execute(stmt)
            ses.commit()


class tbl_clientes(dec_base):
    __tablename__ = "clientes"
    SaldoTransacoes: Mapped[List["tbl_transacoes"]] = relationship()

    PrimeiroNome = Column("PrimeiroNome", RequiredText, nullable=False)
    Sobrenome = Column("Sobrenome", RequiredText, nullable=False)
    Apelido = Column("Apelido", NotRequiredText)
    Telefone = Column(
        "Telefone", PhoneNumberText, nullable=False, default="(99) 90000-0000"
    )
    Endereco = Column("Endereco", NotRequiredText)
    Bairro = Column("Bairro", NotRequiredText)
    Cidade = Column("Cidade", RequiredText, nullable=False)
    Estado = Column("Estado", RequiredStateAcronym, nullable=False)

    @property
    def Transacs(self) -> List[Dict]:
        """List with selected customer's transactions, most recent first."""
        customer_id = getattr(self, "Id", None)
        if not customer_id:
            return []
        stmt = (
            select(tbl_transacoes.Id, tbl_transacoes.DataTransac, tbl_transacoes.Valor)
            .where(tbl_transacoes.IdCliente == customer_id)
            .order_by(tbl_transacoes.Id.desc())
        )
        with Session(DB_ENGINE) as ses:
            res = ses.execute(stmt).all()
            return (
                {
                    "id": r.Id,
                    "data": r.DataTransac,
                    "valor": f"{r.Valor/100:.2f}".replace(".", ","),
                }
                for r in res
            )

    @property
    def NomeCompleto(self):
        if self.Id is None:
            return NA_VALUE
        nome_completo = f"{str(self.Id).zfill(3)}, {
            self.PrimeiroNome} {self.Sobrenome}"
        if self.Apelido != "":
            nome_completo = nome_completo + f" ({self.Apelido})"
        return nome_completo

    @property
    def Local(self):
        if self.Id is None:
            return NA_VALUE
        local = f"{self.Cidade}/{self.Estado}"
        if self.Bairro not in ["", None]:
            local = f"{self.Bairro}, {local}"
        if self.Endereco not in ["", None]:
            local = f"{self.Endereco} - {local}"
        return local

    @property
    def Saldo(self):
        customer_id = getattr(self, "Id", None)
        if customer_id is None:
            return NA_VALUE
        stmt = select(func.sum(tbl_transacoes.Valor)).where(
            tbl_transacoes.IdCliente == self.Id
        )
        with Session(DB_ENGINE) as ses:
            value = ses.execute(stmt).scalar_one()
            if value is None:
                return "0,00"
        return f"{value/100:.2f}".replace(".", ",")

    @staticmethod
    def _display_name(name):
        match name:
            case "PrimeiroNome":
                return "Primeiro Nome*"
            case "Sobrenome":
                return "Sobrenome*"
            case "Telefone":
                return "Telefone*"
            case "Cidade":
                return "Cidade*"
            case "Estado":
                return "Estado*"
            case "Endereco":
                return "Endereço"
            case _:
                return name

    def __repr__(self):
        Id, PrimeiroNome, Sobrenome = self.Id, self.PrimeiroNome, self.Sobrenome
        return f"<cashd customer {Id=}, {PrimeiroNome=}, {Sobrenome=}>"


class tbl_transacoes(dec_base):
    __tablename__ = "transacoes"
    NomeCliente: Mapped["tbl_clientes"] = relationship(back_populates="SaldoTransacoes")

    IdCliente: Mapped[int] = Column("IdCliente", ForeignKey("clientes.Id"))
    CarimboTempo: Mapped[datetime] = Column(DateTime(timezone=True))
    DataTransac = Column("DataTransac", Date)
    Valor = Column("Valor", CurrencyAmount)  # valor em centavos

    def __repr__(self):
        Id, Valor = self.Id, self.Valor
        return f"<cashd transaction {Id=}, {Valor=}>"


def get_default_customer() -> tbl_clientes:
    """Returns a customer filled with all current default values."""
    customer = tbl_clientes()
    customer.Telefone = "(99) 90000-0000"
    customer.Cidade = prefs.settings.default_city
    customer.Estado = prefs.settings.default_state
    return customer


dec_base.metadata.create_all(DB_ENGINE)


FORMATTED_FULL_CUSTOMER_NAME = case(
    (
        tbl_clientes.Apelido != "",
        func.printf(
            "%s, %s %s (%s)",
            tbl_clientes.Id,
            tbl_clientes.PrimeiroNome,
            tbl_clientes.Sobrenome,
            tbl_clientes.Apelido,
        ),
    ),
    else_=func.printf(
        "%s, %s %s",
        tbl_clientes.Id,
        tbl_clientes.PrimeiroNome,
        tbl_clientes.Sobrenome,
    ),
)
FORMATTED_FULL_CUSTOMER_LOCATION = case(
    (
        (tbl_clientes.Endereco != "") & (tbl_clientes.Bairro != ""),
        func.printf(
            "%s - %s, %s/%s",
            tbl_clientes.Endereco,
            tbl_clientes.Bairro,
            tbl_clientes.Cidade,
            tbl_clientes.Estado,
        ),
    ),
    (
        (tbl_clientes.Endereco == "") & (tbl_clientes.Bairro != ""),
        func.printf(
            "%s, %s/%s",
            tbl_clientes.Bairro,
            tbl_clientes.Cidade,
            tbl_clientes.Estado,
        ),
    ),
    (
        (tbl_clientes.Endereco != "") & (tbl_clientes.Bairro == ""),
        func.printf(
            "%s - %s/%s",
            tbl_clientes.Endereco,
            tbl_clientes.Cidade,
            tbl_clientes.Estado,
        ),
    ),
    else_=func.printf("%s/%s", tbl_clientes.Cidade, tbl_clientes.Estado),
)


def query_currency(
    value_query,
    label: str = "Value",
    decimal_sep: str = ",",
    convert_decimal: bool = True,
):
    """Converts numeric integer column query into a formatted currency text column. The
    decimal places are always truncated to 2.

    :param value_query: Input compatible with `sqlalchemy.select` that evaluates to an
      numeric integer column.
    :param label: Column label, equivalent to 'SELECT table.column_name AS Value ...',
      where `label='Value'`.
    :param decimal_sep: Decimal separator for the formatted currency data.
    :param convert_decimal: Should the column be divided by 100 to create decimal places?
    """
    div = 100 if convert_decimal else 1
    return func.replace(
        func.printf("%.2f", cast(value_query, Numeric) / div),
        text("'.'"),
        text(f"'{decimal_sep}'"),
    ).label(label)


class _DataSource:
    def __init__(
        self,
        select_stmt: Select,
        paginated: bool = True,
        searchable: bool = False,
        search_colnames: Iterable[str] = [],
        engine: Engine = DB_ENGINE,
    ):
        """Create a data class that interacts with the database, providing interaction
        capabilities to data widgets.

        :param select_stmt: A `sqlalchemy.sql.expression.Select` that selects the data
          managed by this data source.
        :param paginated: Wether this data source handle pagination.
        :param searchable: Wether this data source handles searches to subset the
          `select_stmt` results.
        :param search_colnames: Name of the columns where the search will be applied.
        :param engine: Engine pointing to the database where the data will be handled.

        :raises ValueError: If `searchable=True`, and `search_colnames` is an empty list,
          or if one of the selected column names are not present in the select query.
        """
        if searchable and (len(search_colnames) == 0):
            raise ValueError(
                "Expecting at least one search colname on searchable data source."
            )
        selected_colnames = select_stmt.selected_columns.keys()
        for col in search_colnames:
            if col not in selected_colnames:
                raise ValueError(
                    f"Expected all `search_colnames` to be present in {
                        selected_colnames}."
                )
        if paginated:
            self._current_page = 1
            self._rows_per_page = 100
        if searchable:
            self._search_text = ""
            self.SEARCH_COLNAMES = search_colnames
        self.SELECT_STMT = select_stmt
        self.ENGINE = engine
        self._fetch_metadata()

    def _fetch_metadata(self, search_text: str = ""):
        """Assigns values for attributes containing metadata for the current
        state of this class's `select_statement`:

        - :nrows: Number of rows in this data source. Affected by search text
          when the data source is searchable.

        If searchable:

        - :search_text: Text with all the keywords that will be inserted into the
          searched SELECT query.

        If paginated:

        - :min_idx: Index of the first item in the current page;
        - :max_idx: Index of the last item in the current page.

        :type search_text: ``str``
        :param search_text: Text with all the keywords that will be inserted into the
          searched SELECT query.
        """
        # `search_text`
        if self.is_searchable():
            self._search_text = search_text
        # `nrows`
        with Session(self.ENGINE) as ses:
            select_stmt = self.searched_select_stmt(search_text)
            nrows_stmt = select(func.count()).select_from(select_stmt.subquery())
            self.nrows = ses.execute(nrows_stmt).scalar()
        if self.is_paginated():
            # `min_idx`
            if self.nrows < self._rows_per_page:
                self.min_idx = 0
            else:
                self.min_idx = self._rows_per_page * (self.current_page - 1)
            # `max_idx`
            max_idx = self.current_page * self._rows_per_page
            if self.nrows < max_idx:
                self.max_idx = self.nrows
            else:
                self.max_idx = max_idx

    @property
    def current_data(self):
        """Assigns the data based on the current metadata values to
        `current_data`.
        """
        stmt = self.searched_select_stmt(search_text=self.search_text)
        if self.is_paginated():
            stmt = stmt.limit(self.rows_per_page).offset(self.min_idx)
        with Session(self.ENGINE) as ses:
            return ses.execute(stmt).all()

    def is_paginated(self) -> bool:
        try:
            _ = self._current_page
            return True
        except AttributeError:
            return False

    def is_searchable(self) -> bool:
        try:
            _ = self._search_text
            return True
        except AttributeError:
            return False

    def searched_select_stmt(self, search_text: str = "") -> Select:
        """If this is a searchable data source, adds a search logic to `self.SELECT_STMT`
        and returns it. Returns only `self.SELECT_STMT` otherwise, or if `search_text`
        is an empty string.

        :param search_text: Text with all the keywords that will be inserted into the
          searched SELECT query.
        """
        if not self.is_searchable() or (search_text == ""):
            return self.SELECT_STMT
        keywords = re.findall(r"\w+", search_text)
        stmt = copy(self.SELECT_STMT)
        for kw in keywords:
            kw_in_cols = [
                self.SELECT_STMT.selected_columns[col].ilike(f"%{kw}%")
                for col in self.SEARCH_COLNAMES
            ]
            stmt = stmt.where(or_(*kw_in_cols))
        return stmt

    @property
    def current_page(self) -> int:
        """Current page number."""
        if not self.is_paginated():
            raise AttributeError(
                "Cannot get 'current_page' on a data source without pagination."
            )
        return self._current_page

    @property
    def rows_per_page(self) -> int:
        self._rows_per_page = 100
        return self._rows_per_page

    def fetch_next_page(self):
        """Advances one page and update `current_data`. Does nothing if already
        on last page.
        """
        if self.max_idx == self.nrows:
            return
        self._current_page = self._current_page + 1
        self._fetch_metadata()

    def fetch_previous_page(self):
        """Backtracks one page and update `current_data`. Does nothing if already
        on first page.
        """
        if self._current_page == 1:
            return
        self._current_page = self._current_page - 1
        self._fetch_metadata()

    def update_date_format(self, date_freq: Literal["m", "w", "d"]):
        """Updates `self.SELECT_STMT` to reflect the date frequency requested. Does
        nothing if the data source can't accept date frequency updates, or if `date_freq`
        is not one of ['m', 'w', 'd'].
        """
        pass

    @property
    def search_text(self) -> str:
        """If searchable, returns the last provided `search_text`, or an empty
        string otherwise. When set, update `self` metadata based on the search performed.
        """
        return getattr(self, "_search_text", "")

    @search_text.setter
    def search_text(self, value: str):
        if self.is_searchable():
            self._search_text = value
            self._fetch_metadata(search_text=value)


class LastTransactionsSource(_DataSource):
    def __init__(self, engine: Engine = DB_ENGINE):
        """Manages database interaction on for 'Last Transactions' data,
        with columns:

        :Data: Transaction date
        :Cliente: Customer name formatted as
          "`{Id},  {FirstName} {LastName} ({Nickname})`" whit nickname
          present, or "`{Id},  {FirstName} {LastName}`" otherwise.
        :Valor: Transaction amount.
        """
        select_stmt = (
            select(
                tbl_transacoes.DataTransac.label("Data"),
                FORMATTED_FULL_CUSTOMER_NAME,
                query_currency(tbl_transacoes.Valor, label="Valor"),
            )
            .join(tbl_clientes, tbl_transacoes.IdCliente == tbl_clientes.Id)
            .order_by(tbl_transacoes.Id.desc())
        )
        super().__init__(
            select_stmt,
            paginated=True,
            searchable=False,
            search_colnames=[],
            engine=engine,
        )


class CustomerListSource(_DataSource):
    def __init__(self, engine=DB_ENGINE):
        """Manages database interaction on for 'Customer List' data,
        with columns:

        - **Id** Customer Id;
        - **Name** Customer name formatted as
          - "`{Id},  {FirstName} {LastName} ({Nickname})`" whit nickname present,
          - or "`{Id},  {FirstName} {LastName}`" otherwise;
        - **Place** Customer location formatted as
          - "`{Address} - {District}, {City}/{State}`" when all fields are present,
          - "`{District}, {City}/{State}`" when Address is missing,
          - "`{Address} - {City}/{State}`" when District is missing,
          - or just "`{City}/{State}`" when they are both missing.
        """
        select_stmt = select(
            tbl_clientes.Id.label("Id"),
            FORMATTED_FULL_CUSTOMER_NAME.label("Name"),
            FORMATTED_FULL_CUSTOMER_LOCATION.label("Place"),
        )
        super().__init__(
            select_stmt=select_stmt,
            paginated=True,
            searchable=True,
            search_colnames=["Name", "Place"],
            engine=engine,
        )


class HighestAmountsSource(_DataSource):
    def __init__(self, engine: Engine = DB_ENGINE):
        """Manages database interaction on for 'Highest Owed Amounts' data,
        with columns:

        - **Name** Customer name formatted as
        "`{Id},  {FirstName} {LastName} ({Nickname})`" whit nickname
        present, or "`{Id},  {FirstName} {LastName}`" otherwise.
        - **OwedAmount** Total amount owed by the customer.
        """
        select_stmt = (
            select(
                FORMATTED_FULL_CUSTOMER_NAME.label("Name"),
                query_currency(func.sum(tbl_transacoes.Valor), label="OwedAmount"),
            )
            .join(tbl_clientes, tbl_transacoes.IdCliente == tbl_clientes.Id)
            .group_by(tbl_clientes.Id)
            .order_by(func.sum(tbl_transacoes.Valor).desc())
        )
        super().__init__(
            select_stmt=select_stmt,
            paginated=True,
            searchable=False,
            search_colnames=[],
            engine=engine,
        )


class InactiveCustomersSource(_DataSource):
    def __init__(self, engine: Engine = DB_ENGINE):
        """Manages database interaction on for 'Inactive Customers' data,
        with columns:

        - **Name** Customer name formatted as
        "`{Id},  {FirstName} {LastName} ({Nickname})`" whit nickname
        present, or "`{Id},  {FirstName} {LastName}`" otherwise.
        - **LastTransac** Date of last transaction performed by the customer.
        - **OwedAmount** Total amount owed by the customer.
        """
        select_stmt = (
            select(
                FORMATTED_FULL_CUSTOMER_NAME.label("Name"),
                func.max(tbl_transacoes.DataTransac).label("LastTransac"),
                query_currency(func.sum(tbl_transacoes.Valor), label="OwedAmount"),
            )
            .join(tbl_clientes, tbl_transacoes.IdCliente == tbl_clientes.Id)
            .group_by(tbl_clientes.Id)
            .order_by(func.max(tbl_transacoes.DataTransac))
        )
        super().__init__(
            select_stmt=select_stmt,
            paginated=True,
            searchable=False,
            search_colnames=[],
            engine=engine,
        )


class TransactionBalanceSource(_DataSource):
    sums_col = func.sum(case((tbl_transacoes.Valor > 0, tbl_transacoes.Valor)))
    deductions_col = func.sum(case((tbl_transacoes.Valor < 0, tbl_transacoes.Valor)))
    balance_col = func.sum(tbl_transacoes.Valor)

    def __init__(self, engine: Engine = DB_ENGINE):
        """Manages database interaction on for 'Transaction Balance' data,
        with columns:

        :Date: Transaction date, might be an interval of month, week or day
          formatted as YYYY-MM, YYYY-WW or YYYY-MM-DD, respectively.
        :Sums: Total amount of all purchases registered.
        :Deductions: Total amount of all payments registered.
        :Balance: Sums + (-Deductions).
        """
        # initial date frequency is monthlhy
        date_col = func.strftime("%Y-%m", tbl_transacoes.DataTransac).label("Date")
        select_stmt = (
            select(
                date_col,
                query_currency(self.sums_col, label="Sums"),
                query_currency(self.deductions_col, label="Deductions"),
                query_currency(self.balance_col, label="Balance"),
            )
            .group_by(date_col)
            .order_by(date_col.desc())
        )
        super().__init__(
            select_stmt=select_stmt,
            paginated=True,
            searchable=False,
            search_colnames=[],
            engine=engine,
        )

    def update_date_format(self, date_freq: Literal["m", "w", "d"]):
        date_format = "%Y-%m"
        if date_freq == "w":
            date_format = "%Y-%W"
        if date_freq == "d":
            date_format = "%Y-%m-%d"
        date_col = func.strftime(date_format, tbl_transacoes.DataTransac).label("Date")
        self.SELECT_STMT = (
            select(
                date_col,
                query_currency(self.sums_col, label="Sums"),
                query_currency(self.deductions_col, label="Deductions"),
                query_currency(self.balance_col, label="Balance"),
            )
            .group_by(date_col)
            .order_by(date_col.desc())
        )


class AggregatedAmountSource(_DataSource):
    sums_col = func.sum(case((tbl_transacoes.Valor > 0, tbl_transacoes.Valor)))
    deductions_col = func.sum(case((tbl_transacoes.Valor < 0, tbl_transacoes.Valor)))

    def __init__(self, engine: Engine = DB_ENGINE):
        """Manages database interaction on for 'Transaction Balance' data,
        with columns:

        :Date: Transaction date, might be an interval of month, week or day
          formatted as YYYY-MM, YYYY-WW or YYYY-MM-DD, respectively.
        :Sums: Total amount of all purchases registered.
        :Deductions: Total amount of all payments registered.
        :AcumBalance: Sums + (-Deductions) aggregated over time.
        """
        date_col = func.strftime("%Y-%m", tbl_transacoes.DataTransac).label("Date")
        acum_balance_col = query_currency(
            func.sum(self.sums_col + self.deductions_col).over(order_by=date_col.asc()),
            label="AcumBalance",
        )
        select_stmt = (
            select(
                date_col,
                query_currency(self.sums_col, label="Sums"),
                query_currency(self.deductions_col, label="Deductions"),
                acum_balance_col,
            )
            .group_by(date_col)
            .order_by(date_col.desc())
        )
        super().__init__(
            select_stmt=select_stmt,
            paginated=True,
            searchable=False,
            search_colnames=[],
            engine=engine,
        )

    def update_date_format(self, date_freq: Literal["m", "w", "d"]):
        date_format = "%Y-%m"
        if date_freq == "w":
            date_format = "%Y-%W"
        if date_freq == "d":
            date_format = "%Y-%m-%d"
        date_col = func.strftime(date_format, tbl_transacoes.DataTransac).label("Date")
        acum_balance_col = query_currency(
            func.sum(self.sums_col + self.deductions_col).over(order_by=date_col.asc()),
            label="AcumBalance",
        )
        self.SELECT_STMT = (
            select(
                date_col,
                query_currency(self.sums_col, label="Sums"),
                query_currency(self.deductions_col, label="Deductions"),
                acum_balance_col,
            )
            .group_by(date_col)
            .order_by(date_col.desc())
        )
