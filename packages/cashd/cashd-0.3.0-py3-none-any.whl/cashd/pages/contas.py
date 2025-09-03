PG_CONTAS = """
<|layout|columns=.68fr auto 1fr|class_name=header_container|

<|part|class_name=header_logo|
<|Cashd|text|height=30px|width=30px|>
|>

<|part|class_name=align_item_stretch|
<|{nav_conta_val}|toggle|lov={nav_conta_lov}|on_change={lambda s: s.elem_conta.update_content(s, s.nav_conta_val[0])}|>
|>

<|part|class_name=text_right|class_name=header_top_right_corner|
<|🗕|button|on_action=btn_mudar_minimizado|>
<|🗖|button|on_action=btn_mudar_maximizado|>
<|✖|button|on_action=btn_encerrar|>
|>

|>

<br />

<|part|partial={elem_conta}|class_name=container|>
"""


ELEMENTO_FORM = """
<|layout|columns=1 1|columns[mobile]=1 1|class_name=container
__Primeiro Nome__*

__Sobrenome__*

<|{form_contas.PrimeiroNome}|input|>

<|{form_contas.Sobrenome}|input|>

__Apelido__

__Telefone__

<|{form_contas.Apelido}|input|>

<|{form_contas.Telefone}|input|label=DDD + 9 dígitos|>

__Endereço__

__Bairro__

<|{form_contas.Endereco}|input|>

<|{form_contas.Bairro}|input|>

__Cidade__*

__Estado__*

<|{form_contas.Cidade}|input|>

<|{form_contas.Estado}|selector|lov={dropdown_uf_lov}|dropdown|>

_(*) Obrigatório_

<|Inserir|button|class_name=plain|on_action=btn_inserir_cliente|>
<|{str(form_contas)}|text|>

|>
"""


ELEMENTO_REGS = """
<|Atualizar listagem|button|class_name=plain|on_action={btn_atualizar_listagem}|> 
<|Editar uma conta|button|on_action={btn_mostrar_dialogo_selec_cliente}|>

<|{df_clientes}|table|paginated|filter|page_size=6|page_size_options={[12,24,36]}|height=380px|>

<|{mostra_selec_cliente}|dialog|title=Selecione o cliente que será editado|width=80%|partial={dial_selec_cliente}|on_action=chg_dialog_selec_cliente_conta|page_id=selecionar_conta|labels=Fechar;Continuar|>

<|{mostra_form_editar_cliente}|dialog|title=Editando...|width=80%|partial={dial_form_editar_cliente}|on_action=chg_dialog_editar_cliente|page_id=editar_conta|labels=Voltar;Continuar|>

<|{mostra_confirma_conta}|dialog|title=Tem certeza?|width=80%|partial={dial_conta_confirmar}|on_action=chg_dialog_confirma_cliente|page_id=confirma_editar_conta|labels=Cancelar;Confirmar|>
"""
