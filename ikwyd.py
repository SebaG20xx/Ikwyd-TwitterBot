import requests
from bs4 import BeautifulSoup
import time
import re
import tweepy

# Twitter API
client = tweepy.Client(
    consumer_key="INSERT_HERE",
    consumer_secret="INSERT_HERE",
    access_token="INSERT_HERE",
    access_token_secret="INSERT_HERE"
)


def get_similar_ips(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36'
    }
    try:
        req = requests.get(url, headers=headers)
        req.raise_for_status()
        soup = BeautifulSoup(req.content, 'html5lib')
        similar_ip_links = soup.find_all("a", class_="bold-links")
        return [link['href'] for link in similar_ip_links]
    except requests.exceptions.RequestException as e:
        print(f"Error requesting {url}: {e}")
    return []

def cargar_tweets_previos(archivo):
    try:
        tweets_previos = set()
        with open(archivo, 'r') as file:
            lines = file.read().splitlines()
            for line in lines:
                parts = line.split(";")
                if len(parts) == 3:
                    ip, fecha, torrent_text = parts[0].strip(), parts[1].strip("'"), parts[2].strip("'")
                    tweets_previos.add((ip, fecha, torrent_text))
        return tweets_previos
    except FileNotFoundError:
        return set()

def guardar_tweet_nuevo(archivo, ip, fecha, torrent_text):
    ip = ip.strip()  
    torrent_text = torrent_text.strip()  
    tweet_text = f"{ip};'{torrent_text}';'{fecha}"
    with open(archivo, 'a') as file:
        file.write(tweet_text + '\n')


def create_tweet_with_retry(client, ip, fecha, torrent_text, url, tweet_file, tweets_previos, max_retries=3):
    tweet_text = f"La IP {ip} ha descargado el siguiente torrent: '{torrent_text.strip()}'\nLink: {url}"
    print(tweet_text)
    formatted_entry = (ip.strip(), fecha, torrent_text.strip() )   
    if formatted_entry in tweets_previos:
        print("El tuit ya existe, omitiendo...")
        return

    for attempt in range(1, max_retries + 1):
        try:
            client.create_tweet(text=tweet_text)
            print("Tuit posteado con exito:", tweet_text)
            guardar_tweet_nuevo(tweet_file, ip, torrent_text)
            tweets_previos.add(formatted_entry) 
            return
        except tweepy.TweepyException as e:
            if isinstance(e, tweepy.errors.Forbidden):
                print(f"Error de tuit duplicado: {e}. Guardando el tuit.")
                guardar_tweet_nuevo(tweet_file, ip, torrent_text) 
                break 
            elif isinstance(e, tweepy.errors.TooManyRequests):
                print(f"Rate Limit :C, esperando 15 minutos (attempt {attempt}/{max_retries})...")
                time.sleep(900)  # Esperar 15 minutos 
            else:
                print(f"Error creating tweet (attempt {attempt}/{max_retries}): {e}")
                if attempt >= max_retries:
                    print("El tuit creado ha fracasado después de " + attempt + " intentos.")
    else:
        print("El tuit ha sido creado con éxito después de " + attempt + "intentos. ")

def process_ip(ip, url, tweet_file, tweets_previos):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36'
    }

    try:
        req = requests.get(url=url, headers=headers)
        req.raise_for_status()
        soup = BeautifulSoup(req.content, 'html5lib')
        out = soup.find_all("div", class_="torrent_files")
        date = soup.find('td', class_='date-column')

        if out:
            print("IP Encontrada:", ip)
            for torrent_file in out:
                torrent_info = torrent_file.text
                fecha = date.text
                print("Torrent File:", torrent_info.strip())
                create_tweet_with_retry(client, ip, fecha, torrent_info.strip(), url, tweet_file, tweets_previos)

        else:
            print("IP no Encontrada:", ip)

        similar_ips = get_similar_ips(url)
        for similar_ip_link in similar_ips:
            match = re.search(r'ip=(\d+\.\d+\.\d+\.\d+)', similar_ip_link)
            if match:
                similar_ip = match.group(1)
                print(f"Looking at similar IP: {similar_ip}")
                process_ip(similar_ip, similar_ip, tweet_file, tweets_previos)

    except requests.exceptions.RequestException as e:
        print(f"Error requesting {url}: {e}")

processed_ips = set()

def main():
    tweet_file = 'tweets_previos.txt'
    tweets_previos = cargar_tweets_previos(tweet_file)
    print("Tweets previos cargados:")
    for tweet in tweets_previos:
        print(tweet)

    URL_BASE = "https://iknowwhatyoudownload.com/en/peer/?ip="

    while True:  
        processed_ips = set()
        with open('ips.txt') as listaips:
            for ip in listaips:
                ip = ip.strip()  # Lee la próxima IP

                # Verificar si la IP ha sido procesada previamente
                if ip in processed_ips:
                    continue
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36'                           }
                URLIP = URL_BASE + ip
                try:
                    req = requests.get(url=URLIP, headers=headers)
                    req.raise_for_status()
                    soup = BeautifulSoup(req.content, 'html5lib')
                    out = soup.find_all("div", class_="torrent_files")

                    if out:
                        print("IP Encontrada: " + ip)
                        torrent_file = out[0]  # Obtener el primer torrent
                        torrent_info = torrent_file.text
                        print("Torrent File:", torrent_info)
                        process_ip(ip, URLIP, tweet_file, tweets_previos)
                        processed_ips.add(ip)
                    else:
                        print("IP no Encontrada: " + ip)

                    similar_ips = get_similar_ips(URLIP)
                    for similar_ip_link in similar_ips:
                        match = re.search(r'ip=(\d+\.\d+\.\d+\.\d+)', similar_ip_link)
                        if match:
                            similar_ip = match.group(1)
                            print(f"Viendo ips similares: {similar_ip}")
                            URLIP = URL_BASE + similar_ip
                            process_ip(similar_ip, URLIP, tweet_file, tweets_previos)

                except requests.exceptions.RequestException as e:
                    print(f"Error solicitando  {URLIP}: {e}")

        print("Esperando 1 hora")
        time.sleep(3600)  # Esperando 1 hora antres de iniciar la siguiente iteración

if __name__ == "__main__":
    main()