import itertools
import string
import threading
import ssl
import httpx
import time
import yaml
import os
import random
from extvip import log, inputf as input, printf as printf

lock = threading.Lock()
tryed = set()

def conf():
    data = {}

    log.info("cfg olustr")

    proxyval = input("prefix girin > (uretecegi isimlerin basin da veya sonun da olacak harf) (bos birakabilirsn): ")
    if proxyval == "":
        data['prefix'] = {
            'deger': None,
            'pos': None
        }
    else:
        posi = input("prefixin basta mi olsun sonda mi? (start/end): ").strip().lower()
        while posi not in ["start", "end"]:
            log.fatal("gecersiz bir sey yazdin, lutfen 'start' ya da 'end' yaz.")
            posi = input("prefix bsata mi olsun sonda mi? (start/end): ").strip().lower()

        data['prefix'] = {
            'deger': proxyval,
            'pos': posi
        }

    uzunlk = int(input("uretilen ismin uzunlugu kac olsun?: "))
    sayi = input("kullanici adin da sayilar olsun mu? (y/n): ").strip().lower() == "y"
    ozel = input("kullanici adin da ozel karakterler olsun mu? (y/n): ").strip().lower() == "y"

    data['isimgen'] = {
        'uzunluk': uzunlk,
        'sayilar': sayi,
        'ozelkarakter': ozel
    }

    proxykullan = input("proxy kullanmak ister misin (residential)? (y/n): ").strip().lower()
    if proxykullan == "y":
        format = input("proxy formati 'username:password@ip:port' seklin de olmali proxy bilgilerini gir: ").strip()
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
                log.fatal("gecersiz proxy formati girdin proxy formati 'username:password@ip:port' seklin de olmali.")
                return
        else:
            log.fatal("proxy bilgileri eksik seks!")
            return
    else:
        log.fatal("premium proxy kullanmadan devam edemen")
        return

    webhook = input("webhook gir: ").strip()
    data['webhook'] = {
        'url': webhook
    }

    debug = input("debug acilsin mi???? (y/n): ").strip().lower() == "y"
    data['debug'] = debug

    # İş parçacığı sayısını sor
    thread_count = input("kac thread kullanmak istersn (def: 30): ")
    if thread_count.isdigit():
        data['thread_count'] = int(thread_count)
    else:
        log.info("gecersiz deger girdin varsayilan olarak 30 kullanilacak.")
        data['thread_count'] = 30

    with open('config.yaml', 'w') as file:
        yaml.dump(data, file)

    log.info("dosya olusturld.")

def cfgload():
    if not os.path.exists('config.yaml'):
        conf()
    with open('config.yaml', 'r') as file:
        return yaml.safe_load(file)

config = cfgload()

def setolustur():
    chrset = list(string.ascii_lowercase)

    if config['isimgen']['sayilar']:
        chrset += list(string.digits)

    if config['isimgen']['ozelkarakter']:
        chrset += ["_", "."]

    return chrset

chrset = setolustur()

def isimgen(prefix, total_uzunlk, posi):
    if prefix is None:
        return ''.join(random.choices(chrset, k=total_uzunlk))

    if len(prefix) > total_uzunlk:
        raise ValueError(f"prefix uzunlugu isim uzunlugundan fazla olamaz > prefix uzunlugun:({len(prefix)}) - > isim uzunlugun({total_uzunlk}).")

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
        with httpx.Client() as client:
            response = client.post(webhook, json=payload)
            if response.status_code == 204:
                log.success(f">>>>>>>>>>>>>>>>>> webhook'a gonderdim: {message}")
            else:
                log.error(f"hata: {response.text}")
    except Exception as e:
        log.error(f"hata2: {e}")

def load_used_usernames():
    if os.path.exists('used.txt'):
        with open('used.txt', 'r') as file:
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
            "http://": proxy_url,
            "https://": proxy_url
        }
    else:
        log.fatal("proxy bilgileri eksik seks!!!")
        return

    debug = config['debug']

    try:
        if prefix and len(prefix) > total_uzunlk:
            raise ValueError(f"prefix uzunlugu isim uzunlugundan fazla olamaz > prefix uzunlugun:({len(prefix)}) - > isim uzunlugun({total_uzunlk}).")

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
                    with httpx.Client(proxies=proxies, verify=ssl_context) as client:
                        xr = client.post('https://discord.com/api/v9/unique-username/username-attempt-unauthed',
                                         json=pys)

                    if xr.status_code == 200:
                        response_json = xr.json()
                        if 'taken' in response_json:
                            if response_json['taken']:
                                log.info(f'taken --> {userx} -> {xr.text}')
                                with open('used.txt', 'a') as file:
                                    file.write(userx + '\n')
                            else:
                                log.success(f'NOTTAKENN ---------> {userx} -> {xr.text}')
                                send(f"alinabilir isim: {userx}")
                        else:
                            log.fatal(f"hatali yanit > {xr.text}")
                    elif xr.status_code == 429:
                        deneme = xr.json().get("retry_after", 1)
                        log.fatal(f"rate yedik sonra tekrar denersin {deneme} saniye..")
                        time.sleep(deneme)
                    else:
                        log.error(f"hata3: {xr.status_code} -> {xr.text}")

                except Exception as e:
                    log.error(f"{e}")

            except ValueError as ve:
                log.error(f"isim uretilirken hata: {ve}")
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
