"""
Calculadora Interativa de Terminal
----------------------------------
Uma calculadora robusta, limpa e modular com suporte a operações básicas,
exponenciação, porcentagem, histórico de resultado anterior e tratamento
completo de erros.
"""

import os
import sys

# Garante compatibilidade com UTF-8 e sequências ANSI no terminal (inclusive no Windows)
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

if hasattr(sys.stdin, 'reconfigure'):
    try:
        sys.stdin.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

if os.name == 'nt':
    os.system('')

# ==============================================================================
# CORES E ESTILOS ANSI
# ==============================================================================
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

# Cores de texto
COR_PRIMARIA = "\033[38;5;39m"    # Azul brilhante
COR_SUCESSO = "\033[38;5;48m"     # Verde água
COR_ALERTA = "\033[38;5;220m"     # Amarelo/Dourado
COR_ERRO = "\033[38;5;203m"       # Vermelho suave
COR_NEUTRA = "\033[38;5;250m"     # Cinza claro
COR_DESTAQUE = "\033[38;5;141m"   # Roxo claro


# ==============================================================================
# FUNÇÕES DE OPERAÇÕES MATEMÁTICAS
# ==============================================================================

def adicao(a: float, b: float) -> float:
    """Retorna a soma de dois números."""
    return a + b


def subtracao(a: float, b: float) -> float:
    """Retorna a diferença entre dois números."""
    return a - b


def multiplicacao(a: float, b: float) -> float:
    """Retorna o produto de dois números."""
    return a * b


def divisao(a: float, b: float) -> float:
    """
    Retorna a divisão do numerador pelo denominador.
    Lança ZeroDivisionError caso o denominador seja zero.
    """
    if b == 0:
        raise ZeroDivisionError("Divisão por zero não é permitida.")
    return a / b


def exponenciacao(base: float, expoente: float) -> float:
    """
    Retorna a base elevada ao expoente.
    Pode lançar OverflowError para valores excessivamente grandes.
    """
    try:
        resultado = base ** expoente
        # Validação para números complexos (ex.: (-4) ** 0.5)
        if isinstance(resultado, complex):
            raise ValueError("O cálculo gerou um número complexo (fora do conjunto dos reais).")
        return float(resultado)
    except OverflowError:
        raise OverflowError("O resultado da exponenciação é muito grande para ser calculado.")


def porcentagem(base: float, taxa: float) -> float:
    """
    Calcula a taxa percentual sobre a base.
    Exemplo: base=200, taxa=15 -> 15% de 200 = 30.0
    """
    return (base * taxa) / 100.0


# Mapeamento dos operadores para suas respectivas funções e símbolos visuais
OPERACOES = {
    '+': {'nome': 'Adição', 'func': adicao, 'simbolo': '+'},
    '-': {'nome': 'Subtração', 'func': subtracao, 'simbolo': '-'},
    '*': {'nome': 'Multiplicação', 'func': multiplicacao, 'simbolo': '×'},
    '/': {'nome': 'Divisão', 'func': divisao, 'simbolo': '÷'},
    '^': {'nome': 'Exponenciação', 'func': exponenciacao, 'simbolo': '^'},
    '%': {'nome': 'Porcentagem', 'func': porcentagem, 'simbolo': '% de'},
}


# ==============================================================================
# FUNÇÕES DE INTERFACE E FORMATAÇÃO
# ==============================================================================

def formatar_numero(valor: float) -> str:
    """Formata um float removendo decimais desnecessários (.0) ou arredondando."""
    if valor.is_integer():
        return f"{int(valor):,}".replace(",", ".")
    
    # Formatação com até 6 casas decimais, retirando zeros à direita
    formatado = f"{valor:,.6f}".rstrip('0').rstrip('.')
    # Ajusta formato brasileiro (ponto para milhar, vírgula para decimal)
    partes = formatado.split('.')
    inteiro = partes[0].replace(",", ".")
    decimal = partes[1] if len(partes) > 1 else ""
    return f"{inteiro},{decimal}" if decimal else inteiro


def exibir_cabecalho() -> None:
    """Exibe o cabeçalho inicial da calculadora."""
    largura = 56
    print(f"{COR_PRIMARIA}╔{'═' * (largura - 2)}╗{RESET}")
    print(f"{COR_PRIMARIA}║{BOLD}{'CALCULADORA DE TERMINAL':^{largura - 2}}{RESET}{COR_PRIMARIA}║{RESET}")
    print(f"{COR_PRIMARIA}║{COR_NEUTRA}{'Simples • Precisa • Robusta':^{largura - 2}}{RESET}{COR_PRIMARIA}║{RESET}")
    print(f"{COR_PRIMARIA}╚{'═' * (largura - 2)}╝{RESET}")


def exibir_menu(resultado_anterior: float | None = None) -> None:
    """Exibe o painel de instruções e opções disponíveis."""
    print(f"\n{COR_DESTAQUE}{BOLD}Operações disponíveis:{RESET}")
    print(f"  {BOLD}[+]{RESET} Adição        {BOLD}[-]{RESET} Subtração     {BOLD}[*]{RESET} Multiplicação")
    print(f"  {BOLD}[/]{RESET} Divisão       {BOLD}[^]{RESET} Exponenciação {BOLD}[%]{RESET} Porcentagem")
    print(f"  {DIM}[c] Limpar memória   [q] Sair a qualquer momento{RESET}")

    if resultado_anterior is not None:
        valor_str = formatar_numero(resultado_anterior)
        print(f"\n{COR_SUCESSO}▶ Resultado em memória: {BOLD}{valor_str}{RESET}")


