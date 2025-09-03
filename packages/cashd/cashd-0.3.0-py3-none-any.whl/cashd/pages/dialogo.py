# chamado em:
#   contas.ELEMENTO_REGS
SELECIONAR_CLIENTE_ETAPA = """
<center>
    <|{SLC_USUARIO}|selector|lov={NOMES_USUARIOS}|filter|propagate|height=520px|width=650px|on_change=chg_cliente_selecionado|>
</center>
"""

SELECIONAR_TRANSAC_ETAPA = """
<center>
    <|{SLC_TRANSAC}|selector|lov={TRANSACS_USUARIO}|filter|paginated|height=360px|>
</center>
"""

FORM_EDITAR_CLIENTE = """
<|layout|columns=1 1|columns[mobile]=1 1|class_name=container
__Primeiro Nome__*

__Sobrenome__*

<|{form_conta_selec.PrimeiroNome}|input|>

<|{form_conta_selec.Sobrenome}|input|>

__Apelido__

__Telefone__

<|{form_conta_selec.Apelido}|input|>

<|{form_conta_selec.Telefone}|input|label=DDD + 9 dígitos|>

__Endereço__

__Bairro__

<|{form_conta_selec.Endereco}|input|>

<|{form_conta_selec.Bairro}|input|>

__Cidade__*

__Estado__*

<|{form_conta_selec.Cidade}|input|>

<|{form_conta_selec.Estado}|input|>

_(*) Obrigatório_
<|{str(form_contas)}|text|>
|>
"""

CONFIRMAR_TRANSAC = """
Valor: *<|{form_transac_selec.Valor}|>*

Data: *<|{form_transac_selec.DataTransac}|>*
"""


CONFIRMAR_CONTA = """
<|layout|columns=1 1|columns[mobile]=1 1|class_name=container
Primeiro Nome: *<|{form_conta_selec.PrimeiroNome}|>*

Sobrenome: *<|{form_conta_selec.Sobrenome}|>*

Apelido: *<|{form_conta_selec.Apelido}|>*

Telefone: *<|{form_conta_selec.Telefone}|>*

Endereço: *<|{form_conta_selec.Endereco}|>*

Bairro: *<|{form_conta_selec.Bairro}|>*

Cidade: *<|{form_conta_selec.Cidade}|>*

Estado: *<|{form_conta_selec.Estado}|>*
|>
"""
