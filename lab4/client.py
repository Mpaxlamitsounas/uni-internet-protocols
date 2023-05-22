import socket
import struct
import sys

def start_client():
    # Επιχειρεί να συνδεθεί στον server
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("localhost", 12000))
    except:
        print("Could not create socket or connect to host")
        exit()
        
    return client_socket

# Διαβάζει τον σωστό αριθμό argument από τον χρήστη
def read_arguments(function):
    error_message = ""
    num_of_args = 0
    match function:
        case '+':
            num_of_args = 4
        case '*':
            num_of_args = 3
        case '-' | '/' | '%':
            num_of_args = 2

    print("Enter {} arguments, one by one".format(num_of_args))
    arguments = [0, 0, 0, 0]
    args_not_digits = []
    args_out_of_range = []
    for i in range(num_of_args):
        arg = input()
        try:
            arguments[i] = int(arg)
            if arguments[i] not in range(0, 60001):
                args_out_of_range.append(arguments[i])
        except:
            args_not_digits.append(arg)
            
    if (len(args_not_digits) > 0):
        error_message += "Failed to parse arguments: " + ", ".join(args_not_digits) + "\n"
        
    if (len(args_out_of_range) > 0):
        error_message += "Parsed arguments outside of valid range: " + ", ".join(args_out_of_range) + "\n"
    
    return error_message, arguments

def demo():
    functions = ['+', '-', '*', '/', '%']
    for function in functions:
        print("Function: " + function)
        error_message, arguments = read_arguments(function)
        
        if len(error_message) == 0 :
            request = struct.pack('!c4H256s', function.encode('utf-8'), arguments[0], arguments[1], arguments[2], arguments[3], ''.encode())
            
            client_socket = start_client()
            try:
                client_socket.send(request)
            except:
                print("Could not send request to server")
                
            try:
                response = struct.unpack('!c4H256s', client_socket.recv(265))
                response = response[5].decode()
                if len(response) > 0:
                    print("Response: \n" + response)
                else:
                    print("Did not receive response") 
            except:
                print("Did not receive response")
                
            client_socket.close()
        else:
            print(error_message)
            

enable_demo = True
# demo για τις 5 λειτουργίες με arguments από το πληκτρολόγιο
if enable_demo:
    demo()
    function = "x"
else:
    # Τρέχει μέχρι ο χρήστης να δώσει μη valid function 
    function = input("Enter function (+, -, *, /, %), anything else to exit\n? ")
    while any([function == "+", function == "-", function == "*", function == "/", function == "%"]):
        #Διαβάζει τα arguments απ'τον χρήστη
        error_message, arguments = read_arguments(function)
        
        if len(error_message) == 0 :
            request = struct.pack('!c4H256s', function.encode('utf-8'), arguments[0], arguments[1], arguments[2], arguments[3], ''.encode())
            
            # Ανοίγει σύνδεση αφού έχει λάβει τα στοιχεία από τον χρήστη για να μην αφήνει στον server σε αναμονή
            client_socket = start_client()
            try:
                client_socket.send(request)
            except:
                print("Could not send request to server")
                
            try:
                response = struct.unpack('!c4H256s', client_socket.recv(265))
                response = response[5].decode()
                if len(response) > 0:
                    print("Response: \n" + response)
                else:
                    # Αν λάβει κενή απάντηση, δεν την εμφανίζει
                    print("Did not receive response") 
            except:
                print("Did not receive response")
                
            client_socket.close()
        else:
            print(error_message)
        
        function = input("Enter function (+, -, *, /, %), anything else to exit\n? ")
       
 
print("Received " + function + " as input, exiting")   
