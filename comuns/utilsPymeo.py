from datetime import datetime, timedelta
import pandas
import sys
import time
import traceback

"""
  tipo : 1 (Erro) ou 2 (Log)
  texto: Lista de mensagens. Ex.: ['Erro','Database não encontrado']
  frame: Dados do arquivo e função que gerou o log
  status: True ou False. Define se a mensagem será mostrado no prompt, além de ser gravada
  Ex.: utilsPymeo.gerarLog(2,
                            [f"### Linha: {'{:>4}'.format(inspect.getframeinfo(inspect.currentframe()).lineno)} - Login realizado com sucesso!"], 
                            inspect.getframeinfo(inspect.currentframe()), 
                            False)

"""
def gerarLog(tipo,texto,frame,status):
    
    try:
        data = retornarDataHoraAtual()
        # Retornar a linha formatada com 4 dígitos
        linha = '{:>4}'.format(frame.lineno)

        arquivo = frame.filename
        funcao = frame.function

        #contexto = inspect.getframeinfo(inspect.currentframe()).code_context
        #indice = inspect.getframeinfo(inspect.currentframe()).index
        #posicao = inspect.getframeinfo(inspect.currentframe()).positions

        # Abrir ou criar arquivo de log
        if tipo==1:
            log = open("logerro.txt", "a")
        else:
            log = open("log.txt", "a")

        # Gravar texto no arquivo de log
        for mensagem in texto:
            log.write(f"{data} : {arquivo} ({funcao}) - Linha: {linha} \n ")
            log.write('{:>18}'.format(' '))
            log.write(f"{mensagem} \n")
            # Mostrar o texto na tela
            if status == True:
                print(mensagem)

        log.close()
    except:
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "ERROS DO PYTHON:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        log.write("" + pymsg + "\n")
        log.close()



# Retornar data e hora atual sem segundos
def retornarDataHoraAtual():
    data = datetime.now()
    return data.strftime("%d/%m/%Y %H:%M")

def dfToPdf(df, arquivo, titulo=None):
    try:
        from fpdf import FPDF
        import inspect
        print("entrei")
        class PDF(FPDF):
            def header(self):
                # Título do documento
                self.set_font('Arial', 'B', 12)
                self.cell(0, 10, titulo, 0, 1, 'C')
                self.titulo = titulo
    
            def footer(self):
                # Posição a 1,5 cm do final
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')
    
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
    
        # Definir as larguras das colunas
        margem = 10
        largura_pagina = pdf.w - 2 * margem
        num_colunas = len(df.columns)
        largura_coluna = largura_pagina / num_colunas
    
        # Adicionar cabeçalho do DataFrame
        for coluna in df.columns:
            pdf.cell(largura_coluna, 10, str(coluna), border=1, align='C')
        pdf.ln()
    
        # Adicionar as linhas do DataFrame
        for index, row in df.iterrows():
            for item in row:
                # Tratar itens que são strings muito longas
                texto = str(item)
                if len(texto) > 15:
                    texto = texto[:12] + '...'
                pdf.cell(largura_coluna, 10, texto, border=1, align='C')
            pdf.ln()
    
        pdf.output(arquivo)
        #print(f"PDF gerado com sucesso: {nome_arquivo}")
    except Exception as e:
        erro = str(e)
        gerarLog(2,
            [
                f"### Linha: {'{:>4}'.format(inspect.getframeinfo(inspect.currentframe()).lineno)}",
                f"Problema ao tentar gerar o arquivo Pdf",
                erro
            ], 
            inspect.getframeinfo(inspect.currentframe()), 
            self.exibirMsg)
        