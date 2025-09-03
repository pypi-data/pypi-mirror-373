PG_ANALISE = """
<|layout|columns=.68fr auto 1fr|class_name=header_container|

<|part|class_name=header_logo|
<|Cashd|text|height=30px|width=30px|>
|>

<|part|class_name=align_item_stretch|
<|{nav_analise_val}|toggle|lov={nav_analise_lov}|on_change={lambda s: s.elem_analise.update_content(s, s.nav_analise_val[0])}|>
|>

<|part|class_name=text_right|class_name=header_top_right_corner|
<|🗕|button|on_action=btn_mudar_minimizado|>
<|🗖|button|on_action=btn_mudar_maximizado|>
<|✖|button|on_action=btn_encerrar|>
|>

|>

<|part|partial={elem_analise}|class_name=container|>
"""


ELEM_PLOT = """
<center>
<|{dropdown_plot_type_val}|selector|lov=Balanço;Saldo acumulado|dropdown|>
<|{dropdown_periodo_val}|selector|lov={dropdown_periodo_lov}|dropdown|>
<|{slider_val}|slider|lov={slider_lov}|text_anchor=bottom|>
</center>

<center>
<|Atualizar|button|on_action={btn_gerar_main_plot}|>
</center>

<br />

<|chart|figure={main_plot}|height=360px|>
"""


ELEM_TABLES = """
<|layout|class_name=top_controls|
<|{dropdown_table_type_val}|selector|dropdown|lov=Últimas transações;Maiores saldos;Clientes inativos|on_change={chg_select_table_stats}|class_name=top_controls_dropdown|>
<|↻|button|on_action={chg_select_table_stats}|>
|>

<|part|partial={part_stats_displayed_table}|>

<|{stats_tables_pagination_legend}|text|class_name=small-text|>
<|Anterior|button|class_name=small-button|on_action=btn_prev_page_displayed_table|>
<|Próxima|button|class_name=small-button|on_action=btn_next_page_displayed_table|>
"""


ELEM_TABLE_TRANSAC_HIST = """
<|{df_last_transacs}|table|paginated|show_all=True|editable=False|sortable=False|height=360px|>
"""


ELEM_TABLE_HIGHEST_AMOUNTS = """
<|{df_highest_amounts}|table|paginated|show_all=True|editable=False|sortable=False|height=360px|>
"""


ELEM_TABLE_INACTIVE_CUSTOMERS = """
<|{df_inactive_customers}|table|paginated|show_all=True|editable=False|sortable=False|height=360px|>
"""