# ==============================================================================
# FUNÇÕES DE LEITURA E VALIDAÇÃO DE ENTRADA
# ==============================================================================

class ComandoSair(Exception):
    """Exceção levantada quando o usuário solicita o encerramento do programa."""
    pass


class ComandoLimpar(Exception):
    """Exceção levantada quando o usuário decide limpar o valor em memória."""
    pass


def tratar_comando_geral(entrada: str) -> None:
    """Verifica se a entrada é um comando de controle (sair ou limpar)."""
    texto = entrada.strip().lower()
    if texto in ('q', 'sair', 'exit', 'quit'):
        raise ComandoSair()
    if texto in ('c', 'limpar', 'clear', 'reset'):
        raise ComandoLimpar()


def ler_numero(mensagem: str, valor_padrao: float | None = None) -> float:
    """
    Solicita um número ao usuário, validando o tipo e tratando entradas inválidas.
    Permite usar o valor padrão caso o usuário pressione ENTER.
    """
    while True:
        try:
            prompt = f"{COR_NEUTRA}{mensagem}{RESET}"
            entrada = input(prompt).strip()
            tratar_comando_geral(entrada)

            # Caso permita valor padrão (usar o resultado anterior)
            if entrada == "" and valor_padrao is not None:
                return valor_padrao

            # Substitui vírgula por ponto para aceitar formato decimal brasileiro
            entrada_normalizada = entrada.replace(',', '.')
            return float(entrada_normalizada)

        except ValueError:
            print(f"  {COR_ERRO}✖ Entrada inválida. Digite um número válido (ex: 10 ou 3,14).{RESET}")
        except ComandoLimpar:
            # Se tentar limpar durante a entrada de número, propaga o comando
            raise


def ler_operador(mensagem: str) -> str:
    """Solicita e valida o operador matemático desejado."""
    while True:
        try:
            prompt = f"{COR_NEUTRA}{mensagem}{RESET}"
            entrada = input(prompt).strip()
            tratar_comando_geral(entrada)

            if entrada in OPERACOES:
                return entrada

            print(f"  {COR_ERRO}✖ Operador inválido. Escolha entre: +, -, *, /, ^, %{RESET}")
        except ComandoLimpar:
            raise


# ==============================================================================
# LOOP PRINCIPAL
# ==============================================================================

def executar_calculadora() -> None:
    """Controla o fluxo principal e o ciclo de vida da calculadora."""
    exibir_cabecalho()
    resultado_anterior: float | None = None

    while True:
        try:
            exibir_menu(resultado_anterior)
            print(f"{COR_PRIMARIA}{'─' * 56}{RESET}")

            # 1. Leitura do Primeiro Valor
            if resultado_anterior is not None:
                msg = f"Primeiro número [ENTER para usar {formatar_numero(resultado_anterior)}]: "
                num1 = ler_numero(msg, valor_padrao=resultado_anterior)
            else:
                num1 = ler_numero("Digite o primeiro número: ")

            # 2. Leitura do Operador
            operador = ler_operador("Digite a operação (+, -, *, /, ^, %): ")

            # 3. Leitura do Segundo Valor
            if operador == '%':
                msg_segundo = f"Porcentagem a aplicar sobre {formatar_numero(num1)} (%): "
            elif operador == '^':
                msg_segundo = "Digite o expoente: "
            else:
                msg_segundo = "Digite o segundo número: "

            num2 = ler_numero(msg_segundo)

            # 4. Processamento da Operação
            info_op = OPERACOES[operador]
            funcao_op = info_op['func']
            resultado = funcao_op(num1, num2)

            # 5. Exibição Formatada do Resultado
            str_num1 = formatar_numero(num1)
            str_num2 = formatar_numero(num2)
            str_res = formatar_numero(resultado)

            print(f"\n{COR_SUCESSO}✔ Operação realizada com sucesso:{RESET}")
            if operador == '%':
                print(f"  {BOLD}{str_num2}% de {str_num1} = {COR_SUCESSO}{str_res}{RESET}")
            else:
                simbolo = info_op['simbolo']
                print(f"  {BOLD}{str_num1} {simbolo} {str_num2} = {COR_SUCESSO}{str_res}{RESET}")

            # Armazena o resultado para possibilitar encadeamento
            resultado_anterior = resultado

        except ComandoLimpar:
            resultado_anterior = None
            print(f"\n{COR_ALERTA}↺ Memória reiniciada. Iniciando um novo cálculo.{RESET}")

        except ZeroDivisionError as erro:
            print(f"\n{COR_ERRO}✖ Erro Matemático: {erro}{RESET}")

        except OverflowError as erro:
            print(f"\n{COR_ERRO}✖ Erro de Limite: {erro}{RESET}")

        except ValueError as erro:
            print(f"\n{COR_ERRO}✖ Erro de Valor: {erro}{RESET}")

        except ComandoSair:
            print(f"\n{COR_PRIMARIA}Encerrando a calculadora. Até a próxima! 👋{RESET}\n")
            break

        except (KeyboardInterrupt, EOFError):
            print(f"\n\n{COR_ALERTA}Operação interrompida pelo usuário. Até a próxima! 👋{RESET}\n")
            break

        except Exception as erro_inesperado:
            print(f"\n{COR_ERRO}✖ Ocorreu um erro inesperado: {erro_inesperado}{RESET}")


if __name__ == "__main__":
    executar_calculadora()
