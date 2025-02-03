import itertools
import string
import threading
import ssl
import requests
import time
import yaml
import os
import random
from extvip import log, inputf as input, printf as printf
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

lock = threading.Lock()
tryed = set()

def conf():
    data = {}

    log.info("cfg gen")

    proxyval = input("enter prefix > (the letter that will be at the beginning or at the end of the names it will produce) (you can leave it blank): ")
    if proxyval == "":
        data['prefix'] = {
            'deger': None,
            'pos': None
        }
    else:
        posi = input("should your prefix be at the beginning or at the end (start/end): ").strip().lower()
        while posi not in ["start", "end"]:
            log.fatal("if you have typed something invalid, please type 'start' or 'end'.")
            posi = input("prefix at the beginning or at the end? (start/end): ").strip().lower()

        data['prefix'] = {
            'deger': proxyval,
            'pos': posi
        }

    uzunlk = int(input("how long should the generated name be ??: "))
    sayi = input("do you want numbers in your username ? (y/n): ").strip().lower() == "y"
    ozel = input("do you want special characters in your username ?? (y/n): ").strip().lower() == "y"

    data['isimgen'] = {
        'uzunluk': uzunlk,
        'sayilar': sayi,
        'ozelkarakter': ozel
    }

    proxykullan = input("do you want to use a proxy (residential)? (y/n): ").strip().lower()
    if proxykullan == "y":
        format = input("proxy format should be 'username:password@ip:port' enter proxy information: ").strip()
        if format:
            try:
                parts = format.split('@')
                bilgi, address_port = parts[0], parts[1]
                isim, proxy_password = bilgi.split(':')
                ipadresi, proxy_port = address_port.split(':')
                data['proxy'] = {
                    "username": isim,
                    "password": proxy_password,
                    "address": ipadresi,
                    "port": int(proxy_port)
                }
            except ValueError:
                log.fatal("you entered an invalid proxy format, the proxy format should be 'username:password@ip:port'.")
                return
        else:
            log.fatal("proxy information missing sex!")
            return
    else:
        data['proxy'] = None

    webhook = input("webhook gir: ").strip()
    data['webhook'] = {
        'url': webhook
    }

    debug = input("should debug be enabled ???? (y/n): ").strip().lower() == "y"
    data['debug'] = debug

    thread_count = input("enter threadd (def: 30): ")
    if thread_count.isdigit():
        data['thread_count'] = int(thread_count)
    else:
        log.info("you entered an invalid value 30 will be used by default.")
        data['thread_count'] = 30

    with open('config.yaml', 'w', encoding='utf-8') as file:
        yaml.dump(data, file)

    log.info("cfg createdz")
    os.system("cls")

def cfgload():
    if not os.path.exists('config.yaml'):
        conf()
    with open('config.yaml', 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

config = cfgload()

def setolustur():
    chrset = list(string.ascii_lowercase)

    if config['isimgen']['sayilar']:
        chrset += list(string.digits)

    if config['isimgen']['ozelkarakter']:
        chrset += [".", "."]

    return chrset

chrset = setolustur()

def isimgen(prefix, total_uzunlk, posi):
    if prefix is None:
        return ''.join(random.choices(chrset, k=total_uzunlk))

    if len(prefix) > total_uzunlk:
        raise ValueError(f"prefix length cannot be longer than name length > prefix length:({len(prefix)}) - > name length({total_length}).")

    kalanuzunluk = total_uzunlk - len(prefix)

    rendimchar = ''.join(random.choices(chrset, k=kalanuzunluk))

    if posi == "start":
        return prefix + rendimchar
    elif posi == "end":
        return rendimchar + prefix
    else:
        return rendimchar

def send(message):
    webhook = config['webhook']['url']
    payload = {
        "content": message
    }
    try:
        response = requests.post(webhook, json=payload)
        if response.status_code == 204:
            log.success(f">>>>>>>>>>>>>>>>>> SENDED WEBHOOK: {message}")
        else:
            log.error(f"hata: {response.text}")
    except Exception as e:
        log.error(f"err2: {e}")

def load_used_usernames():
    if os.path.exists('nicks.txt'):
        with open('nicks.txt', 'r') as file:
            return set(file.read().splitlines())
    return set()

def thr():
    ssl_context = ssl.create_default_context()

    prefix = config['prefix']['deger']
    total_uzunlk = config['isimgen']['uzunluk']
    posi = config['prefix']['pos'] if prefix else None

    used_usernames = load_used_usernames()

    proxcfg = config['proxy']
    if proxcfg['username'] and proxcfg['address']:
        proxy_url = f"http://{proxcfg['username']}:{proxcfg['password']}@{proxcfg['address']}:{proxcfg['port']}"
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
    else:
        log.fatal("proxy information missing sex!!!")
        return

    debug = config['debug']

    try:
        if prefix and len(prefix) > total_uzunlk:
            raise ValueError(f"prefix length cannot be longer than name length > prefix length:({len(prefix)}) - > name length({total_length}).")

        while True:
            try:
                userx = isimgen(prefix, total_uzunlk, posi)

                if userx in used_usernames:
                    continue

                with lock:
                    if userx in tryed:
                        continue
                    tryed.add(userx)

                if debug:
                    with open('nicks.txt', 'a') as file:
                        file.write(userx + '\n')

                pys = {"username": userx}

                try:
                    response = requests.post(
                        'https://discord.com/api/v9/unique-username/username-attempt-unauthed',
                        json=pys,
                        proxies=proxies,
                        verify=False,
                        timeout=30
                    )
                    xr = response

                    if xr.status_code == 200:
                        response_json = xr.json()
                        if 'taken' in response_json:
                            if response_json['taken']:
                                log.info(f'taken --> {userx} -> {xr.text}')
                                with open('nicks.txt', 'a') as file:
                                    file.write(userx + '\n')
                            else:
                                log.success(f'NOTTAKENN ---------> {userx} -> {xr.text}')
                                send(f"available nick: {userx}")
                        else:
                            log.fatal(f"error > {xr.text}")
                    elif xr.status_code == 429:
                        deneme = xr.json().get("retry_after", 1)
                        log.fatal(f"rated {deneme} then try again")
                        time.sleep(deneme)
                    else:
                        log.error(f"err3: {xr.status_code} -> {xr.text}")

                except requests.exceptions.RequestException as e:
                    log.error(f"{e}")
                    time.sleep(5)
                    continue

            except ValueError as ve:
                log.error(f"error generating name: {ve}")
                break

    except ValueError as e:
        log.error(f"[HT] {e}")
        return

threads = []
for _ in range(config['thread_count']):
    thread = threading.Thread(target=thr)
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()
