import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from datetime import datetime

equipamentos = {
    "Câmera": [""],
    "Porta Automatizada Externa": ["Mola hidráulica", "Facial", "Fecho eletroimã", "Solenóide", "Botoeira"],
    "Porta Automatizada Interna": ["Mola hidráulica", "Facial", "Fecho eletroimã", "Botoeira"],
    "Portão Veículos Externo": ["Sensores Anti-esmagamento", "Motor", "Receptor de controle", "Fecho eletroimã", "Teste dos sensores"],
    "Portão Veículos Interno": ["Sensores Anti-esmagamento", "Motor", "Receptor de controle", "Teste dos sensores"],
    "Botão de emergência": ["Botão"],
    "Giroled": ["Giroled", "Testado"],
    "Sirene": ["Sirene", "Testado"],
    "Locker": ["Infra"],
    "Roteador": ["Testado"],
    "Integração de cerca elétrica": [" "],
    "Integração de central de incêndio": [" "],
    "Elevadores": [" "],
}

st.set_page_config(page_title="Vistoria de Equipamentos", layout="wide")
st.title("Formulário de Vistoria de Equipamentos")

st.header("0. Informações do Local da Vistoria")
condominio = st.text_input("Nome do Condomínio:")
endereco = st.text_input("Endereço:")
responsavel = st.text_input("Responsável pela vistoria:")

st.header("1. Informe a quantidade de cada equipamento:")
quantidades = {}
for eq in equipamentos:
    quantidades[eq] = st.number_input(f"{eq}:", min_value=0, max_value=50, step=1, key=f"qtd_{eq}")

st.header("2. Preencha os dados da vistoria")
dados_vistoria = []
for eq, qtd in quantidades.items():
    for i in range(1, qtd + 1):
        nome_unico = f"{eq} {str(i).zfill(2)}"
        st.markdown(f"### {nome_unico}")
        perifericos = equipamentos[eq]
        resultado = {
            "Equipamento": nome_unico,
            "Tipo": eq,
        }
        for p in perifericos:
            instalado = st.checkbox(f"{p} instalado?", key=f"{nome_unico}_{p}")
            resultado[p] = "Sim" if instalado else "Não"

        obs = st.text_area(f"Observações para {nome_unico}:", key=f"obs_{nome_unico}")
        resultado["Observações"] = obs

        dados_vistoria.append(resultado)

st.header("3. Considerações e Observações Gerais")
consideracoes_gerais = st.text_area("Digite aqui as considerações e observações gerais da vistoria:", height=150)

def gerar_pdf(dados, consideracoes, condominio, endereco, responsavel):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, altura - 2 * cm, "Relatório de Vistoria de Equipamentos")

    # Dados iniciais
    c.setFont("Helvetica", 12)
    y = altura - 3 * cm
    c.drawString(2 * cm, y, f"Condomínio: {condominio}")
    y -= 0.5 * cm
    c.drawString(2 * cm, y, f"Endereço: {endereco}")
    y -= 0.5 * cm
    c.drawString(2 * cm, y, f"Responsável: {responsavel}")
    y -= 1 * cm

    for item in dados:
        c.drawString(2 * cm, y, f"Equipamento: {item['Equipamento']}")
        y -= 0.6 * cm
        for key, val in item.items():
            if key not in ["Equipamento", "Tipo"]:
                c.drawString(3 * cm, y, f"{key}: {val}")
                y -= 0.5 * cm
        y -= 0.3 * cm
        if y < 4 * cm:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = altura - 2 * cm

    # Considerações gerais
    if y < 6 * cm:
        c.showPage()
        y = altura - 2 * cm

    c.setFont("Helvetica-Bold", 14)
    c.drawString(2 * cm, y, "Considerações e Observações Gerais:")
    y -= 1 * cm
    c.setFont("Helvetica", 12)

    max_chars_per_line = 90
    linhas = []
    texto = consideracoes.split('\n')
    for linha in texto:
        while len(linha) > max_chars_per_line:
            linhas.append(linha[:max_chars_per_line])
            linha = linha[max_chars_per_line:]
        linhas.append(linha)

    for linha in linhas:
        c.drawString(2 * cm, y, linha)
        y -= 0.5 * cm
        if y < 2 * cm:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = altura - 2 * cm

    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

if dados_vistoria and condominio and endereco and responsavel:
    pdf_bytes = gerar_pdf(dados_vistoria, consideracoes_gerais, condominio, endereco, responsavel)

    st.download_button(
        label="📥 Baixar relatório em PDF",
        data=pdf_bytes,
        file_name=f"vistoria_{datetime.now().strftime('%d-%m-%Y')}.pdf",
        mime="application/pdf"
    )
