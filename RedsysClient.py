import requests
import os
from dotenv import load_dotenv # 导入 load_dotenv

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
            response = requests.get(self.base_url, params=self.request_params)

            response.raise_for_status() 

            return response.url
        except requests.exceptions.HTTPError as e:
            print(f"URL de respuesta: {e.response.url}") # Se puede imprimir la URL donde ocurrió el error
            print(f"Contenido de respuesta: {e.response.text}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error de solicitud: {e}")
            return None
        except Exception as e:
            print(f"Error desconocido: {e}")
            return None

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

