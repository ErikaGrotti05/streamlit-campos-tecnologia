import streamlit as st
import requests
import base64

# API_KEY = "g57u89pklmnuygfdraswxcd"  # Sua chave de API
# HEADERS = {
#     "x-api-key": API_KEY
# }

PAGE_SELECTION_KEY = "page_selection"
ENDPOINT_URL = "https://iog3e3n780.execute-api.us-east-1.amazonaws.com/dev"  # Seu endpoint

selected_archives = []

# Inicializa o estado da sessão para "Chat"
if PAGE_SELECTION_KEY not in st.session_state:
    st.session_state[PAGE_SELECTION_KEY] = "Chat"

# ---  Seção do Chatbot (Onde o problema original estava) ---
if st.session_state[PAGE_SELECTION_KEY] == "Chat":
    st.title("💬 Chat")

    # Obter empresas
    try:
        # response = requests.get(ENDPOINT_URL + "/company", headers=HEADERS, timeout=30)
        response = requests.get(ENDPOINT_URL + "/company", timeout=30)
        
        response.raise_for_status()
        companies = response.json()
        company_id_options = [company["name"] for company in companies]
    except requests.exceptions.RequestException as e:
        st.error(f"Falha ao obter a lista de empresas: {e}")
        st.stop()
    except Exception as e:
        st.error(f"Um erro ocorreu ao obter empresas: {e}")
        st.stop()

    # Seleção de empresa
    selected_company_name = st.selectbox("Setor", company_id_options)
    selected_company_id = next(
        (company['id'] for company in companies if company["name"] == selected_company_name),
        None,
    )

    # Seleção de documento
    selected_document_name = None
    if selected_company_id:
        try:
            selected_company = next((company for company in companies if company["id"] == selected_company_id), None)
            if selected_company and "archives" in selected_company:
                documents = selected_company["archives"]
                document_options = ["Todos os Documentos"] + [doc["archive_name"] for doc in documents]
                selected_document_name = st.selectbox("Documento", document_options)
                if selected_document_name == "Todos os Documentos":
                    selected_document_name = None
            else:
                st.error("Nenhum documento encontrado para esta empresa.")
                st.stop()
        except Exception as e:
            st.error(f"Erro ao carregar os arquivos: {str(e)}")
            st.stop()

    # Modelo e opções
    # models = {
    #     "claude-3-5-sonnet-v2": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    # }
    # model_id_options = list(models.keys())
    # selected_model_id = st.selectbox("Modelo", model_id_options)
    chosen_company_id = selected_company_id
    chosen_model_id = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"

    # Inicialização das mensagens (se necessário)
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "Como posso ajudar você?"}
        ]

    # Exibe mensagens existentes
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Input do usuário e processamento
    if prompt := st.chat_input():
        user_message = {"role": "user", "content": prompt}
        st.session_state.messages.append(user_message)
        st.chat_message("user").write(prompt)

        request_data = {
            "question": prompt,
            "companyId": chosen_company_id,
            "modelId": chosen_model_id,
        }
        if selected_document_name:
            request_data["document_id"] = selected_document_name

        # Chamada à API com spinner e tratamento de erros
        with st.spinner('Processando sua pergunta...'):
            try:
                # response = requests.post(ENDPOINT_URL + "/chat", json=request_data, headers=HEADERS, timeout=70)
                response = requests.post(ENDPOINT_URL + "/chat", json=request_data, timeout=70)
                
                response.raise_for_status()
                response_data = response.json()
                response_text = response_data["response"]

                assistant_message = {"role": "assistant", "content": response_text}
                st.session_state.messages.append(assistant_message)
                st.chat_message("assistant").write(response_text)

            except requests.exceptions.Timeout as e:
                st.error("A requisição demorou muito. Tente novamente.")
            except requests.exceptions.ConnectionError as e:
                st.error(f"Erro de conexão: {e}")
            except requests.exceptions.HTTPError as e:
                st.error(f"Erro HTTP: {e}")
            except requests.exceptions.RequestException as e:
                st.error(f"Erro na requisição: {e}")
            except Exception as e:
                st.error(f"Erro inesperado: {e}")