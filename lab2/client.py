import socket

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
    num_of_args = 0
    match function:
        case "+":
            num_of_args = 4
        case "*":
            num_of_args = 3
        case "-" | "/" | "%":
            num_of_args = 2

    print("Enter {} arguments".format(num_of_args))
    arguments = []
    for _ in range(num_of_args):
        arguments.append(input())
    
    return arguments

def demo():
    functions = ["+", "-", "*", "/", "%"]
    for function in functions:
        print("Function: " + function)
        arguments = read_arguments(function)
                
        request = function + " " + " ".join(str(argument) for argument in arguments)
       
        client_socket = start_client()
        try:
            client_socket.send(request.encode("UTF-8"))
        except:
            print("Could not send request to host")
        
        try:
            response = client_socket.recv(256).decode("UTF-8")
            print(response)
            if len(response) > 0:
                print("Response: " + response)
            else:
                print("Did not receive response")    
        except:
            print("Did not receive response")
            
        client_socket.close()
        print()
    
    
enable_demo = True
# demo για τις 5 λειτουργίες με arguments από το πληκτρολόγιο
if enable_demo:
    demo()
    function = "x"
else:
    # Τρέχει μέχρι ο χρήστης να δώσει μη valid function 
    function = input("Enter function (+, -, *, /, %), anything else to exit\n? ")
    while any([function == "+", function == "-", function == "*", function == "/", function == "%"]):
        #Διαβάζει τα arguments απ'τον χρήστη, δεν γίνεται κάποιος έλεγχος ορθότητας
        arguments = read_arguments(function)
                
        request = function + " " + " ".join(str(argument) for argument in arguments)
       
        # Ανοίγει σύνδεση αφού έχει λάβει τα στοιχεία από τον χρήστη για να μην αφήνει στον server σε αναμονή
        client_socket = start_client()
        try:
            client_socket.send(request.encode("UTF-8"))
        except:
            print("Could not send request to host")
        
        try:
            response = client_socket.recv(256).decode("UTF-8")
            print(response)
            # Αν λάβει κενή απάντηση, δεν την εμφανίζει
            if len(response) > 0:
                print("Response: " + response)
            else:
                print("Did not receive response")    
        except:
            print("Did not receive response")
            
        client_socket.close()
        print()
        
        function = input("Enter function (+, -, *, /, %), anything else to exit\n? ")
       
        
print("Received " + function + " as input, exiting")   
