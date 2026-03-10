import os
import hashlib

USER_FILE = "username.data"

module_dir = os.path.dirname(os.path.abspath(__file__))
uf_path = os.path.abspath(module_dir + "/" + USER_FILE)

def myFunction(number):
    sum = 2+2
    return sum == number

def hash_password(password, salt):
    return hashlib.sha256(salt + password.encode()).hexdigest()

def username_exists(username):
    global USER_FILE

    if not os.path.exists(uf_path):
        print(f"{uf_path} does not exist. Please create the file and add usernames.")
        return False

    with open(uf_path, "r") as f:
        users = [line.strip() for line in f.readlines()]

    return username in users

def username_index(username):
    global USER_FILE
    
    with open(uf_path, "r") as f:
        users = [line.strip() for line in f.readlines()]
        return users.index(username)