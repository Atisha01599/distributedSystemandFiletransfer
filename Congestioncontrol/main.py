
import socket
import time
import hashlib
import matplotlib.pyplot as plt

# Server connection information
server_host = "10.17.7.218"
# server_host = "127.0.0.1"
server_port = 9802

# Create a socket for udp connevtion
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket.settimeout(0.03) 

starttime = time.time()*1000
predicted_rtt = 0.4
predicted_deviation=0
Constant1=0.25
constant2=0.125

requestInterval = 0.0001

def change_timeOut(clientsocket,current_rtt):
    global predicted_rtt
    global predicted_deviation
    global Constant1
    global constant2
    actual_deviation=abs(current_rtt-predicted_rtt)
    predicted_rtt=Constant1*current_rtt+(1-Constant1)*predicted_rtt
    predicted_deviation=constant2*actual_deviation+(1-constant2)*predicted_deviation
    timeOut=predicted_rtt+4*predicted_deviation
    clientsocket.settimeout(timeOut)

try:
    # Step 1: sendsize alog with reset command to get pennalty 
    clientSocket.sendto("SendSize\nReset\n\n".encode(), (server_host, server_port))
    response, data= clientSocket.recvfrom(4096)
    recievedResponse = response.decode()
    totalDataSize = int(recievedResponse.split(':')[1])
    print(f"Total bytes to receive: {totalDataSize}")


    # Step 2: Send data requests
    offset = 0
    totalMaxRequestSize = 1448
    
    requestTime = []
    requestOffset =[]
    currentTime =[]
    currentOffset =[]
    
    timeout =0
    response =0
    currentWindow =1
    totalPenaltyForThisWindow = 0
    window_sizes = []

    offsets = []
    #defining a data buffer to store data recieved from server
    changertt1 =0
    rtt2 =0
    firstResponse = True 
    offsetkeys = range(0, totalDataSize, 1448) 

    dic = {key: "" for key in offsetkeys}
    
    dataRemainingOffset = list(offsetkeys)
    
    time1 = time.perf_counter()*1000
    data_buffer = bytearray(totalDataSize)  
    while len(dataRemainingOffset) > 0:            
       
        time2 = time.perf_counter()*1000
        totaltime = time2 -time1
        requestTime.append(totaltime)
        # requestOffset.append(offset)
        
        try:
                totalPenaltyForThisWindow = 0
                RequiredOfset = offset
                # send request
                for i in range(0,min(currentWindow, len(dataRemainingOffset)),1):
                    if totalDataSize - dataRemainingOffset[i] < totalMaxRequestSize:
                        bytenumber = totalDataSize - dataRemainingOffset[i]
                    else:
                        bytenumber = totalMaxRequestSize
                    request = f"Offset: {dataRemainingOffset[i]}\nNumBytes: {bytenumber}\n\n"
                    clientSocket.sendto(request.encode(), (server_host, server_port))
                    time.sleep(requestInterval)
                    if i == min(currentWindow, len(dataRemainingOffset)) -1:
                        changertt1 = time.time()*1000 - starttime
                    
            
                
                        
                for i in range(0,min(currentWindow, len(dataRemainingOffset))):  
                    try:        
                        responseForData,socketData = clientSocket.recvfrom(4096)
                        response=response+1
                        if firstResponse:
                            rtt2 = time.time()*1000 - starttime
                            firstResponse =  False
                        time2 = time.perf_counter()*1000
                        totaltime = time2 -time1
                        currentTime.append(totaltime)
                        currentOffset.append(offset)

                        data = responseForData.decode()
                        data_parts = data.split("\n",3)
                        # offsetRecieved = int(data_parts[0][8:])
                        # data_squished = (data_parts[2] == "Squished")
                        # value_to_store = data_parts[-1]
                        offsetRecieved = int(data_parts[0][8:])
                        data_squished = data_parts[2] == "Squished"
                        value_to_store = data_parts[3][1:] if data_squished else data_parts[3]
                        # You can use a dictionary comprehension to update the 'dic' dictionary.
                        dic[offsetRecieved] = value_to_store

                        # If 'offsetRecieved' should be removed from 'dataRemainingoffset', you can add this condition.
                        if not data_squished:
                            value_to_remove =offsetRecieved 
                            if value_to_remove in dataRemainingOffset:
                                dataRemainingOffset.remove(value_to_remove)
                            else:
                            # Handle the case where the value is not in the list
                               pass
                            # dataRemainingOffset.remove(offsetRecieved)

                        offsets.append(offsetRecieved)
                        # Print a message based on whether it's "Squished" or not.
                        if data_squished:
                            print("SQUISHEDDD")
                            time.sleep(0.01)
                            
                        print(offsetRecieved)

                        
                    except socket.timeout:
                        print("Request timed out.")
                        timeout=timeout+1
                        totalPenaltyForThisWindow  =  1
                        break

                        
                        
                firstResponse =True        
                change_timeOut(clientSocket,(rtt2-changertt1)/1000)       
                if totalPenaltyForThisWindow==1:
                    currentWindow = currentWindow//2 
                    
                if totalPenaltyForThisWindow ==0:
                    currentWindow = min(16,currentWindow*2)
                    
                if currentWindow <1:
                    currentWindow =1
                
                print(f"***************************************************************************************")   
                window_sizes.append(currentWindow)
                    
                print("current window size :",currentWindow)
                        

        except socket.timeout:
                print("Request timed out.")
                timeout=timeout+1
                print(timeout)
                

    
    vayuData = ''.join(dic.values())    
    md5 = hashlib.md5()
    md5.update(vayuData.encode("utf-8"))
    generatedmd5 = md5.hexdigest()

    finalSubmitRequest = f"Submit: [mcs232498mcs232491@team]\nMD5: {generatedmd5}\n\n"
    clientSocket.sendto(finalSubmitRequest.encode(), (server_host, server_port))
    finalSubmitData,socketData = clientSocket.recvfrom(4096)
    finalSubmitResponse= finalSubmitData.decode()

    # Extracting Server reply
    temp = finalSubmitResponse.strip().split('\n')
    print("Reply Recieved from Server")
    
    totalTime = float(temp[1].split(': ')[1])
    

    totalTime = float(temp[1].split(': ')[1])
    print("Time taken in  ms",totalTime)
   
    penalty = temp[2].split(': ')[1]
    print("Penalty",penalty)
    result = temp[0].split(': ')[1]
    print("Result",result)
    

except Exception as e:
    print(f"Error connecting a server {e}")


clientSocket.close()

# plt.scatter(requestTime,requestOffset,label='Request',color='blue') 
# plt.scatter(currentTime,currentOffset,label='Request',color='red') 
# plt.xlabel('TIME')
# plt.ylabel('offset')
# plt.title("request and response time and offset")
# plt.grid()
# plt.show()

plt.plot(requestTime, window_sizes, label='Window Size', color='green')
plt.xlabel('Time (ms)')
plt.ylabel('Window Size')
plt.title("Window Size over Time")
plt.grid()
plt.legend()
plt.show()

# plt.plot(offsets, window_sizes, label='Window Size', color='green')
# plt.xlabel('Current Offset')
# plt.ylabel('Window Size')
# plt.title("Window Size with respect to Current Offset")
# plt.grid()
# plt.legend()
# plt.show()


