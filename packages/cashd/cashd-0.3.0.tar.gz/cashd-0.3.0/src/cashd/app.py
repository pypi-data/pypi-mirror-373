from typing import Literal, Type
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
from tkinter.filedialog import askopenfilename
from pyshortcuts import make_shortcut
from os import path
import pandas as pd
import threading
import webview
import socket
import sys

from taipy.gui import Gui, notify, State, navigate, Icon, builder

from cashd import db, backup, plot, prefs, data
from cashd.pages import transac, contas, analise, configs, dialogo



PYTHON_PATH = path.dirname(sys.executable)


####################
# BOTOES
####################

def btn_next_page_customer_search(state: State):
    usuarios = getattr(state, "usuarios", data.CustomerListSource())
    usuarios.fetch_next_page()
    update_search_widgets(state=state)


def btn_prev_page_customer_search(state: State):
    usuarios = getattr(state, "usuarios", data.CustomerListSource())
    usuarios.fetch_previous_page()
    update_search_widgets(state=state)


def btn_next_page_displayed_table(state: State):
    tablename = state.dropdown_table_type_val
    selected_source = fetch_displayed_table_datasource(state=state, tablename=tablename)
    selected_source.fetch_next_page()
    chg_select_table_stats(state=state)


def btn_prev_page_displayed_table(state: State):
    tablename = state.dropdown_table_type_val
    selected_source = fetch_displayed_table_datasource(state=state, tablename=tablename)
    selected_source.fetch_previous_page()
    chg_select_table_stats(state=state)


def btn_mostrar_dialogo(state: State, id: str, payload: dict, show: str):
    show_dialogs = {
        "confirma_conta": "mostra_confirma_conta",
        "confirma_transac": "mostra_confirma_transac",
        "selec_cliente": "mostra_selec_cliente",
        "edita_cliente": "mostra_form_editar_cliente",
        "selec_transac": "mostra_selec_transac",
    }
    for dialog in show_dialogs.values():
        state.assign(dialog, False)
    state.assign(show_dialogs[show], True)


def btn_mostrar_dialogo_selec_cliente(state: State, id: str, payload: dict):
    btn_mostrar_dialogo(state, id, payload, show="selec_cliente")


def btn_mostrar_dialogo_edita_cliente(state: State, id: str, payload: dict):
    btn_mostrar_dialogo(state, id, payload, show="edita_cliente")


def btn_mostrar_dialogo_selec_transac(state: State, id: str, payload: dict):
    state.assign(
        "TRANSACS_USUARIO",
        db.listar_transac_cliente(state.SLC_USUARIO[0], para_mostrar=False),
    )
    btn_mostrar_dialogo(state, id, payload, "selec_transac")


def btn_atualizar_listagem(state: State):
    with db.DB_ENGINE.connect() as conn, conn.begin():
        state.df_clientes = pd.read_sql_query("SELECT * FROM clientes", con=conn)


def btn_gerar_main_plot(state: State | None = None):
    """
    Se `state=None` retorna um `plotly.graph_objects.Figure`, caso contrario, atualiza o valor
    de `'main_plot'`."""

    if state:
        p = state.dropdown_periodo_val[0]
        n = int(state.slider_val[0])
        tipo = state.dropdown_plot_type_val
    else:
        p = dropdown_periodo_val[0]
        n = int(slider_val[0])
        tipo = dropdown_plot_type_val

    if tipo == "Saldo Acumulado":
        fig = plot.saldo_acum(periodo=p, n=n)
    else:
        fig = plot.balancos(periodo=p, n=n)

    if state:
        state.assign("main_plot", fig)
        state.refresh("main_plot")
        return
    return


def btn_atualizar_df_ult_transac(state: State):
    try:
        updated_tbl = db.ultimas_transac_displ()
        state.assign("df_ult_transac", updated_tbl)
    except Exception as xpt:
        notify(state, "error", f"Erro inesperado atualizando a tabela: {str(xpt)}")


def btn_atualizar_locais_de_backup(state: State | None = None):
    """
    Se `state=None` retorna um `pd.DataFrame`, caso contrario, atualiza o valor
    de `'df_locais_de_backup'`."""
    locais_de_backup = backup.settings.read_backup_places()
    df = pd.DataFrame(
        {"Id": range(len(locais_de_backup)), "Locais de backup": locais_de_backup}
    )
    if state:
        state.assign("df_locais_de_backup", df)
        state.refresh("df_locais_de_backup")
        return
    return df


