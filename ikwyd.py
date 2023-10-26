import requests
from bs4 import BeautifulSoup
import time
import re
import tweepy

# Twitter API credentials
client = tweepy.Client(
    consumer_key="INSERT_HERE",
    consumer_secret="kINSERT_HERE",
    access_token="INSERT_HERE",
    access_token_secret="INSERT_HERE"
)

def contarlineas(archivo):
    with open(archivo, "r") as file:
        return sum(1 for _ in file)

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

# Define a function to create a tweet with retries
def create_tweet_with_retry(client, tweet_text, retries=3):
    for _ in range(retries):
        try:
            client.create_tweet(text=tweet_text)
            return
        except tweepy.errors.TooManyRequests as e:
            print("Rate limit exceeded. Waiting for 15 minutes...")
            time.sleep(900)  # Wait for 15 minutes (900 seconds)
        except tweepy.TweepError as e:
            print(f"Error creating tweet: {e}")
            break
    print("Failed to create tweet after retries.")

def process_ip(ip, url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36'
    }
    URLIP = url  # Use the correct URL format

    try:
        req = requests.get(url=URLIP, headers=headers)
        req.raise_for_status()
        soup = BeautifulSoup(req.content, 'html5lib')
        out = soup.find_all("div", class_="torrent_files")

        if out:
            print("IP Encontrada: " + ip)
            # Process the torrent files here
            for torrent_file in out:
                # Extract and process the torrent file data
                torrent_info = torrent_file.text
                tweet = f"La IP {ip} ha descargado el siguiente torrent: '{torrent_info}'\nLink: {URLIP}"
                print("Torrent File:", torrent_info)
                print("Tweet:", tweet)

                # Post the tweet with retries
                create_tweet_with_retry(client, tweet)
        else:
            print(URLIP)
            print("IP no Encontrada: " + ip)

    except requests.exceptions.RequestException as e:
        print(f"Error requesting {URLIP}: {e}")

processed_ips = set()

def main():
    while True:
        cont = 0
        listaips = open('ips.txt')
        registro = open('ipsdetectadas.txt', 'w')
        URL_BASE = "https://iknowwhatyoudownload.com/en/peer/?ip="
        cantidad_lineas = contarlineas("ips.txt")

        for ip in listaips:
            ip = ip.strip()
            
            # Check if the IP has already been processed
            if ip in processed_ips:
                continue
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36'
            }
            URLIP = URL_BASE + ip

            try:
                req = requests.get(url=URLIP, headers=headers)
                req.raise_for_status()
                soup = BeautifulSoup(req.content, 'html5lib')
                out = soup.find_all("div", class_="torrent_files")

                if out:
                    print("IP Encontrada: " + ip)
                    # Process the first torrent file here
                    torrent_file = out[0]  # Get the first torrent
                    torrent_info = torrent_file.text
                    print("Torrent File:", torrent_info)

                    # Pass the URL to process_ip
                    process_ip(ip, URLIP)
                    
                    # Add the IP to the set of processed IPs
                    processed_ips.add(ip)
                    
                    # Continue to the next IP
                    continue

                else:
                    print("IP no Encontrada: " + ip)

                cont += 1
                restantes = cantidad_lineas - cont
                print("Quedan " + str(restantes) + " ips restantes")

                similar_ips = get_similar_ips(URLIP)
                for similar_ip_link in similar_ips:
                    match = re.search(r'ip=(\d+\.\d+\.\d+\.\d+)', similar_ip_link)
                    if match:
                        similar_ip = match.group(1)
                        print(f"Looking at similar IP: {similar_ip}")

                        # Update the URLIP for similar IPs
                        URLIP = URL_BASE + similar_ip

                        # Pass the updated URLIP to process_ip
                        process_ip(similar_ip, URLIP)

            except requests.exceptions.RequestException as e:
                print(f"Error requesting {URLIP}: {e}")

        listaips.close()
        registro.close()
        print("Sleeping for 10 minutes")  
        time.sleep(600)  

if __name__ == "__main__":
    main()