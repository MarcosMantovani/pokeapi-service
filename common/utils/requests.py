import time
import logging
import requests
from functools import wraps
from requests.exceptions import ConnectionError
from memoize import memoize

logger = logging.getLogger(__name__)


def retry_on_failure(max_retries=3, delay=3):
    """
    Decorator para tentar executar uma função novamente se houver erro de conexão.

    Args:
        max_retries: Número máximo de tentativas
        delay: Delay entre tentativas (em segundos)

    Returns:
        Decorator para tentar executar uma função novamente se houver erro de conexão.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except ConnectionError as e:
                    if attempt == max_retries - 1:  # Last attempt
                        logger.error(f"Failed after {max_retries} attempts: {str(e)}")
                        raise  # Re-raise the last exception
                    logger.warning(
                        f"Connection error on attempt {attempt + 1}: {str(e)}. Retrying..."
                    )
                    time.sleep(delay * (attempt + 1))  # Exponential backoff
            return None

        return wrapper

    return decorator


@memoize()
def url_to_buffer(url: str, timeout: int = 30) -> tuple[bytes, dict]:
    """
    Baixa o conteúdo de um URL e retorna o conteúdo e os headers.

    Args:
        url: URL do arquivo

    Returns:
        tuple[bytes, dict]: Conteúdo e headers do arquivo
    """
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.content, response.headers


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
