import requests
import threading
import time
import os
import sys
import socket
import random
from queue import Queue

write_queue = Queue()
elite_results = []
https_results = []
http_results = []

KAYNAKLAR = [
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    "https://www.proxy-list.download/api/v1/get?type=http",
    "https://proxyspace.pro/http.txt",
    "https://openproxylist.xyz/http.txt"
]

TEST_DOMAINS = ["http://httpbin.org/headers", "http://checkip.amazonaws.com", "http://neverssl.com"]
FORBIDDEN_HEADERS = ["via", "x-forwarded-for", "forwarded", "proxy-connection", "x-real-ip"]

try:
    MY_IP = requests.get("http://checkip.amazonaws.com", timeout=5).text.strip()
except:
    MY_IP = "127.0.0.1"

def ekran_yenile():
    os.system('cls' if os.name == 'nt' else 'clear')

def gorsel_banner():
    ekran_yenile()
    resim_yolu = "assets/banner.jpg"
    try:
        if os.path.exists(resim_yolu):
            os.system(f"chafa --symbols block --colors 240 --dither ordered --size 77x34 {resim_yolu}")
        else:
            print("\033[1;31m[!] Görsel bulunamadı: assets/banner.jpg\033[0m")
    except:
        pass
        
    print("\033[1;35m" + "█"*65)
    print("   PRO-HUNTER v5 | DERİN ARAMA HIZLI TEST | THT | @sweazy")
    print("   [Toplayıcı + Doğrulayıcı (Checker)+ Kalite Sıralaması: AKTİF]")
    print("█"*65 + "\033[0m")

def intelligence_check(p):
    try:
        ip, port = p.split(":")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(2.5)
        if s.connect_ex((ip, int(port))) != 0:
            s.close()
            return
        s.close()
    except: return

    with requests.Session() as session:
        session.proxies = {"http": f"http://{p}", "https": f"http://{p}"}
        session.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        
        try:
            r1 = session.get("http://httpbin.org/headers", timeout=(3, 5), allow_redirects=False)
            if r1.ok:
                data = r1.json().get("headers", {})
                if MY_IP in str(data): return 
                
                is_elite = not any(h in [k.lower() for k in data.keys()] for h in FORBIDDEN_HEADERS)
                
                try:
                    start_tls = time.perf_counter()
                    r_https = session.get("https://example.com", timeout=(3, 5), allow_redirects=False)
                    latency = round(time.perf_counter() - start_tls, 2)
                    has_https = r_https.ok
                except:
                    has_https = False
                    latency = 5.0

                time.sleep(2) 
                r_burst = session.head("http://neverssl.com", timeout=3)
                
                if r_burst.ok:
                    quality_score = latency - (1.0 if is_elite else 0) - (0.5 if has_https else 0)
                    res_data = {"proxy": p, "speed": latency, "score": quality_score}
                    
                    status = "ELITE" if is_elite else "ANON"
                    color = "\033[1;32m" if is_elite and has_https else "\033[1;36m"
                    print(f"{color}{p} | {latency}s | {status} | STABIL\033[0m")

                    if is_elite: elite_results.append(res_data)
                    if has_https: https_results.append(res_data)
                    else: http_results.append(res_data)
        except: pass

def final_save(filename, data_list, baslik):
    sorted_list = sorted(data_list, key=lambda x: x['score'])
    with open(filename, "w") as f:
        f.write(f"--- {baslik} ---\n")
        f.write("SIRALAMA KRITERI: Hiz + Stabilite + Gizlilik Skoru\n")
        f.write("NOT: Elite durumu IP gizler ancak banlanmayi garanti etmez.\n")
        f.write("EN IYI PERFORMANS ICIN: 05:00-11:00 UTC saatlerini kullanin.\n\n")
        for item in sorted_list:
            f.write(f"{item['proxy']}\n")

def baslat():
    while True:
        gorsel_banner()
        print("1 | Proxy Topla")
        print("2 | Doğrulama (Checker)")
        print("3 | Çıkış")
        sec = input("\nSeçiminiz: ")

        if sec == "1":
            limit = input("\nKaç adet (örn: 500 a (adeti temsil eder)) veya Kaç saniye (örn: 60 s): ").lower()
            try:
                val = int(limit.split()[0])
                mod = limit.split()[1]
            except: print("Hatalı format!"); time.sleep(2); continue
            
            dosya = input("Kayıt edilecek dosya adı (.txt): ")
            havuz = set()
            basla = time.time()
            print("\n[*] Kaynaklar taranıyor, lütfen bekleyin...")

            for url in KAYNAKLAR:
                if mod == 's' and (time.time() - basla) > val: break
                if mod == 'a' and len(havuz) >= val: break
                try:
                    r = requests.get(url, timeout=10)
                    for line in r.text.splitlines():
                        p = line.strip()
                        if ":" in p:
                            havuz.add(p)
                            if mod == 'a' and len(havuz) >= val: break
                    print(f"[+] Kaynak taranıyor: {url.split('/')[2]} | Güncel Havuz: {len(havuz)}")
                except: continue
            
            with open(dosya, "w") as f:
                for p in list(havuz): f.write(p + "\n")
            print(f"\n[!] İşlem tamamlandı. {len(havuz)} adet benzersiz proxy toplandı.")
            input("\nMenüye dönmek için ENTER basın...")

        elif sec == "2":
            kaynak = input("\nAnaliz edilecek dosya adı: ")
            if not os.path.exists(kaynak): print("Dosya bulunamadı!"); time.sleep(2); continue
            
            proxyler = list(set(open(kaynak).read().splitlines()))
            q = Queue()
            for p in proxyler: q.put(p)
            
            print(f"\n[*] {len(proxyler)} proxy inceleniyor. İş parçacığı (threads): 70")
            
            def worker():
                while not q.empty():
                    intelligence_check(q.get())
                    q.task_done()

            for _ in range(70):
                threading.Thread(target=worker, daemon=True).start()
            
            q.join()
            
            if elite_results: final_save("elite_sirali.txt", elite_results, "ELITE PROXY LISTESI")
            if https_results: final_save("https_sirali.txt", https_results, "HTTPS PROXY LISTESI")
            if http_results: final_save("http_sirali.txt", http_results, "HTTP ONLY LISTESI")
            
            print("\n[!] Analiz bitti. En kaliteli sonuçlar dosyaya en hızlıdan yavaşa doğru yazıldı.")
            input("\nMenüye dönmek için ENTER basın...")

        elif sec == "3":
            print("\nsweazy sundu. Güvende kalın, THT ile kalın.")
            sys.exit()

if __name__ == "__main__":
    baslat()
    