# CI/CD Deployment FastAPI Health API

## Deskripsi Tugas
Pada tugas ini, peserta diminta untuk membuat sebuah **Public API** sederhana yang memiliki endpoint `/health`. Endpoint tersebut berfungsi untuk menampilkan informasi dasar mengenai kondisi server yang sedang berjalan. Informasi yang ditampilkan meliputi identitas pembuat API, waktu saat request dilakukan, serta lama server telah berjalan (uptime).
Setelah API berhasil dibuat, API tersebut harus dijalankan di dalam **container Docker** dan dideploy pada **VPS publik**. API tidak boleh dijalankan pada port 80 atau 443. Selanjutnya, server akan menggunakan **Nginx sebagai reverse proxy** yang dikonfigurasi menggunakan **Ansible**, sehingga API dapat diakses tanpa konfigurasi manual di server. Proses deployment juga direncanakan untuk diotomatisasi menggunakan **GitHub Actions** sebagai bagian dari implementasi **CI/CD**.
Pada tahap yang telah dilakukan saat ini, API sudah berhasil dibuat menggunakan **FastAPI**, berhasil dijalankan di dalam **container Docker**, dan sudah berhasil dijalankan pada **VPS**. Namun masih terdapat kendala pada akses API dari internet yang menyebabkan API hanya dapat diakses dari dalam VPS menggunakan `curl`.

---

# Implementasi API
API dibuat menggunakan bahasa pemrograman **Python** dengan framework **FastAPI**. Framework ini dipilih karena ringan, cepat, dan mudah digunakan untuk membuat REST API sederhana.
Endpoint utama yang dibuat adalah: 
```
/health
```

Endpoint ini akan mengembalikan informasi dalam format **JSON** yang berisi data identitas pembuat API, status server, waktu saat request dilakukan, serta uptime server.
Isi struktur response yang dihasilkan adalah sebagai berikut:
```json
{
  "nama": "Arda",
  "nrp": "5025241074",
  "status": "UP",
  "timestamp": "2026-03-27 14:10:22",
  "uptime": "15.23 seconds"
}
```

Endpoint ini digunakan sebagai indikator sederhana untuk mengetahui apakah API sedang berjalan dengan baik atau tidak.


# Implementasi Endpoint /health
Berikut adalah implementasi endpoint /health yang dibuat menggunakan FastAPI.
```python
from fastapi import FastAPI
from datetime import datetime
import time

app = FastAPI()

start_time = time.time()

@app.get("/health")
def health():
    uptime = time.time() - start_time
    return {
        "nama": "Arda",
        "nrp": "5025241074",
        "status": "UP",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "uptime": f"{uptime:.2f} seconds"
    }
```
Pada kode di atas, variabel `start_time` digunakan untuk mencatat waktu saat server pertama kali dijalankan. Setiap kali endpoint `/health` diakses, sistem akan menghitung selisih waktu antara waktu saat ini dengan waktu awal server dijalankan. Nilai tersebut kemudian ditampilkan sebagai uptime server.
Selain itu, waktu saat request dilakukan juga ditampilkan dalam bentuk timestamp menggunakan modul datetime.


# Setup Environment Python
Sebelum melakukan proses containerization menggunakan Docker, environment Python terlebih dahulu dibuat menggunakan virtual environment. Hal ini bertujuan untuk mengisolasi dependency yang digunakan oleh project.
Langkah-langkah yang dilakukan adalah sebagai berikut:
```bash
unset PYTHONPATH
python3 -m venv env
source env/bin/activate
pip install fastapi uvicorn
pip freeze > requirements.txt
deactivate
```
Perintah `pip freeze` digunakan untuk menyimpan seluruh dependency yang telah terinstall ke dalam file `requirements.txt`. File ini nantinya akan digunakan kembali oleh Docker untuk menginstall dependency yang sama di dalam container.


# Containerization Menggunakan Docker
Setelah API berhasil dibuat dan berjalan dengan baik di lingkungan lokal, langkah berikutnya adalah melakukan containerization menggunakan Docker. Tujuan dari containerization adalah agar aplikasi dapat dijalankan secara konsisten di berbagai environment tanpa harus melakukan konfigurasi ulang.
## Dockerfile
Berikut adalah Dockerfile yang digunakan dalam project ini:
```dockerfile
FROM python:3.10

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt
```
Dockerfile ini melakukan beberapa langkah utama, yaitu:
1. Menggunakan base image python:3.10
2. Membuat direktori kerja /app
3. Menyalin seluruh file project ke dalam container
4. Menginstall dependency yang terdapat pada requirements.txt

