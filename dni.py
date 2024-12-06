import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable

# URL de consulta
url_inicial = "https://eldni.com/pe/buscar-datos-por-dni"

# Encabezados para simular un navegador
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

# Crear una sesión para manejar cookies automáticamente
session = requests.Session()
session.headers.update(headers)

def obtener_token():
    """Obtiene el token automáticamente de la página inicial."""
    response = session.get(url_inicial)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        csrf_token = soup.find("input", {"name": "_token"})
        if csrf_token:
            return csrf_token["value"]
    return None

def procesar_html(html):
    """Procesa el HTML de la respuesta para extraer nombres y apellidos."""
    soup = BeautifulSoup(html, "html.parser")
    campos = {}

    # Intentar extraer los datos desde la tabla
    tabla = soup.find("table", {"class": "table table-striped table-scroll"})
    if tabla:
        filas = tabla.find("tbody").find_all("tr")
        if filas:
            celdas = filas[0].find_all("td")
            campos["DNI"] = celdas[0].text.strip()
            campos["Nombres"] = celdas[1].text.strip()
            campos["Apellido Paterno"] = celdas[2].text.strip()
            campos["Apellido Materno"] = celdas[3].text.strip()
            return campos

    # Respaldo: Extraer datos desde los inputs
    campos["Nombres"] = soup.find("input", {"id": "nombres"})["value"] if soup.find("input", {"id": "nombres"}) else "No encontrado"
    campos["Apellido Paterno"] = soup.find("input", {"id": "apellidop"})["value"] if soup.find("input", {"id": "apellidop"}) else "No encontrado"
    campos["Apellido Materno"] = soup.find("input", {"id": "apellidom"})["value"] if soup.find("input", {"id": "apellidom"}) else "No encontrado"

    return campos

def consultar_dni():
    """Consulta los datos del DNI ingresado."""
    # Paso 1: Obtener el token automáticamente
    csrf_token = obtener_token()
    if not csrf_token:
        print("No se pudo obtener el token. Verifica la página.")
        return

    print(f"Token obtenido: {csrf_token}")

    # Paso 2: Solicitar el DNI al usuario
    dni = input("Ingresa el número de DNI: ").strip()

    # Datos del formulario
    data = {
        "dni": dni,
        "_token": csrf_token
    }

    # Realizar la solicitud POST
    response = session.post(url_inicial, headers=headers, data=data)

    if response.status_code == 200:
        print("\nConsulta realizada con éxito. Procesando resultados...\n")

        # Procesar los datos obtenidos
        campos = procesar_html(response.text)

        # Crear una tabla para mostrar los resultados
        tabla = PrettyTable()
        tabla.field_names = ["Campo", "Resultado"]
        for campo, valor in campos.items():
            tabla.add_row([campo, valor])

        print(tabla)
    else:
        print(f"Error al realizar la consulta: {response.status_code}")

# Llamar a la función principal
if __name__ == "__main__":
    consultar_dni()