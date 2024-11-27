import streamlit as st
import sys
import os
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta

# Adicione o diretório base ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ultils.config import Config


def upload_blob(file, file_name):
    try:
        # Conexão ao Azure Blob Storage
        connect_str = Config.AZURE_STORAGE_CONNECTION_STRING
        container_name = Config.CONTAINER_NAME

        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)

        # Enviar arquivo
        blob_client.upload_blob(file, overwrite=True)

        # Gerar URL SAS
        sas_token = generate_blob_sas(
            account_name=blob_client.account_name,
            container_name=blob_client.container_name,
            blob_name=blob_client.blob_name,
            account_key=blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        return f"{blob_client.url}?{sas_token}"
    except Exception as e:
        st.error(f"Erro ao enviar para o Blob Storage: {e}")
        return None


def detectar_cartao_falso(blob_url):
    # Simulação de detecção de informações de cartão
    return {
        "card_name": "John Doe",
        "bank_name": "Banco Exemplo",
        "card_expiry_date": "12/2024"
    }


def show_image_and_validation(blob_url, credit_card_info):
    st.image(blob_url, caption="Imagem Enviada", use_column_width=True)
    st.write("Resultado da Validação:")

    if credit_card_info and credit_card_info.get("card_name"):
        st.markdown(f"<h1 style='color: green;'>Cartão Válido</h1>", unsafe_allow_html=True)
        st.write(f"Nome do Titular: {credit_card_info['card_name']}")
        st.write(f"Banco Emissor: {credit_card_info['bank_name']}")
        st.write(f"Data de Validade: {credit_card_info['card_expiry_date']}")
    else:
        st.markdown(f"<h1 style='color: red;'>Cartão Inválido</h1>", unsafe_allow_html=True)
        st.write("Não foi possível detectar informações de cartão de crédito.")


def configure_interface():
    st.title("Upload de Arquivo DIO - Desafio 1 - Azure - Fake Docs")
    uploaded_file = st.file_uploader("Escolha um arquivo", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        file_name = uploaded_file.name

        # Enviar para o blob storage
        blob_url = upload_blob(uploaded_file, file_name)
        if blob_url:
            st.success(f"Arquivo {file_name} enviado com sucesso para o Azure Blob Storage")

            # Simulação de detecção de informações de cartão de crédito
            credit_card_info = detectar_cartao_falso(blob_url)

            # Exibir imagem e validação
            show_image_and_validation(blob_url, credit_card_info)
        else:
            st.error(f"Falha ao enviar o arquivo {file_name} para o Azure Blob Storage")


if __name__ == "__main__":
    configure_interface()