def btn_fazer_backups(state: State):
    try:
        backup.run(force=True, _raise=True)
        notify(state, "success", "Backup concluído!")
    except Exception as xpt:
        notify(state, "error", str(xpt))


def btn_add_local_de_backup(state: State):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    folder = filedialog.askdirectory()
    backup.settings.add_backup_place(folder)
    btn_atualizar_locais_de_backup(state)


def btn_rm_local_de_backup(state: State, var_name, payload):
    idx = int(payload["index"])
    backup.settings.rm_backup_place(idx)
    btn_atualizar_locais_de_backup(state)


def btn_carregar_backup(state: State):
    filename = askopenfilename()
    try:
        backup.load(file=filename, _raise=True)
        notify(state, "success", "Dados carregados com sucesso")
    except OSError:
        notify(state, "error", "Arquivo selecionado não é um banco de dados SQLite")
    except Exception as xpt:
        notify(state, "error", f"Erro inesperado carregando arquivo: {xpt}")


def btn_criar_atalho(state: State):
    ico_file = path.join(backup.SCRIPT_PATH, "assets", "ICO_LogoIcone.ico")
    startup_script = path.join(PYTHON_PATH, "cashd.exe")
    if not path.isfile(startup_script):
        startup_script = path.join(PYTHON_PATH, "Scripts", "cashd.exe")

    make_shortcut(
        script=startup_script,
        icon=ico_file,
        name="Cashd",
        description="Registre seu fluxo de caixa rapidamente e tenha total controle dos seus dados!",
        terminal=False,
        desktop=True,
        startmenu=True,
    )
    notify(state, "success", "Atalho criado com sucesso!")


def btn_inserir_transac(state: State):
    carregar_lista_transac(state)
    try:
        state.form_transac.DataTransac = state.display_tr_data
        nova_transac: dict = state.form_transac.despejar()
        state.form_transac.Valor = ""
        agora = datetime.now()

        db.adicionar_transac(db.tbl_transacoes(CarimboTempo=agora, **nova_transac))
        notify(state, "success", f"Nova transação adicionada!")

        id_selecionado = int(nova_transac["IdCliente"])
        state.assign("SLC_USUARIO", state.NOMES_USUARIOS[id_selecionado - 1])
        state.assign("display_tr_valor", "0,00")
        state.refresh("form_transac")
    except Exception as msg_erro:
        notify(state, "error", str(msg_erro))


def btn_inserir_cliente(state: State):
    try:
        novo_cliente: db.FormContas = state.form_contas.despejar()
        state.form_contas.__init__()
        db.adicionar_cliente(db.tbl_clientes(**novo_cliente))

        nome_completo = f"{novo_cliente['PrimeiroNome']} {
            novo_cliente['Sobrenome']}"
        notify(state, "success", message=f"Novo cliente adicionado!\n{nome_completo}")
        state.refresh("form_contas")
        state.NOMES_USUARIOS = sel_listar_clientes()
    except Exception as msg_erro:
        notify(state, "error", str(msg_erro))


def btn_chg_prefs_main_state(state: State, val: str):
    try:
        prefs.settings.write_main_state(val)
        state.form_contas.Estado = val
        state.refresh("form_contas")
        notify(state, "success", f"Estado preferido atualizado para {val}")
    except Exception as xpt:
        notify(state, "error", f"Erro inesperado: {str(xpt)}")


def btn_chg_prefs_main_city(state: State, val: str):
    try:
        val = val.title()
        prefs.settings.write_main_city(val)
        state.input_cidade_val = val
        state.form_contas.Cidade = val
        state.refresh("form_contas")
        notify(state, "success", f"Cidade preferida atualizada para {val}")
    except Exception as xpt:
        notify(state, "error", f"Erro inesperado: {str(xpt)}")


def btn_chg_max_ultimas_transacs(state: State, val: int):
    try:
        val = int(val)
        prefs.settings.write_last_transacs_limit(val)
        btn_atualizar_df_ult_transac(state)
        notify(
            state,
            "success",
            f"Limite de entradas em 'Últimas transações' atualizado para {
                val}",
        )
    except Exception as xpt:
        notify(state, "error", f"Erro inesperado: {str(xpt)}")


