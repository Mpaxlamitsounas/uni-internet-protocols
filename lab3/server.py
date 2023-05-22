import socket
import _thread

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
     # Χωρίζει το request στο πρώτο κενό
     function, arguments = request.split(" ", 1)
     # Χωρίζει το δεξί μέρος που έχει τα arguments σε αντικείμενα λίστας
     arguments = arguments.split()
     
     args_not_digit = []
     parsed_arguments = []
     for argument in arguments:
          # Ελέγχει ποιά από αυτά είναι ακέραιοι αριθμοί
          try:
               parsed_arguments.append(int(argument))
          except:
               args_not_digit.append(argument)
     
     # Αν βρεί arguments που δεν μπορεί να μετατρέψει, επιστρέφει ότι μπόρεσε να βρει, και ένα error message
     if len(args_not_digit) > 0:
          return False, function, parsed_arguments, args_not_digit, "Argument(s) " + ", ".join(args_not_digit) + " could not be parsed"
     
     # Αλλιώς επιστρέφει το function και αριθμούς arguments
     return True, function, parsed_arguments, [], ""

def validate_args(function, arguments, num_arguments):
     # Ο ορισμός του valid αλλάζει ανα function
     allowed_range = range(0, 60000)
     match function:
          case "+":
               valid_num_args = 4
     
          case "*":
               valid_num_args = 3
                         
          case "-" | "/" | "%":
              valid_num_args = 2
              if function == "-":
                   allowed_range = range(0, 30000)
                   
          # Αν δεν είναι κανένα από τα παραπάνω, δεν είναι ορισμένo function
          case _:
               return False, "\tUnrecognised function \"" + function + "\"\n"
          
     # Ελέγχει αν ο αριθμός arguments είναι σωστός για το function
     if num_arguments != valid_num_args:
          return False, "Incorrect number of number arguments, must be " + str(valid_num_args)
     
     # Ελέγχει ποιά αριθμοί arguments είναι εκτός πεδίου ορισμού της πράξης
     args_out_of_range = []
     for argument in arguments:
          if argument not in allowed_range:
               args_out_of_range.append(str(argument))
     
     # Αν βρεθούν παραβιάσεις, επιστρέφει ποιά ήταν εκτός ορίων
     if len(args_out_of_range) > 0: 
          return False, "Argument(s) {} out of allowed range of [{}, {}]".format(", ".join(args_out_of_range), allowed_range.start, allowed_range.stop)

     # Δεν γίνεται να επιστραφεί σφάλμα για παραπάνω από 1 error διαφορετικού είδους
     
     return True, ""

def calculate(request, function, arguments, panic):
     result = "In \"" + request + "\":\n"
     match function:
          case "+":
               result = sum(arguments)
                    
          case "-":
               result = arguments[0] - arguments[1]
                    
          case "*":
               result = arguments[0] * arguments[1] * arguments[2]
                         
          case "/":
               if arguments[1] == 0: 
                    result += "\tCannot divide by 0\n"
               elif not panic:
                    result = arguments[0] / arguments[1]
                    
          case "%":
               if arguments[1] == 0: 
                    result += "\tModulo of 0 is undefined\n"
               elif not panic:
                    result = arguments[0] % arguments[1]
                     
     return result

def threaded_client(connection_socket, addr):
     try:
          request = connection_socket.recv(512).decode("UTF-8")
     except:
          print("Failed to connect with client")
          return
     
     result = "In \"" + request + "\":\n"
     # panic mode == Αν βρεθεί λάθος, ο server θα κάνει όλα τα checks κανονικά αλλά όχι τελικούς υπολογισμούς 
     # ώστε να δώσει στον χρήστη όσο περισσότερα λάθη που μπορεί να έχει κάνει στο request με το response
     panic = False
     
     # Αν δεχθεί άδειο request, ο server crashάρει
     if len(request) > 0:
          valid, function, arguments, invalid_arguemnts, error_message = parse(request)
          num_arguments = len(arguments) + len(invalid_arguemnts)
          if not valid:
               panic = True
               result += "\t" + error_message + "\n"
          
          valid, error_message = validate_args(function, arguments, num_arguments)
          if not valid:
               panic = True
               result += "\t" + error_message + "\n"
               
          if not panic:
               result = calculate(request, function, arguments, panic)
          
          # Εμφανίζει το request και αποτέλεσμα στο τέλος
          print(request + " : " + str(result))
          try:
               connection_socket.send(str(result).encode("UTF-8"))
               connection_socket.close()
          except:
               print("Failed to send response to client")
     else:
          print("Received empty request")


server_socket = start_server()

while True:
     # Ο server είναι σε αναμονή μέχει να λάβει σύνδεση και δεδομένα
     try:
          connection_socket, addr = server_socket.accept()
          _thread.start_new_thread(threaded_client, (connection_socket, addr))
          # Αν η σύνδεση αποτύχει, το αγνοεί και μπαίνει ξανά σε αναμονή
     except:
          print("Failed to connect with client")
          continue
     
