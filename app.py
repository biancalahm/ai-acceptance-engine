import streamlit as st
import io
import logging
from contextlib import redirect_stdout

from get_requirements import processar_requisito

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="Tech Lead IA", layout="wide")
st.title("Tech Lead IA → Trello")

# ─────────────────────────────────────────────
# ESTADO
# ─────────────────────────────────────────────
if "requisito" not in st.session_state:
    st.session_state.requisito = ""

if "resultado" not in st.session_state:
    st.session_state.resultado = None

if "logs" not in st.session_state:
    st.session_state.logs = ""

# ─────────────────────────────────────────────
# FUNÇÕES
# ─────────────────────────────────────────────
def limpar_texto():
    st.session_state.requisito = ""
    st.session_state.resultado = None
    st.session_state.logs = ""


def processar_requisito_com_logs(requisito: str):
    buffer = io.StringIO()
    log_stream = io.StringIO()

    logger = logging.getLogger()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.INFO)

    logger.addHandler(handler)

    try:
        with redirect_stdout(buffer):
            resultado = processar_requisito(requisito)

        logs_print = buffer.getvalue()
        logs_logging = log_stream.getvalue()

        logs_completos = (logs_print + "\n" + logs_logging).strip()

        return resultado, logs_completos

    finally:
        logger.removeHandler(handler)
        handler.close()


# ─────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────
st.markdown("Cole seu requisito funcional abaixo:")

st.text_area(
    "Requisito",
    height=300,
    key="requisito",
    placeholder="Ex: O sistema deverá permitir cadastrar usuários..."
)

col1, col2 = st.columns(2)

with col1:
    executar = st.button("Processar", use_container_width=True)

with col2:
    st.button("Limpar", on_click=limpar_texto, use_container_width=True)

# ─────────────────────────────────────────────
# EXECUÇÃO
# ─────────────────────────────────────────────
if executar:
    if not st.session_state.requisito.strip():
        st.warning("Digite um requisito antes de processar.")
    else:
        with st.spinner("Processando..."):
            try:
                resultado, logs = processar_requisito_com_logs(
                    st.session_state.requisito
                )

                st.session_state.resultado = resultado
                st.session_state.logs = logs

                st.success("Processamento concluído!")

            except Exception as e:
                st.error(f"Erro: {str(e)}")

# ─────────────────────────────────────────────
# RESULTADOS
# ─────────────────────────────────────────────
if st.session_state.logs:
    with st.expander("Logs do processamento", expanded=True):
        st.text_area(
            "Logs",
            st.session_state.logs,
            height=300
        )

if st.session_state.resultado:
    with st.expander("Resultado final", expanded=True):
        st.write(st.session_state.resultado)