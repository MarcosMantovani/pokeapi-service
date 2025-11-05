import logging
import requests


def make_api_request(
    method: str,
    payload=None,
    params=None,
    url: str = None,
    headers: dict = None,
    log_prefix="API",
):
    """
    Realiza uma requisição à API e trata os erros de forma padronizada.

    Args:
        method (str): Método HTTP ('get', 'post', 'put', 'patch', 'delete')
        payload (dict, optional): Dados a serem enviados no corpo da requisição
        params (dict, optional): Parâmetros de query string
        url (str, optional): URL base da API
        headers (dict, optional): Cabeçalhos da requisição
        log_prefix (str, optional): Prefixo para as mensagens de log

    Returns:
        dict or False: Resposta da API em caso de sucesso ou False em caso de erro
    """
    method = method.lower()
    request_methods = {
        "get": requests.get,
        "post": requests.post,
        "put": requests.put,
        "patch": requests.patch,
        "delete": requests.delete,
    }

    if method not in request_methods:
        logging.error(f"Método HTTP inválido: {method}")
        return False

    request_func = request_methods[method]

    try:
        logging.debug(f"{log_prefix}: Enviando requisição {method.upper()} para {url}")
        if payload:
            logging.debug(f"{log_prefix}: Payload: {payload}")
        if params:
            logging.debug(f"{log_prefix}: Parâmetros: {params}")

        # Fazer a requisição com os parâmetros apropriados
        if payload and params:
            response = request_func(url, json=payload, params=params, headers=headers)
        elif payload:
            response = request_func(url, json=payload, headers=headers)
        elif params:
            response = request_func(url, params=params, headers=headers)
        else:
            response = request_func(url, headers=headers)

        # Registrar resposta antes de verificar o status
        try:
            response_data = response.json()
            logging.debug(f"{log_prefix}: Resposta recebida: {response_data}")
        except ValueError:
            logging.debug(f"{log_prefix}: Resposta não-JSON recebida: {response.text}")

        # Verificar status da resposta
        response.raise_for_status()

        # Se chegou aqui, a requisição foi bem-sucedida
        return response.json(), response.status_code

    except requests.exceptions.RequestException as e:
        error_message = f"Erro na requisição {method.upper()} para {url}: {e}"

        # Adicionar detalhes do erro caso exista uma resposta da API
        if hasattr(e, "response") and e.response is not None:
            error_message += f" (Status: {e.response.status_code})"
            try:
                error_detail = e.response.json()
                error_message += f" - Detalhes: {error_detail}"
            except ValueError:
                error_message += f" - Resposta: {e.response.text}"

        logging.error(error_message)
        return False, e.response.status_code
