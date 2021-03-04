import socket
import sys
import struct
import time
import random

ack_packet_id = "1010101010101010"
data_packet_id = "0101010101010101"
bufferSize = 2048


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

def recv_file(s,filename,fdata):

    loss_fl = 1
    exp_seq_num = 0
    while(True):
        packet, client_address = s.recvfrom(bufferSize)

        packet = packet.decode("utf-8")
        # print(packet)
        seq_num = packet[:32]
        # time.sleep(0.05)
        # print("got:" + str(int(seq_num,2)) + " , exp: "+str(exp_seq_num))
        checksum = packet[32:48]
        Identifier_field = packet[48:64]
        data = packet[64:]

        cal_checksum = compute_checksum(data)

        rand_num = random.random()

        if rand_num > p:
            if Identifier_field == data_packet_id and checksum == "{0:016b}".format(cal_checksum) and seq_num == "{0:032b}".format(exp_seq_num):
                # write to file
                # if seq_num == "{0:032b}".format(exp_seq_num):
                #     print("write:",exp_seq_num)
                f = open(filename,"a")
                f.write(data)
                f.close()
                exp_seq_num += 1
                    # print(data)

                # print("got:",exp_seq_num)

                #send ack
                zero_field = "{0:016b}".format(0)
                ack_pkt = str(seq_num) + str(zero_field) + ack_packet_id
            
                # Sending a reply to client
                # if exp_seq_num != 2:
                s.sendto(str.encode(ack_pkt), client_address)
                loss_fl = 1
                
        else:
            if loss_fl == 1:
                print("Packet loss, sequence number = " + str(exp_seq_num))
                # zero_field = "{0:016b}".format(0)
                # ack_pkt = str(int(seq_num,2)+1) + str(zero_field) + ack_packet_id
            
                # # Sending a reply to client
                # # if exp_seq_num != 2:
                # s.sendto(str.encode(ack_pkt), client_address)
                loss_fl = 0
def main():
    if len(sys.argv) < 4:
        print("Enter: py server <server port num> <filename> <p>")
        exit()
    global p 
    server_port = int(sys.argv[1])
    filename = sys.argv[2]
    p = float(sys.argv[3])

    server_address = ('127.0.0.1',server_port)
    s = socket.socket(family=socket.AF_INET, type = socket.SOCK_DGRAM)
    s.bind(server_address)
    fdata = ""
    recv_file(s, filename, fdata)
    s.close()

if __name__ == "__main__":
    main()