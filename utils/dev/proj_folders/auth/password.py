import os
from .authname import username as u

def passcode(): #use when authenticating a user in a terminal shell
    attempts = 8
    file_dir = os.path.dirname(__file__)
    auth_dir = os.path.join(file_dir, "authname")

    while attempts > 0:

        username = input("Username: ")

        if not u.username_exists(username):
            print("Invalid username. Please try again.")
            attempts -= 1
        
        else:
            password = input("Password: ")
            password_file = f"user{u.username_index(username)}_password.dat"
            password_file_path = os.path.join(auth_dir, password_file)

            if password == "setupnewuser":

                if os.path.exists(password_file_path):
                    print("Wrong password, please try again")
                    attempts -= 1
                    return False

                new_password = input("Create a password: ")
                salt = os.urandom(16)
                hashed = u.hash_password(new_password, salt)

                with open(password_file_path, "w") as f:
                    f.write(salt.hex() + ":" + hashed)

                print("Password setup complete. Please log in with your new password.")

            
            else:
                if not os.path.exists(password_file_path):
                    print("Password file does not exist. Please set up a new password.")
                    attempts -= 1
                    continue

                with open(password_file_path, "r") as f:
                    salt_hex, stored_hash = f.read().split(":")
                
                salt = bytes.fromhex(salt_hex)
                attempt_hash = u.hash_password(password, salt)

                if attempt_hash == stored_hash:
                    print("Access granted.")
                    return True
                else:
                    print("Wrong password, please try again")
                    attempts -= 1

    print("Too many failed attempts. Exiting....")
    return False

def authenticate(username, password):    #use when authenticating a user in a Program GUI (user puts username and password in the GUI)

    file_dir = os.path.dirname(__file__)
    auth_dir = os.path.join(file_dir, "authname")

    if not u.username_exists(username):
        message = "Invalid username. Please try again."
        print(message)
        attempts -= 1
        return False, message
    
    password_file = f"user{u.username_index(username)}_password.dat"
    password_file_path = os.path.join(auth_dir, password_file)

    if not os.path.exists(password_file_path):
        message = "Password file does not exist. Please set up a new password on terminal by running password.py"
        print(message)
        attempts -= 1
        return False, message
    
    if password == "setupnewuser":
        message = "Password setup not allowed in GUI apps. Please set up a new password on terminal by running password.py"
        print(message)
        attempts -= 1
        return False, message

    else:

        with open(password_file_path, "r") as f:
            salt_hex, stored_hash = f.read().split(":")
        
        salt = bytes.fromhex(salt_hex)
        attempt_hash = u.hash_password(password, salt)

        if attempt_hash == stored_hash:
            message = "Access granted."
            print(message)
            return True, message
        
        else:
            message = "Invalid password, please try again"
            print(message)
            attempts -= 1
            return False, message
        
if __name__ == "__main__":
    passcode()
