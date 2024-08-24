import sys
import socket
import threading
import os
import time
import matplotlib.pyplot as plt

# Initialize a list to store processing times
processing_times = []
submit = "SUBMIT\n"
submit_ID = "mcs232498@onepiece\n"
submit_line = "1000\n"
rec_count = int(0)
line_table = [0] * 1000
lock = threading.Lock()
threads = []
start_time = 0.0


PORT= 12345
SERVER="10.194.58.44"
ADDR=(SERVER,PORT)

file_name = "server_response.txt"

try:
    file_pointer = open(file_name, 'w')
except:
    print("[ERROR] Unable to open file [%s]" % (file_name))


def plot_efficiency_graph(data):
    plt.plot(data)
    plt.xlabel('Number of lines')
    plt.ylabel('Processing Time (ms)')
    plt.title('Efficiency Plot')
    plt.savefig('master_efficiency_plot.jpg', format='jpg')


def retrieve_file(thread_run, server_domain, server_port, client_socket):
    thread_id = threading.get_ident()
    global rec_count
    global lock
    global start_time
    global processing_times
    

    
    try:
                
        start_time = time.time()
        client_socket.sendall("SESSION RESET\n".encode())
        data_rec = client_socket.recv(1024).decode()
        print("debug ", data_rec)
        message = "SENDLINE\n"
        interval = 1.0 / 100
        
        try:
            while rec_count != 1000:
                client_socket.sendall(message.encode())
                line_count = 0
                received_data = ""
                
                while rec_count != 1000 and line_count != 2:
                    data = client_socket.recv(1024)
                    received_data += data.decode('utf-8')
                    line_count = received_data.count('\n')
    
                
                
                if rec_count != 1000 and received_data[0:2] != "-1":
                    lines = received_data.split('\n')
                    line_number = int(lines[0])
                    # print(lines[0])
                    
                    if rec_count != 1000 and line_table[line_number] != 1:
                        lock.acquire()
                        current_time = time.time()
                        elapsed_time = (current_time - start_time) * 1000
                        file_pointer.write(received_data)
                        line_table[line_number] = 1
                        rec_count += 1
                        # print(rec_count)
                        processing_times.append(elapsed_time)
                        lock.release()
               # else:
                   # print(received_data[0:2])
        except Exception as e:
            print("Error in retrieval")
            
    except ConnectionRefusedError:
        print("[ERROR] Thread ID [%s]: Socket connect error" % thread_id)

    print("[INFO] Thread ID [%s]: Thread End" % thread_id)
    file_pointer.close()

# Function to send a file to the server over the same connection
def send_file(thread_run, server_domain, server_port, file_path, client_socket):
    thread_id = threading.get_ident()
    
    try:
        with open(file_path, 'rb') as file:
            file_data = file.read()
        
        client_socket.sendall(submit.encode())
        print("SUBMIT")
        client_socket.sendall(submit_ID.encode())
        print("team ID")
        client_socket.sendall(submit_line.encode())
        print("1000 lines submitted")
        # Send the file data to the server
        client_socket.sendall(file_data)
        print("[INFO] Thread ID [%s]: File sent to the server" % thread_id)
            
    except Exception as e:
        print("[ERROR] Thread ID [%s]: File sending error [%s]" % (thread_id, str(e)))

    try:
        submission_data = ""
        lcount = 0
                
        while lcount != 1:
            sdata = client_socket.recv(1024)
            submission_data += sdata.decode('utf-8')
            lcount = submission_data.count('\n')

        sline = submission_data.split('\n')
        print(sline[0])

    except Exception as e:
        print("Error in submission")
    try:
        sline_list=submission_data.split("-")[3].split(", ")
        total_time = int(sline_list[2]) - int(sline_list[0])
        print(f'Total time is {total_time}')
    
    except Exception as e:
        print("Error in time printing")

    if client_socket:
            client_socket.close()
    print("[INFO] Thread ID [%s]: Thread End" % thread_id)

def client_connection(connection, address):
    global rec_count
    global lock
    global file_pointer
    global start_time
    global processing_times
    print(f"New connection connected with IP : {address}")

    try:
        while rec_count != 1000:
            connection.sendall("SENDLINE\n".encode())
            line_input = ""
            line_input += connection.recv(1024).decode('utf-8')
            print("Line input")
            print(line_input)
            message_input = ""
            if rec_count != 1000 and line_input:
                line_number = line_input.split('\n')
                if line_number[0] == "WAIT\n":
                    continue    
                if rec_count != 1000 and line_table[int(line_number[0])] == 0:
                    connection.sendall("SENDMESSAGE\n".encode())

                    lcount = 0
                    
                    while lcount != 1:
                        m = connection.recv(1024)
                        message_input += m.decode('utf-8')
                        lcount = message_input.count('\n')

                    print("Message input")
                    print(message_input)
                    if rec_count != 1000 and message_input:
                        line_content = line_input + message_input
                        lock.acquire()

                        current_time = time.time()
                        elapsed_time = (current_time - start_time) * 1000
                        file_pointer.write(line_content)
                        line_table[int(line_number[0])] = 1
                        rec_count += 1

                        processing_times.append(elapsed_time)
                        lock.release()

        
        connection.sendall("STOP\n".encode())
        file_path = 'server_response.txt'
    except Exception as e:
        print(f'Exception Occured: {e}')

    try:
        with open(file_path, 'rb') as file:
            file_data = file.read()
        
        connection.sendall(file_data)

            
    except Exception as e:
        print("[ERROR] Thread ID [%s]: File sending error [%s]" % (address ,str(e)))
    connection.close()

def master_start():
    global threads
    global master
    PORT= 12345
    SERVER="10.194.58.44"
    ADDR=(SERVER,PORT)

    master=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    master.bind(ADDR)
    master.listen(3)
    print(f"[LISTENING Server is listening on {SERVER}]")
    for i in range(3):
        print("before accept")
        conn,addr=master.accept()
        print("after accept")
        thread=threading.Thread(target=client_connection,args=(conn,addr))
        thread.start()
        threads.append(thread)
        print(f"[ACTIVE CONNECTIONS] {threading.active_count()-1}")                 






def main():
    print("Hello")
    server_domain = '10.17.7.134'
    server_port = 9801
    thread_run = True
    global threads
    global master
    

    file_path = 'server_response.txt'
    
    client_socket = None

    
    
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_domain, server_port))
        print("[INFO] Connected to Domain [%s] Port [%s]" % (server_domain, server_port))
        

        t1 = threading.Thread(target=retrieve_file, args=(lambda: thread_run, server_domain, server_port, client_socket))
        t1.start()

        print("Mater starting")
        t3 = threading.Thread(target=master_start)
        t3.start()        
        t1.join()


        t2 = threading.Thread(target=send_file, args=(lambda: thread_run, server_domain, server_port, file_path, client_socket))
        t2.start()
        

        t2.join()
        for t in threads:
            t.join()

        t3.join()
        print("Master completed")
    
    except ConnectionRefusedError:
        print("[ERROR] Connection to server refused.")
    
    finally:
        if client_socket:
            client_socket.close()
    

    plot_efficiency_graph(processing_times)

if __name__ == "__main__":
    main()
