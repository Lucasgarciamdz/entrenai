"""
Cliente para conectar con la API de Moodle.
"""
import requests
import mimetypes
from core.utils import configurar_logging
from core.errors import ErrorMoodle

class MoodleClient:
    """
    Cliente para conectar con la API de Moodle
    """
    def __init__(self, url: str, token: str):
        """
        Inicializa el cliente de Moodle.
        
        Args:
            url: URL base de la instancia de Moodle
            token: Token de autenticación para la API de Moodle
        """
        self.url = url
        self.token = token
        self.logger = configurar_logging("moodle_client")

    def _make_request(self, function: str, params=None):
        """
        Realiza una petición a la API de Moodle.
        
        Args:
            function: Nombre de la función de la API a llamar
            params: Parámetros adicionales para la petición
            
        Returns:
            Datos de respuesta de la API
            
        Raises:
            ErrorMoodle: Si ocurre un error en la comunicación con Moodle
        """
        if params is None:
            params = {}
        request_url = f"{self.url}/webservice/rest/server.php"
        request_params = {
            'wstoken': self.token,
            'wsfunction': function,
            'moodlewsrestformat': 'json',
            **params
        }
        try:
            self.logger.debug("Solicitando %s a Moodle", function)
            response = requests.get(request_url, params=request_params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict) and 'exception' in data:
                self.logger.error("Error de Moodle: %s", data.get('message', 'Error desconocido'))
                raise ErrorMoodle(data.get('message', 'Error desconocido'))
            return data
        except requests.RequestException as e:
            self.logger.error("Error al comunicarse con Moodle: %s", e)
            raise ErrorMoodle(str(e))

    def get_courses(self):
        """
        Obtiene la lista de cursos disponibles.
        
        Returns:
            Lista de cursos
        """
        result = self._make_request('core_course_get_courses', {})
        if result is None:
            return []
        return result

    def get_course_contents(self, course_id: int):
        """
        Obtiene el contenido de un curso.
        
        Args:
            course_id: ID del curso
            
        Returns:
            Contenido del curso
        """
        result = self._make_request('core_course_get_contents', {'courseid': course_id})
        if result is None:
            return []
        return result

    def download_file(self, file_url: str, filename: str):
        """
        Descarga un archivo de Moodle.
        
        Args:
            file_url: URL del archivo
            filename: Nombre del archivo
            
        Returns:
            Tupla con (contenido del archivo, tipo de contenido)
            
        Raises:
            ErrorMoodle: Si ocurre un error al descargar el archivo
        """
        try:
            url_with_token = f"{file_url}&token={self.token}"
            self.logger.debug("Descargando archivo: %s", filename)
            response = requests.get(url_with_token, timeout=30)
            response.raise_for_status()
            content_type = response.headers.get('Content-Type', '')
            if not content_type or content_type == 'application/octet-stream':
                content_type, _ = mimetypes.guess_type(filename)
                if not content_type:
                    content_type = 'application/octet-stream'
            self.logger.debug("Tipo de contenido detectado: %s", content_type)
            if content_type.startswith('text/') or content_type in [
                'application/json', 'application/xml',
                'application/javascript', 'application/xhtml+xml']:
                return response.text, content_type
            else:
                return response.content, content_type
        except requests.RequestException as e:
            self.logger.error("Error al descargar archivo: %s", e)
            raise ErrorMoodle(str(e))