def btn_chg_max_highest_balances(state: State, val: int):
    try:
        val = int(val)
        prefs.settings.write_highest_balaces_limit(val)
        state.df_maiores_saldos = db.rank_maiores_saldos(val)
        notify(
            state,
            "success",
            f"Limite de entradas em 'Maiores saldos' atualizado para {val}",
        )
    except Exception as xpt:
        notify(state, "error", f"Erro inesperado: {str(xpt)}")


def tggl_backup_on_exit(state: State | None = None):
    if not state:
        return backup.settings.read_backup_on_exit()
    val = state.toggle_backup_on_exit
    backup.settings.write_backup_on_exit(val)


def btn_encerrar():
    try:
        backup.run(force=False, _raise=False)
        window.destroy()
    except NameError:
        window = webview.active_window()
        window.destroy()
    finally:
        raise KeyboardInterrupt("Encerrando...")


def btn_mudar_maximizado():
    window.toggle_fullscreen()


def btn_mudar_minimizado():
    window.minimize()


####################
# UTILS
####################


def carregar_lista_transac(state: State):
    elems = db.listar_transac_cliente(state.SLC_USUARIO[0])
    state.df_transac = elems["df"]
    state.SLC_USUARIO_SALDO = elems["saldo"]
    state.SLC_USUARIO_LOCAL = elems["local"]
    state.refresh("df_transac")
    state.refresh("SLC_USUARIO_SALDO")


def sel_listar_clientes():
    clientes = db.listar_clientes()
    return [(str(i["id"]), i["nome"]) for i in clientes]


def menu_lateral(state, action, info):
    page = info["args"][0]
    navigate(state, to=page)


def update_search_widgets(state: State):
    with state as s:
        s.NOMES_USUARIOS = [
            (str(row[0]), f"{row[1]} — {row[2]}") for row in usuarios.current_data
        ]
        s.search_user_pagination_legend = (
            f"{usuarios.nrows} itens, "
            f"mostrando {usuarios.min_idx + 1} até {usuarios.max_idx}"
        )


def fetch_displayed_table_datasource(
        state: State,
        tablename = Literal["Últimas transações", "Maiores saldos", "Clientes inativos"]
    ) -> Type[data._DataSource] | None:
    source_names = {
        "Últimas transações": "last_transacs_data_source",
        "Maiores saldos": "highest_amounts_data_source",
        "Clientes inativos": "inactive_customers_data_source",
    }
    sources = {
        "Últimas transações": last_transacs_data_source,
        "Maiores saldos": highest_amounts_data_source,
        "Clientes inativos": inactive_customers_data_source,
    }
    selected_source = getattr(state, source_names[tablename], None)
    if selected_source is None:
        selected_source = sources.get(tablename)
    return selected_source


def update_displayed_table_pagination(
        state: State,
        tablename = Literal["Últimas transações", "Maiores saldos", "Clientes inativos"]
    ):
    selected_source = fetch_displayed_table_datasource(state=state, tablename=tablename)
    selected_source._fetch_metadata()
    state.stats_tables_pagination_legend = (
        f"{selected_source.nrows} itens, "
        f"mostrando {selected_source.min_idx + 1} até {selected_source.max_idx}"
    )

####################
# ON ACTION
####################


def chg_dialog_selec_cliente_conta(state: State, id: str, payload: dict):
    with state as s:
        if payload["args"][0] < 1:
            s.assign("mostra_selec_cliente", False)

        if payload["args"][0] == 1:
            if s.SLC_USUARIO[0] == "0":
                notify(s, "error", "Nenhuma conta foi selecionada")
            else:
                cliente_selec = db.cliente_por_id(s.SLC_USUARIO[0])
                s.form_conta_selec.carregar_valores(cliente_selec)
                s.refresh("form_conta_selec")
                s.assign("mostra_selec_cliente", False)
                s.assign("mostra_form_editar_cliente", True)


def chg_dialog_editar_cliente(state: State, id: str, payload: dict):
    with state as s:
        if payload["args"][0] == -1:
            s.assign("mostra_selec_cliente", False)

        if payload["args"][0] == 0:
            s.assign("mostra_form_editar_cliente", False)
            s.assign("mostra_selec_cliente", True)

        if payload["args"][0] == 1:
            s.assign("mostra_form_editar_cliente", False)
            s.assign("mostra_confirma_conta", True)


