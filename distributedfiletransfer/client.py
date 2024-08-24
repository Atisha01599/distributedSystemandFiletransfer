import socket
import threading


SERVER_HOST = "10.17.7.134"
SERVER_PORT = 9801  


MASTER_HOST="10.194.58.44"
MASTER_PORT=12345
file_input=""

flag_master=[0]*1000
flag_server=[0]*1000
messages=['']*1000
cnt_master=0
cnt_server=0
queue=[]
stop_master=0
final_stop=0

def connect_server(thread_run, server_host,server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_host, server_port))
    client_socket.sendall("SESSION RESET\n".encode())
    data_recv=client_socket.recv(32).decode('utf-8')

    message = "SENDLINE\n"
    global file_input
    global cnt_server
    global cnt_master
    global stop_master
    global final_stop

    while cnt_server!=1000 and stop_master==0:
        client_socket.sendall(message.encode())
        response=""
        line_count=0

        while line_count<2:
            data = client_socket.recv(1024).decode('utf-8')
            response+=data
            line_count +=data.count('\n') 
              
        if(response[0:2]=="-1"):
            continue


        rp=response.split("\n")
        line,message1=rp[0],rp[1]
        line=int(line)


        if flag_server[line]==0:
            flag_server[line]=1
            messages[int(line)]=message1+"\n"
            cnt_server +=1

            if flag_master[line]==0:
                flag_master[line]=1
                cnt_master+=1
                queue.append(line)



    while final_stop==0:
        continue
    send_file = "SUBMIT\n" + "mcs232498@onepiece\n" + "1000\n" + file_input
    try:
        client_socket.sendall(send_file.encode())
    except Exception as e:
        print("[ERROR] File sending error : [%s]" % str(e))

    try:
        submission_data = ""
        lcount = 0
                
        while lcount != 1:
            sdata = client_socket.recv(1024)
            submission_data += sdata.decode('utf-8')
            lcount = submission_data.count('\n')

        sline = submission_data.split('\n')

    except Exception as e:
        print("Error in submission")
    try:
        sline_list=submission_data.split("-")[3].split(", ")
        total_time = int(sline_list[2]) - int(sline_list[0])
        print(f'Total time taken is {total_time} ms')
    
    except Exception as e:
        print("Error in time printing")
    
    client_socket.close()

def connect_master(thread_run, master_host,master_port):
    global file_input
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((master_host, master_port))
    print(f'[{master_host}] connected')
    message=""
    while True:
        previous_line=-1
        while True:
            if len(queue)==0:
                break
            current_line=queue.pop(0)
            if message=="":
                message = client_socket.recv(128).decode('utf-8')
            if message=="STOP\n":
                print("STOPPED\n")
                break
            if message=="SENDMESSAGE\n":
                client_socket.sendall(messages[previous_line].encode())
                message=""
                if message=="":
                    message=client_socket.recv(128).decode('utf-8')
                if message=="STOP\n":
                    print("STOPPED\n")
                    break
            client_socket.sendall((str(current_line)+"\n").encode())
            message=""
            previous_line=current_line
        if previous_line!=-1 and message!="STOP\n":
            if message=="":
                message = client_socket.recv(128).decode('utf-8')
            if message=="SENDMESSAGE\n":
                client_socket.sendall(messages[previous_line].encode())
                message=""
                if message=="":
                    message=client_socket.recv(128).decode('utf-8')

            if message=='STOP\n':
                print("STOPPED\n")
                break

        if cnt_master>=1000 or message=="STOP\n":
            break

    global stop_master
    global final_stop
    global file_input
    lcount = 0
    stop_master=1
    while lcount != 2000:
        message_recv = client_socket.recv(1024).decode('utf-8')
        file_input += message_recv
        lcount += message_recv.count('\n')
    
    final_stop=1
    client_socket.close()



def main():
    thread_run = True
    t1 = threading.Thread(target=connect_server, args=(lambda: thread_run, SERVER_HOST, SERVER_PORT))
    t1.start()
    t2 = threading.Thread(target=connect_master, args=(lambda: thread_run, MASTER_HOST, MASTER_PORT))
    t2.start()
    t2.join()
    t1.join()

if __name__=='__main__':
    main()

