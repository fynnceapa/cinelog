import requests
import threading
import time

# URL-ul aplicației tale
URL = "http://localhost:8000/"
# Numărul de request-uri
REQUEST_COUNT = 50

def send_request(i):
    try:
        start_time = time.time()
        response = requests.get(URL)
        duration = time.time() - start_time
        print(f"Request #{i}: Status {response.status_code} | Timp: {duration:.2f}s")
    except Exception as e:
        print(f"Request #{i}: Eroare - {e}")

print(f"--- Începem testul de încărcare cu {REQUEST_COUNT} cereri concurente ---")
threads = []

for i in range(REQUEST_COUNT):
    t = threading.Thread(target=send_request, args=(i+1,))
    threads.append(t)
    t.start()
    # Adăugăm un mic delay pentru a nu bloca complet rețeaua locală, dar suficient de mic pentru a forța load balancing-ul
    time.sleep(0.1) 

for t in threads:
    t.join()

print("--- Test finalizat ---")