## Docker Compose
Untuk menjalankan container dengan lebih mudah, digunakan Docker Compose dengan konfigurasi berikut:
```yaml
version: '3'

services:
  web:
    build: .
    command: sh -c "uvicorn main:app --reload --port=8000 --host=0.0.0.0"
    ports:
      - "8000:8000"
    volumes:
      - .:/app
```

Konfigurasi ini menjalankan FastAPI menggunakan Uvicorn pada port 8000 dan menghubungkan port tersebut dengan port 8000 pada host.
Container kemudian dijalankan menggunakan perintah berikut:
```bash
sudo docker compose up --build
```

Setelah container berjalan, API dapat diakses melalui:
```
http://localhost:8000/health
```
API berhasil dijalankan dengan baik pada environment lokal menggunakan Docker.
<img width="600" height="200" alt="image" src="https://github.com/user-attachments/assets/a82179ea-0752-4c47-aaaa-f10cc0c4609f" />



# Struktur Project
Struktur project yang digunakan dalam repository ini adalah sebagai berikut:
```
.
├── .dockerignore
├── Dockerfile
├── docker-compose.yaml
├── main.py
├── requirements.txt
```
File `.dockerignore` digunakan untuk memastikan file yang tidak diperlukan tidak ikut disalin ke dalam container, seperti virtual environment dan cache Python.


# Deployment ke VPS
Setelah container berhasil berjalan di environment lokal, langkah berikutnya adalah melakukan deployment ke VPS publik.
Server yang digunakan menggunakan sistem operasi Ubuntu 22.04.
Akses ke VPS dilakukan menggunakan SSH dengan perintah berikut:
```bash
ssh ubuntu@157.15.40.83 -p 7112
```
Setelah berhasil masuk ke VPS, repository project kemudian di-clone dari GitHub dan container dijalankan menggunakan Docker Compose.
Langkah-langkah yang dilakukan adalah sebagai berikut:
```bash
git clone <repository>
cd <repository>
docker compose up -d --build
```
Container berhasil dijalankan di VPS tanpa error.


# Kendala yang Ditemukan
Walaupun container berhasil berjalan di VPS, terdapat kendala pada saat mencoba mengakses API dari internet.
API hanya dapat diakses dari dalam VPS menggunakan perintah berikut:
```bash
curl 0.0.0.0:8000/health
```
Namun ketika mencoba mengakses API menggunakan browser melalui alamat:
```
http://157.15.40.83:8000/health
```
API tidak dapat diakses.
Hal ini menunjukkan bahwa service FastAPI sebenarnya sudah berjalan di dalam container, namun masih terkendala oleh sebab yang belum diketahui. Masalah ini menyebabkan proses deployment belum dapat diselesaikan sepenuhnya.


# Implementasi yang Direncanakan
Setelah masalah akses API pada VPS berhasil diselesaikan, langkah selanjutnya yang direncanakan dalam tugas ini adalah:
## Konfigurasi Nginx Reverse Proxy
Nginx akan digunakan sebagai reverse proxy yang meneruskan request dari port web server ke API yang berjalan di port 8000. Konfigurasi Nginx akan dilakukan menggunakan Ansible Playbook, sehingga seluruh proses instalasi dan konfigurasi dapat dijalankan secara otomatis.
Sehingga, API nantinya dapat diakses tanpa harus mengakses port secara langsung.

## Implementasi CI/CD dengan GitHub Actions
Setelah deployment server berjalan dengan baik, proses deployment akan diotomatisasi menggunakan GitHub Actions.
Pipeline CI/CD nantinya akan bertugas untuk:
1. Menjalankan proses build Docker image
2. Mengirim perubahan ke VPS
3. Menjalankan container terbaru
4. Melakukan restart service jika diperlukan
Dengan pipeline ini, setiap perubahan pada repository dapat langsung dideploy ke server secara otomatis. Namun implementasi ini belum dapat dilakukan karena proses deployment dasar pada VPS masih mengalami kendala.


# Sumber Belajar
Berikut adalah beberapa sumber yang digunakan selama proses pengerjaan tugas ini:
- **Dockerize FastAPI**
  - https://youtu.be/CzAyaSolZjY?si=mVbS53QeiMOpU5xR
- **VPS Server Tutorial**
  - https://youtu.be/YiwBkRukugw?si=9LE_QnMgRW7XQgDf
- **Ansible Tutorial**
  - https://youtu.be/yARgG7y0O64?si=Umq2T1sPxARwlL9f
  - https://youtu.be/w9eCU4bGgjQ?si=oFGauNzhNDlUPxMW
- **Nginx Reverse Proxy**
  - https://youtu.be/ZmH1L1QeNHk?si=FmJTvK0YOQq7ay-W
