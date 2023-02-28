from socket  import *
import pickle
import const #- addresses, port numbers etc. (a rudimentary way to replace a proper naming service)
import threading

server_sock = socket(AF_INET, SOCK_STREAM) # socket for clients to connect to this server
server_sock.bind((const.CHAT_SERVER_HOST, const.CHAT_SERVER_PORT))
server_sock.listen(5) # may change if too many clients

print("Chat Server is ready...")

class Thread(threading.Thread):
    # Override in class Thread methods init and run
    # Defines socket
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.conn = conn
    #Defines run method in Thread class  
    def run(self):
        #
        # Get a message from a sender client
        marshaled_msg_pack = self.conn.recv(1024)   # receive data from client
        msg_pack = pickle.loads(marshaled_msg_pack)
        msg = msg_pack[0]
        dest = msg_pack[1]
        src = msg_pack[2]
        print("RELAYING MSG: " + msg + " - FROM: " + src + " - TO: " + dest) # just print the message and destination
        #
        # Check that the destination exists
        try:
            dest_addr = const.registry[dest] # get address of destination in the registry
        except:
            self.conn.send(pickle.dumps("NACK")) # to do: send a proper error code
            pass
        else:
            print("Server: sending Ack to " + src)
            self.conn.send(pickle.dumps("ACK")) # send ACK to client
        conn.close() # close the connection
        #
        # Forward the message to the recipient client
        client_sock = socket(AF_INET, SOCK_STREAM) # socket to connect to clients
        dest_ip = dest_addr[0]
        dest_port = dest_addr[1]
        try:
            print("Server: Trying to connect to (" + dest_ip + "," + str(dest_port) + ")")
            client_sock.connect((dest_ip, dest_port))
        except:
            print ("Error: Destination client is down")
            pass
        msg_pack = (msg, src)
        marshaled_msg_pack = pickle.dumps(msg_pack)
        client_sock.send(marshaled_msg_pack)
        marshaled_reply = client_sock.recv(1024)
        reply = pickle.loads(marshaled_reply)
        if reply != "ACK":
            print("Error: Destination client did not receive message properly")
        else:
            print("Server: Received Ack from client")
            return
        client_sock.close()

while True:
    (conn, addr) = server_sock.accept()  # returns new socket and addr. client
    print("Chat Server: client is connected from address " + str(addr))
    Thread_msg = Thread(conn).start() # Calls method run in Thread class with .start() to start server

