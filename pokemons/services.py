import os
import base64
import mimetypes
from typing import List, Dict

from common.utils import make_api_request

POKE_API_BASE_URL = "https://pokeapi.co/api/v2"


class PokeApiService:

    def __init__(self):

        self.base_url = os.getenv("BASE_URL", POKE_API_BASE_URL)

    def make_request(
        self, endpoint: str, method: str, payload: dict = None, params: dict = None
    ):
        data, _ = make_api_request(
            method=method,
            url=self.base_url + endpoint,
            payload=payload,
            params=params,
            headers=self.headers,
            log_prefix="Clicksign API",
        )
        return data

    def create_envelope(self, name: str):
        payload = {
            "data": {
                "type": "envelopes",
                "attributes": {
                    "name": name,
                    "locale": "pt-BR",
                    "auto_close": True,
                    "remind_interval": 1,
                    "block_after_refusal": False,
                },
            }
        }
        endpoint = "/envelopes"
        return self.make_request(endpoint, "post", payload)

    def create_document(self, envelope_id: str, file_path: str):
        # Lê o arquivo e converte para base64
        with open(file_path, "rb") as file:
            file_content = file.read()

        # Detecta o mimetype do arquivo
        mimetype, _ = mimetypes.guess_type(file_path)
        if not mimetype:
            mimetype = "application/octet-stream"

        # Codifica em base64 e formata com o mimetype
        file_base64 = base64.b64encode(file_content).decode("utf-8")
        content_base64 = f"data:{mimetype};base64,{file_base64}"

        # Extrai apenas o nome do arquivo
        filename = os.path.basename(file_path)

        payload = {
            "data": {
                "type": "documents",
                "attributes": {
                    "filename": filename,
                    "content_base64": content_base64,
                },
            }
        }
        endpoint = f"/envelopes/{envelope_id}/documents"
        return self.make_request(endpoint, "post", payload)

    def create_signer(
        self, envelope_id: str, name: str, email: str, phone_number: str, cpf: str
    ):
        payload = {
            "data": {
                "type": "signers",
                "attributes": {
                    "name": name,
                    "email": email,
                    "phone_number": phone_number,
                    "has_documentation": True,
                    "documentation": cpf,
                    "location_required_enabled": False,
                    "communicate_events": {
                        "signature_request": "whatsapp",
                        "signature_reminder": "email",
                        "document_signed": "whatsapp",
                    },
                },
            }
        }
        endpoint = f"/envelopes/{envelope_id}/signers"
        return self.make_request(endpoint, "post", payload)

    def create_qualification_requirement(
        self, envelope_id: str, document_id: str, signer_id: str
    ):
        payload = {
            "data": {
                "type": "requirements",
                "attributes": {"action": "agree", "role": "contractor"},
                "relationships": {
                    "document": {
                        "data": {
                            "type": "documents",
                            "id": document_id,
                        }
                    },
                    "signer": {
                        "data": {
                            "type": "signers",
                            "id": signer_id,
                        }
                    },
                },
            }
        }
        endpoint = f"/envelopes/{envelope_id}/requirements"
        return self.make_request(endpoint, "post", payload)

    def create_authentication_requirement(
        self, envelope_id: str, document_id: str, signer_id: str
    ):
        payload = {
            "data": {
                "type": "requirements",
                "attributes": {"action": "provide_evidence", "auth": "whatsapp"},
                "relationships": {
                    "document": {
                        "data": {
                            "type": "documents",
                            "id": document_id,
                        }
                    },
                    "signer": {
                        "data": {
                            "type": "signers",
                            "id": signer_id,
                        }
                    },
                },
            }
        }
        endpoint = f"/envelopes/{envelope_id}/requirements"
        return self.make_request(endpoint, "post", payload)

    def activate_envelope(self, envelope_id: str):
        payload = {
            "data": {
                "type": "envelopes",
                "id": envelope_id,
                "attributes": {"status": "running"},
            }
        }
        endpoint = f"/envelopes/{envelope_id}"
        return self.make_request(endpoint, "patch", payload)

    def notify_signers(self, envelope_id: str):
        payload = {"data": {"type": "notifications", "attributes": {"message": None}}}
        endpoint = f"/envelopes/{envelope_id}/notifications"
        return self.make_request(endpoint, "post", payload)

    def send_contract_via_whatsapp(
        self, name: str, contract_path: str, signers: List[Dict]
    ):
        """
        Envia contrato via WhatsApp usando a Clicksign.
        Args:
            name: Nome do contrato
            contract_path: Caminho do arquivo do contrato
            signers: Lista de signers com os seguintes campos:
                - name: Nome do signer
                - email: Email do signer
                - phone_number: Número de telefone do signer
                - cpf: CPF do signer
        Returns:
            envelope_id: ID do envelope
        """
        envelope = self.create_envelope(name=name)
        envelope_id = envelope["data"]["id"]

        document = self.create_document(
            envelope_id=envelope_id, file_path=contract_path
        )
        document_id = document["data"]["id"]

        signer_ids = []
        for signer in signers:
            signer = self.create_signer(
                envelope_id=envelope_id,
                name=signer["name"],
                email=signer["email"],
                phone_number=signer["phone_number"],
                cpf=signer["cpf"],
            )
            signer_ids.append(signer["data"]["id"])

        for signer_id in signer_ids:
            self.create_qualification_requirement(
                envelope_id=envelope_id,
                document_id=document_id,
                signer_id=signer_id,
            )
            self.create_authentication_requirement(
                envelope_id=envelope_id,
                document_id=document_id,
                signer_id=signer_id,
            )

        self.activate_envelope(envelope_id=envelope_id)
        self.notify_signers(envelope_id=envelope_id)
        return envelope_id
