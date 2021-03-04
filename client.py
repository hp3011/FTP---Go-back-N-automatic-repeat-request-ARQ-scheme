import socket
import sys
import time
import struct
import threading

ack_packet_id = "1010101010101010"
data_packet_id = "0101010101010101"

GLB_success_tx = 0
timer = {}
last_send = 0
last_ack = -1

def compute_checksum(data):
    csum = 0
    data = bytes(data,"utf-8")
    data_len = len(data)
    if (data_len% 2):
        data_len += 1
        data += struct.pack('!B', 0)

    for i in range(0, data_len, 2):
        w = ((data[i]) << 8) + (data[i + 1])
        csum += w
    csum = (csum >> 16) + (csum & 0xFFFF)
    return ~csum & 0xFFFF

def check_ack():
    global GLB_success_tx, last_send, N, timer, last_ack, st_time
    
    while len(timer) != 0:
        try:
    
            ack_pkt = s.recvfrom(2048)
            # Stop the timer for the recevied ACK
            ack_num = int(ack_pkt[0][0:32],2)
            if last_ack == ack_num:
                time_taken = time.time() - st_time
                print("Delay = " + str(time_taken))
            GLB_success_tx += 1

            # print(timer)
            # print("GL ACK and ack = ", GLB_success_tx, ack_num)
            # print("original ack, exp:",ack_num, last_send)
            
            if ack_num in timer:
                timer[ack_num].cancel()
                timer.pop(ack_num)

            wnd_size = N - ((last_send + 1) - (GLB_success_tx))
            if wnd_size > 0:
                tx_window_N(last_send + 1, N - (last_send - GLB_success_tx + 1))

        except:
            print("Exception Error")
            # print("Timeout GL on ACK", GLB_success_tx)
            # print("Timeout original ack, exp:",ack_num, last_send)
            # tx_window_N(GLB_success_tx,N)


def retransmit():
    global GLB_success_tx, timer, st_time
    if GLB_success_tx in timer and threading.current_thread() == timer[GLB_success_tx]:
        print("Timeout, sequence number = " + str(GLB_success_tx))

        tx_window_N(GLB_success_tx,N)
        check_ack()
    else:
        # print("timer len: ",len(timer))
        threading.current_thread().cancel()

def tx_window_N(st,wnd_size):
    global last_send, timer, readfile, N, last_ack
    # print("window GLB succes func = ",GLB_success_tx)
    # stti = time.time()
    for seq_num in range(st,st+wnd_size):
        # filedata = "RFC file : send from the client to the server for testing purposes."
        filedata = readfile
        data_st = ((seq_num)*MSS)
        if data_st > len(filedata):
            # print("St > len: ", data_st,len(filedata),seq_num)
            return
        data_end = ((seq_num + 1)*MSS)
        if data_end >= len(filedata):
            data_end = len(filedata)
            last_ack = seq_num
            # print("end ", data_end,len(filedata))
        data =filedata[data_st:data_end]
        checksum = compute_checksum(data)

        header = "{0:032b}".format(seq_num) + "{0:016b}".format(checksum) + str(data_packet_id)
        send_data= header + data

        s.sendto(str.encode(send_data), server_address)
        last_send = seq_num
        t = threading.Timer(1, retransmit)
        t.start()
        timer[seq_num] = t
    # print("1024 transmit time = ", (time.time() - stti))
    # time.sleep(5)

def rdt_send():
    global GLB_success_tx, N
    tx_window_N(GLB_success_tx ,N)
    check_ack()

def main():
    if len(sys.argv) < 5:
        print("Enter: py client <server port num> <filename> <window size N> <MSS>")
        exit()
    global server_address, MSS, N, s, readfile, GLB_success_tx, st_time

    server_port = int(sys.argv[1])
    filename = sys.argv[2]
    N = int(sys.argv[3])
    MSS = int(sys.argv[4]) 

    server_address = ('127.0.0.1',server_port)

    with open(filename,encoding ='utf-8') as f:
        readfile = f.read()

    s = socket.socket(family=socket.AF_INET, type = socket.SOCK_DGRAM)
    st_time = time.time()
    rdt_send()
    s.close()

if __name__ == "__main__":
    main()