def chg_dialog_confirma_cliente(state: State, id: str, payload: dict):
    with state as s:
        if payload["args"][0] == 1:
            try:
                db.atualizar_cliente(state.SLC_USUARIO[0], state.form_conta_selec)
                state.NOMES_USUARIOS = sel_listar_clientes()
                notify(s, "success", "Cadastro atualizado com sucesso!")
            except Exception as xpt:
                notify(s, "error", f"Erro ao atualizar cadastro: {str(xpt)}")
                s.assign("mostra_confirma_conta", False)

        s.assign("mostra_confirma_conta", False)


def chg_dialog_selec_transac(state: State, id: str, payload: dict):
    with state as s:
        if payload["args"][0] < 1:
            s.assign("mostra_selec_transac", False)

        if payload["args"][0] == 1:
            if s.SLC_TRANSAC == "0":
                notify(s, "error", "Nenhuma transação foi selecionada")
            elif not db.id_transac_pertence_a_cliente(
                s.SLC_TRANSAC[0], s.SLC_USUARIO[0]
            ):
                notify(s, "error", "Selecione uma transação antes de continuar")
                return
            else:
                transac_selec = db.transac_por_id(s.SLC_TRANSAC[0])
                s.form_transac_selec.carregar_valores(transac_selec)
                s.refresh("form_transac_selec")
                s.assign("mostra_confirma_transac", True)
        s.assign("mostra_selec_transac", False)


def chg_dialog_confirma_transac(state: State, id: str, payload: dict):
    with state as s:
        s.assign("mostra_confirma_transac", False)

        if payload["args"][0] == 0:
            s.assign("mostra_selec_transac", True)

        if payload["args"][0] == 1:
            db.remover_transac(s.SLC_TRANSAC[0])
            notify(s, "success", "Transação removida.")
            s.assign("SLC_TRANSAC", "0")


def chg_transac_valor(state: State) -> None:
    state.display_tr_valor = db.fmt_moeda(state.form_transac.Valor, para_mostrar=True)
    state.refresh("form_transac")
    return


def chg_select_table_stats(state: State):
    source_names = {
        "Últimas transações": "last_transacs_data_source",
        "Maiores saldos": "highest_amounts_data_source",
        "Clientes inativos": "inactive_customers_data_source",
    }
    sources = {
        "Últimas transações": last_transacs_data_source,
        "Maiores saldos": highest_amounts_data_source,
        "Clientes inativos": inactive_customers_data_source,
    }
    table_partials = {
        "Últimas transações": analise.ELEM_TABLE_TRANSAC_HIST,
        "Maiores saldos": analise.ELEM_TABLE_HIGHEST_AMOUNTS,
        "Clientes inativos": analise.ELEM_TABLE_INACTIVE_CUSTOMERS,
    }
    dataframe_names = {
        "Últimas transações": "df_last_transacs",
        "Maiores saldos": "df_highest_amounts",
        "Clientes inativos": "df_inactive_customers",
    }
    # Get option selected in the dropdown
    tablename = state.dropdown_table_type_val
    # Fetch datasource from state, if not available, use local datasource
    selected_source = fetch_displayed_table_datasource(state=state, tablename=tablename)
    if selected_source is None:
        return
    # Assign newest data to dataframe
    df = getattr(state, dataframe_names[tablename])
    df = pd.DataFrame(data=selected_source.current_data, columns=df.columns)
    state.assign(dataframe_names[tablename], df)
    # Update pagination label
    update_displayed_table_pagination(state=state, tablename=tablename)
    # Ensure datasource is assigned to state
    state.assign(name=source_names[tablename], value=sources[tablename])
    # Display selected dataframe
    state.part_stats_displayed_table.update_content(state, table_partials[tablename])


def chg_cliente_selecionado(state: State) -> None:
    carregar_lista_transac(state=state)
    state.form_transac.IdCliente = int(state.SLC_USUARIO[0])
    state.nome_cliente_selec = state.SLC_USUARIO[1]
    state.refresh("form_transac")


def chg_cliente_pesquisa(state: State, id, payload):
    usuarios = getattr(state, "usuarios", data.CustomerListSource())
    with state as s:
        usuarios.search_text = s.search_user_input_value
        update_search_widgets(state=state)
        s.usuarios = usuarios


####################
# VALORES INICIAIS
####################

# visibilidade de dialogos
mostra_selec_cliente = False
mostra_selec_transac = False
mostra_form_editar_cliente = False
mostra_confirma_conta = False
mostra_confirma_transac = False

# controles dos graficos
slider_elems = list(range(10, 51)) + [None]
slider_lov = [(str(i), str(i)) if i is not None else (i, "Tudo") for i in slider_elems]
slider_val = slider_lov[0]

