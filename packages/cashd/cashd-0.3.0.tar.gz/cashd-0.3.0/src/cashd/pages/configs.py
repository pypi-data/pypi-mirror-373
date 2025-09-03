PG_CONFIG = """
<|layout|columns=.68fr auto 1fr|persistent|class_name=header_container|

<|part|class_name=header_logo|
<|Cashd|text|height=30px|width=30px|>
|>

<|part|class_name=align_item_stretch|
<|{nav_config_val}|toggle|lov={nav_config_lov}|on_change={lambda s: s.elem_config.update_content(s, s.nav_config_val[0])}|>
|>

<|part|class_name=text_right|class_name=header_top_right_corner|
<|🗕|button|on_action=btn_mudar_minimizado|>
<|🗖|button|on_action=btn_mudar_maximizado|>
<|✖|button|on_action=btn_encerrar|>
|>

|>

<br />

<|part|partial={elem_config}|class_name=narrow_element|>

<br />
"""

ELEMENTO_BACKUP = """
# Locais de backup

<|{df_locais_de_backup}|table|editable|editable[Id]=False|editable[Locais de backup]=False|width[Id]=50px|page_size=4|page_size_options={[]}|on_add=btn_add_local_de_backup|on_delete={btn_rm_local_de_backup}|height=190px|hover_text=Clique no símbolo de + para adicionar um local de backup|>

# Ações

<|layout|columns=1fr 1fr|

<|part|
<|Carregar backup|button|on_action={btn_carregar_backup}|>

*_Não se preocupe, esta operação é reversível. Consulte a documentação._
|>

<|part|
<|Fazer backup|button|class_name=plain|on_action={btn_fazer_backups}|>

*_Backups serão salvos nos Locais de backup._
|>
|>
"""

ELEMENTO_ATALHO = """
# Atalhos

<|Adicionar atalho|button|on_action={btn_criar_atalho}|class_name=plain|>

*_Atalhos serão adicionados ao menu iniciar e à área de trabalho._

<br />

# Sessão

Executando em http://127.0.0.1:<|{port}|text|>
"""

ELEMENTO_PREFS = """
# Contas

__Valores padrão no formulário:__

<br />

<|layout|columns=1 1|columns[mobile]=1 1|class_name=container

<|{dropdown_uf_val}|selector|label=Estado padrão|lov={dropdown_uf_lov}|dropdown|on_change={lambda s: btn_chg_prefs_main_state(s, dropdown_uf_val)}|>

<|{input_cidade_val}|input|label=Cidade padrão|change_delay=1200|on_change={lambda s: btn_chg_prefs_main_city(s, input_cidade_val)}|>

|>

# Estatísticas

__Limite de linhas na tabela:__

<br />

<|layout|columns=1 1|columns[mobile]=1 1|class_name=container

<|{input_quant_max_ultimas_transacs}|number|label=Últimas transações [1000]|change_delay=1200|on_change={lambda s: btn_chg_max_ultimas_transacs(s, input_quant_max_ultimas_transacs)}|>

<|{input_quant_max_highest_balances}|number|label=Maiores saldos [10]|change_delay=1200|on_change={lambda s: btn_chg_max_highest_balances(s, input_quant_max_highest_balances)}|>

|>

"""
