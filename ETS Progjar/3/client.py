import socket
import json
import logging
import threading
import datetime
import random
from tabulate import tabulate

server_address = ('172.16.16.101', 12000)

def make_socket(destination_address='localhost',port=12000):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        logging.warning(f"connecting to {server_address}")
        sock.connect(server_address)
        return sock
    except Exception as ee:
        logging.warning(f"error {str(ee)}")

def deserialisasi(s):
    logging.warning(f"deserialisasi {s.strip()}")
    return json.loads(s)

def send_command(command_str):
    alamat_server = server_address[0]
    port_server = server_address[1]
    sock = make_socket(alamat_server,port_server)

    logging.warning(f"connecting to {server_address}")
    try:
        logging.warning(f"sending message ")
        sock.sendall(command_str.encode())
        # Menunggu respons hingga socket selesai (tidak ada data lagi)
        data_received="" #empty string
        while True:
            # socket tidak menerima seluruh data secara bersamaan, data diterima secara bertahap (datang sebagian), bersambung hingga akhir proses
            data = sock.recv(16)
            if data:
                # data tidak kosong, bersambung dengan konten sebelumnya
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                # tidak ada data lagi, proses diberhentikan memakai break
                break
        # pada bagian ini, data_received (string) akan berisikan seluruh data yang datang dari socket
        # agar bisa menggunakan data_received sebagai dikte, maka perlu memuatnya menggunakan json.loads()
        hasil = deserialisasi(data_received)
        logging.warning("data received from server:")
        return hasil
    except Exception as ee:
        logging.warning(f"error during data receiving {str(ee)}")
        return True

def getdatapemain(nomor=0):
    cmd=f"getdatapemain {nomor}\r\n\r\n"
    hasil = send_command(cmd)
    if (hasil):
        pass
    else:
        print("kegagalan pada data transfer")
    return hasil

def lihatversi(is_secure=True):
    cmd=f"versi \r\n\r\n"
    hasil = send_command(cmd)
    return hasil

def getdatapemain_multithread(total_request, table_data):
    total_response = 0
    texec = dict()
    catat_awal = datetime.datetime.now()

    for k in range(total_request):
        # bagian ini merupakan bagian yang mengistruksikan eksekusi getdatapemain secara multithread
        texec[k] = threading.Thread(
            target=getdatapemain, args=(random.randint(1, 20),))
        texec[k].start()

    # setelah menyelesaikan tugasnya, dikembalikan ke main thread dengan join
    for k in range(total_request):
        if (texec[k]):
            total_response += 1
        texec[k].join()

    catat_akhir = datetime.datetime.now()
    selesai = catat_akhir - catat_awal
    table_data.append([total_request, total_request, total_response, selesai])

if __name__ == '__main__':
    h = lihatversi()
    if (h):
        print(h)
    total_request = [1, 5, 10, 20]
    table_data = []
    
    for request in total_request:
        getdatapemain_multithread(request, table_data)
        
    table_header = ["Jumlah Thread", "Jumlah Request", "Jumlah Response", "Latency"]
    print(tabulate(table_data, headers=table_header, tablefmt="fancy_grid"))