dropdown_periodo_lov = [("mes", "Mensal"), ("sem", "Semanal"), ("dia", "Diário")]
dropdown_periodo_val = dropdown_periodo_lov[0]

dropdown_plot_type_val = "Balanço"

dropdown_uf_lov = [
    "AC",
    "AL",
    "AP",
    "AM",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MT",
    "MS",
    "MG",
    "PA",
    "PB",
    "PE",
    "PI",
    "PR",
    "RJ",
    "RN",
    "RO",
    "RR",
    "RS",
    "SC",
    "SE",
    "SP",
    "TO",
]
dropdown_uf_val = prefs.settings.read_main_state()

main_plot = btn_gerar_main_plot()

# campo de pesquisa de clientes
search_user_input_value = ""

# listagem de clientes
with db.DB_ENGINE.connect() as conn, conn.begin():
    df_clientes = pd.read_sql_query("SELECT * FROM clientes", con=conn)

# valor inicial dos campos "Valor" e "Data" no menu "Adicionar Transacao"
display_tr_valor = "0,00"
display_tr_data = datetime.now()

# valor inicial do seletor de conta global
usuarios = data.CustomerListSource()
usuarios.search_text = search_user_input_value

NOMES_USUARIOS = [
    (str(row[0]), f"{row[1]} — {row[2]}") for row in usuarios.current_data
]
if len(NOMES_USUARIOS) > 0:
    SLC_USUARIO = NOMES_USUARIOS[0]
else:
    SLC_USUARIO = "0"

# texto de paginação da pesquisa de clientes
search_user_pagination_legend = (
    f"{usuarios.nrows} itens, mostrando 1 até {usuarios.max_idx}"
)

# formularios
form_contas = db.FormContas()
form_transac = db.FormTransac(IdCliente=SLC_USUARIO[0])
form_conta_selec = db.FormContas()
form_transac_selec = db.FormTransac(IdCliente=SLC_USUARIO[0])


# nome do cliente selecionado
nome_cliente_selec = ""

# valor inicial do seletor de transacao global
TRANSACS_USUARIO = db.listar_transac_cliente(SLC_USUARIO[0], para_mostrar=False)
if len(TRANSACS_USUARIO) > 0:
    SLC_TRANSAC = TRANSACS_USUARIO[0]
else:
    SLC_TRANSAC = "0"

# define se a webview vai iniciar em tela cheia
maximizado = False

# valor inicial da tabela de transacoes do usuario selecionado em SLC_USUARIO
last_transacs_data_source = data.LastTransactionsSource()
highest_amounts_data_source = data.HighestAmountsSource()
inactive_customers_data_source = data.InactiveCustomersSource()

df_last_transacs = pd.DataFrame(
    data=last_transacs_data_source.current_data,
    columns=["Data", "Cliente", "Valor"],
)
df_highest_amounts = pd.DataFrame(
    data=highest_amounts_data_source.current_data,
    columns=["Nome", "Saldo devedor"],
)
df_inactive_customers = pd.DataFrame(
    data=inactive_customers_data_source.current_data,
    columns=["Nome", "Última transação", "Saldo devedor"],
)

dropdown_table_type_val = "Últimas transações"
stats_tables_pagination_legend = (
    f"{last_transacs_data_source.nrows} itens, mostrando "
    f"{last_transacs_data_source.min_idx + 1} até {last_transacs_data_source.max_idx}"
)

# valor inicial do saldo do usuario selecionado em SLC_USUARIO
init_meta_cliente = db.listar_transac_cliente(SLC_USUARIO[0])

df_transac = init_meta_cliente["df"]
SLC_USUARIO_SALDO = init_meta_cliente["saldo"]
SLC_USUARIO_LOCAL = init_meta_cliente["local"]

# valor inicial da lista de locais de backup
df_locais_de_backup = btn_atualizar_locais_de_backup()

# valor inicial do campo "cidade preferida"
input_cidade_val = prefs.settings.read_main_city()

# valor inicial da configuracao Limite de linhas na tabela "Últimas transações"
input_quant_max_ultimas_transacs = prefs.settings.read_last_transacs_limit()
#                    " " "                       na tabela "Maiores saldos"
input_quant_max_highest_balances = prefs.settings.read_highest_balaces_limit()

# valor inicial do toggle "backup ao sair"
toggle_backup_on_exit = tggl_backup_on_exit()

