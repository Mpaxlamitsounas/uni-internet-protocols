import socket
import _thread
import struct

def start_server():
    # Επιχειρεί να αρχίσει τον server
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("", 12000))
        server_socket.listen(10)
        print("The server is ready to receive")
        # Αν αποτύχει βγάζει μήνυμα και τερματίζει το πρόγραμμα
    except:
        print("Failed to start server")
        exit()
    
    # Αλλιώς επιστρέφει το socket στο οποίο τρέχει
    return server_socket
    
def parse(request):
    function, arg0, arg1, arg2, arg3, _ = request
    return function.decode(), [arg0, arg1, arg2, arg3]

def validate_args(function, arguments):
    
    error_message = ""
    
    # Ο ορισμός του valid αλλάζει ανα function
    allowed_range = range(0, 60001)
    match function:
        case "+":
            valid_num_args = 4
    
        case "*":
            valid_num_args = 3
                        
        case "-" | "/" | "%":
            valid_num_args = 2
            if function == "-":
                allowed_range = range(0, 30001)
                
        # Αν δεν είναι κανένα από τα παραπάνω, δεν είναι ορισμένo function
        case _:
            return False, "\tUnrecognised function \"" + function + "\"\n"
        
    # Ελέγχει αν ο αριθμός arguments είναι σωστός για το function
    for i, argument in enumerate(arguments):
        if (argument != 0 and i+1 > valid_num_args):
            error_message = "\tReceived non zero value for argument not used\n"

    # Ελέγχει ποιά αριθμοί arguments είναι εκτός πεδίου ορισμού της πράξης
    args_out_of_range = []
    for argument in arguments:
        if argument not in allowed_range:
            args_out_of_range.append(str(argument))
    
    # Αν βρεθούν παραβιάσεις, επιστρέφει ποιά ήταν εκτός ορίων
    if len(args_out_of_range) > 0: 
        return False, error_message + "\tArgument(s) {} out of allowed range of [{}, {}]".format(", ".join(args_out_of_range), allowed_range.start, allowed_range.stop) + "\n"
    
    return True, error_message

def calculate(function, arguments, panic):
    result = ""
    
    if function == '/' and arguments[1] == 0:
        result += "Cannot divide by 0"
    elif function == '%' and arguments[1] == 0:
        result += "Modulo of 0 is undefined"
    elif not panic:
        match function:
            case "+":
                result = sum(arguments)
                    
            case "-":
                result = arguments[0] - arguments[1]
                    
            case "*":
                result = arguments[0] * arguments[1] * arguments[2]
                            
            case "/":
                result = arguments[0] / arguments[1]
                    
            case "%":
                result = arguments[0] % arguments[1]

    return result

def threaded_client(connection_socket, addr):
    
    try:
        request = struct.unpack('!c4H256s', connection_socket.recv(265))
    except:
        print("Failed to connect with client, or unpack request")
        return
    
    result = "In \"" + str(request) + "\":\n"

    # Αν δεχθεί άδειο request, ο server crashάρει
    if len(request) > 0:
        
        panic = False
        # panic mode == Αν βρεθεί λάθος, ο server θα κάνει όλα τα checks κανονικά αλλά όχι τελικούς υπολογισμούς 
        # ώστε να δώσει στον χρήστη όσο περισσότερα λάθη που μπορεί να έχει κάνει στο request με το response
        function, arguments = parse(request)
        
        valid, error_message = validate_args(function, arguments)
        if not valid:
            panic = True
            result += error_message
            
        if not panic:
            result = "\t" + str(calculate(function, arguments, panic))

        # Εμφανίζει το request και αποτέλεσμα στο τέλος
        print(function + ' ' + str(arguments) + " : \n" + result)

        result = struct.pack('!c4H256s', '0'.encode(), 0, 0, 0, 0, result.encode())
        try:
            connection_socket.send(result)  
        except:
            print("Failed to send response to client")
        connection_socket.close()
    else:
        print("Received empty request")


server_socket = start_server()

while True:
    # Ο server είναι σε αναμονή μέχει να λάβει σύνδεση και δεδομένα
    try:
        connection_socket, addr = server_socket.accept()
        _thread.start_new_thread(threaded_client, (connection_socket, addr))
        # Αν η σύνδεση αποτύχει, το~ αγνοεί και μπαίνει ξανά σε αναμονή
    except:
        print("Failed to connect with client")
        continue
    
