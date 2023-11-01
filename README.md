# IKnowwhatyoudownload.com TwitterBot (X - Bot)

Este es un proyecto de seguimiento de IPs que han descargado torrents utilizando el sitio web [iknowwhatyoudownload.com](https://iknowwhatyoudownload.com/). El proyecto utiliza Python y las bibliotecas Requests, BeautifulSoup y Tweepy para realizar un seguimiento de las IPs y publicar tweets sobre las descargas de torrents.

## Configuración

Antes de utilizar este proyecto, necesitas configurar tus credenciales de Twitter API en el código. Sigue estos pasos:

1. Ve a [Twitter Developer](https://developer.twitter.com/en/apps) y crea una aplicación.
2. Obten tus claves de acceso (consumer_key, consumer_secret, access_token y access_token_secret).
3. Inserta estas claves en el código en las variables correspondientes.

## Uso

1. Asegúrate de tener Python instalado en tu sistema.
2. Instala las bibliotecas necesarias ejecutando `pip install requests beautifulsoup4 tweepy html5lib`.
3. Crea un archivo `ips.txt` con una lista de IPs que deseas rastrear, una por línea.
4. Ejecuta el programa principal usando `python ikwyd.py`.

El programa buscará las IPs en el archivo `ips.txt`, rastreará sus descargas de torrents en [iknowwhatyoudownload.com](https://iknowwhatyoudownload.com/) y publicará tweets sobre las descargas si son encontradas. Los tweets se guardarán en el archivo `tweets_previos.txt` para evitar duplicados.

## Créditos

Este proyecto fue creado por Sebastián Guevara y se inspiró en la idea de rastrear IPs que descargan torrents. Utiliza las siguientes bibliotecas:

- [Requests](https://docs.python-requests.org/en/latest/) para realizar solicitudes HTTP.
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) para analizar páginas web.
- [Tweepy](https://www.tweepy.org/) para interactuar con la API de Twitter.

## Contribuciones

¡Las contribuciones son bienvenidas! Si deseas contribuir al proyecto, abre una issue y estaré encantado de revisarlo.

## Licencia

Este proyecto está bajo la licencia [MIT](LICENSE).
