import requests
import os
import uuid
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv 

class RedsysClient:
    """
    Clase para interactuar con la API de Redsys.
    """
    def __init__(self, env_filepath='redsys.env'):
        """
        Inicializa RedsysClient.
        Args:
            env_filepath (str): La ruta del archivo .env.
        """
        # Cargar variables de entorno desde el archivo .env
        if not os.path.exists(env_filepath):
            raise FileNotFoundError(f"Archivo de entorno no encontrado: {env_filepath}")
        
        load_dotenv(dotenv_path=env_filepath) # Cargar el archivo .env especificado

        self.base_url = "https://apis-i.redsys.es:20443/psd2/xs2a/api-oauth-xs2a/services/rest/BancSabadell/authorize"
        self.token_url = "https://apis-i.redsys.es:20443/psd2/xs2a/api-oauth-xs2a/services/rest/BancSabadell/token"
        self.request_params = {}
        self._prepare_request_parameters()

    def _get_env_variable(self, key, default=None):
        """
        Obtiene el valor de una variable de entorno, usando un valor por defecto si no existe.
        """
        value = os.getenv(key)
        if value is None and default is None:
            raise ValueError(f"Falta una variable de entorno requerida: {key}")
        return value if value is not None else default

    def _prepare_request_parameters(self):
        """
        Extrae y prepara los parámetros de URL para solicitudes API desde las variables de entorno cargadas.
        """
        # Nota: Las claves del diccionario son los nombres de los parámetros de URL, y los valores son los nombres de las variables de entorno
        param_map = {
            'response_type': 'RESPONSE_TYPE',
            'client_id': 'CLIENT_ID',
            'second_client_id': 'SECOND_CLIENT_ID', # Este es un valor fijo, también se puede obtener desde el archivo .env
            'scope': 'SCOPE',
            'state': 'STATE',
            'redirect_uri': 'REDIRECT_URI',
            'code_challenge': 'CODE_CHALLENGE',
            'code_challenge_method': 'CODE_CHALLENGE_METHOD',
        }

        for param_key, env_key in param_map.items():
            self.request_params[param_key] = self._get_env_variable(env_key)
        

    def get_authorization_redirect_url(self):
        """
        Envía la solicitud de autorización y devuelve la URL de redirección final.
        """
        try:
            response = requests.get(self.base_url, params=self.request_params, verify=False)

            response.raise_for_status() 

            return response.url
        
        except Exception as e:
            print(f"Error desconocido: {e}")
            return None

    def extract_code_from_redirect_url(self, redirect_url):
        
        try:
            parsed_url = urlparse(redirect_url)
            query_params = parse_qs(parsed_url.query)
            
            if 'code' in query_params:
                return query_params['code'][0]  # parse_qs devuelve una lista, tomar el primer valor
            else:
                print("No se encontró el parámetro code en la URL")
                return None
        except Exception as e:
            print(f"Error al analizar la URL: {e}")
            return None

    def get_access_token(self, code):

        try:
            payload = {
                'grant_type': 'authorization_code',
                'client_id': self._get_env_variable('CLIENT_ID'),
                'code': code,
                'redirect_uri': self._get_env_variable('REDIRECT_URI'),
                'code_verifier': self._get_env_variable('CODE_VERIFIER')
            }

            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            response = requests.post(self.token_url, headers=headers, data=payload, verify=False)
            
            response.raise_for_status()
            
            return {
                'success': True,
                'data': response.json(),
                'status_code': response.status_code
            }
            
        
        except Exception as e:
            print(f"Error desconocido: {e}")
            return {
                'success': False,
                'error': f"Error desconocido: {e}"
            }

    def create_payment_request(self, access_token, payment_data=None):

        try:
            payment_url = "https://apis-i.redsys.es:20443/psd2/xs2a/api-entrada-xs2a/services/BancSabadell/v1.1/payments/sepa-credit-transfers"
            
            request_id = str(uuid.uuid4())
            
            headers = {
                'X-Request-ID': request_id,
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'X-IBM-Client-Id': self._get_env_variable('CLIENT_ID'),
                'Origin': 'https://market.apis-i.redsys.es',
                'Referer': 'https://market.apis-i.redsys.es/',  
                'TPP-Redirect-URI': 'http://localhost:8080',
                'PSU-IP-Address': '192.168.1.1',
                'Cookie': 'JSESSIONPSD2SANDBOX=000057hCGTTrfuLsCui-hO0-aYL:54f4f83818ad2e530218696453cc5c86'
            }
            
            response = requests.post(payment_url, headers=headers, json=payment_data, verify=False)
            
            response.raise_for_status()
            
            response_data = response.json()
            return {
                'success': True,
                'data': response_data,
                'status_code': response.status_code,
                'request_id': request_id
            }
            
        
        except Exception as e:
            print(f"Error desconocido: {e}")
            return {
                'success': False,
                'error': f"Error desconocido: {e}"
            }

    def check_payment_status(self, access_token, payment_id):

        try:
            status_url = f"https://apis-i.redsys.es:20443/psd2/xs2a/api-entrada-xs2a/services/BancSabadell/v1.1/payments/sepa-credit-transfers/{payment_id}/status"
            
            request_id = str(uuid.uuid4())
            
            headers = {
                'X-Request-ID': request_id,
                'Authorization': f'Bearer {access_token}',
                'X-IBM-Client-Id': self._get_env_variable('CLIENT_ID'),
                'Origin': 'https://market.apis-i.redsys.es',
                'Refer': 'https://market.apis-i.redsys.es/',
                'PSU-IP-Address': '192.168.1.1'
            }
            
            response = requests.get(status_url, headers=headers, verify=False)
            
            response.raise_for_status()
            
            response_data = response.json()
            return {
                'success': True,
                'data': response_data,
                'status_code': response.status_code
            }
            
        
        except Exception as e:
            print(f"Error desconocido: {e}")
            return {
                'success': False,
                'error': f"Error desconocido: {e}"
            }

if __name__ == "__main__":
    try:
        client = RedsysClient(env_filepath='redsys.env')

        final_url = client.get_authorization_redirect_url()

        if final_url:
            print("\nLa URL de redirección final es:", final_url)
        else:
            print("\nNo se pudo obtener la URL de redirección final.")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Asegúrese de que el archivo 'redsys.env' existe y está en la ruta correcta.")
    except ValueError as e:
        print(f"Error de configuración: {e}")
        print("Verifique que el archivo 'redsys.env' no tiene configuraciones faltantes.")