# dados de entradas e abatimentos
df_entradas_abatimentos = db.saldos_transac_periodo()
layout_df_entradas_abatimentos = {
    "x": "Data",
    "y[1]": "Somas",
    "y[2]": "Abatimentos",
    "layout": {
        "barmode": "overlay",
        "barcornerradius": "20%",
        "hovermode": "x unified",
        "hovertemplate": "<b>Total</b>: R$ %{y:.2f}",
    },
}
config_df_entradas_abatimentos = {"displaymodebar": False}


RAIZ = """
<|menu|label=Menu|width=200px|lov={("transacoes", Icon("assets/SVG_TransacaoBranco.svg", "Transações")), ("clientes", Icon("assets/SVG_ContasBranco.svg", "Clientes")), ("analise", Icon("assets/SVG_DadosBranco.svg", "Estatísticas")), ("configs", Icon("assets/SVG_ConfiguracaoBranco.svg", "Configurações"))}|on_action=menu_lateral|>
"""


paginas = {
    "/": RAIZ,
    "transacoes": transac.PG_TRANSAC,
    "clientes": contas.PG_CONTAS,
    "analise": analise.PG_ANALISE,
    "configs": configs.PG_CONFIG,
}

app = Gui(pages=paginas)

elem_transac_sel = Gui.add_partial(app, transac.ELEMENTO_SELEC_CONTA)
elem_transac_form = Gui.add_partial(app, transac.ELEMENTO_FORM)
elem_conta = Gui.add_partial(app, contas.ELEMENTO_FORM)
elem_config = Gui.add_partial(app, configs.ELEMENTO_PREFS)
elem_analise = Gui.add_partial(app, analise.ELEM_TABLES)

dial_selec_cliente = Gui.add_partial(app, dialogo.SELECIONAR_CLIENTE_ETAPA)
dial_selec_transac = Gui.add_partial(app, dialogo.SELECIONAR_TRANSAC_ETAPA)
dial_form_editar_cliente = Gui.add_partial(app, dialogo.FORM_EDITAR_CLIENTE)
dial_transac_confirmar = Gui.add_partial(app, dialogo.CONFIRMAR_TRANSAC)
dial_conta_confirmar = Gui.add_partial(app, dialogo.CONFIRMAR_CONTA)

part_stats_displayed_table = Gui.add_partial(app, analise.ELEM_TABLE_TRANSAC_HIST)

### menus de navegacao ###
# transacoes
nav_transac_lov = [
    (transac.ELEMENTO_FORM, "Adicionar transação"),
    (transac.ELEMENTO_HIST, "Ver histórico"),
]
nav_transac_val = nav_transac_lov[0]
# contas
nav_conta_lov = [
    (contas.ELEMENTO_FORM, "Criar conta"),
    (contas.ELEMENTO_REGS, "Contas registradas"),
]
nav_conta_val = nav_conta_lov[0]
# estatisticas
nav_analise_lov = [(analise.ELEM_TABLES, "Tabelas"), (analise.ELEM_PLOT, "Gráficos")]
nav_analise_val = nav_analise_lov[0]
# configs
nav_config_lov = [
    (configs.ELEMENTO_PREFS, "Preferências"),
    (configs.ELEMENTO_BACKUP, "Backup"),
    (configs.ELEMENTO_ATALHO, "Outros"),
]
nav_config_val = nav_config_lov[0]


def porta_aberta() -> int:
    port = 5000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        for i in range(51):
            if s.connect_ex(("localhost", port + i)) != 0:
                return port + i
        return port + 50


port = porta_aberta()


def start_cashd(with_webview: bool = False):
    if "--webview" in sys.argv:
        with_webview = True

    def run_taipy_gui():
        app.run(
            title="Cashd",
            run_browser=not with_webview,
            dark_mode=False,
            stylekit={
                "color_primary": "#478eff",
                "color_background_light": "#ffffff",
            },
            run_server=True,
            port=port,
            favicon="assets/PNG_LogoFavicon.png",
            watermark="",
        )

    if with_webview:
        taipy_thread = threading.Thread(target=run_taipy_gui)
        taipy_thread.start()

        global window
        window = webview.create_window(
            title="Cashd",
            url=f"http://localhost:{port}",
            frameless=True,
            maximized=maximizado,
            easy_drag=False,
            min_size=(900, 600),
        )

        webview.start()

    else:
        run_taipy_gui()
