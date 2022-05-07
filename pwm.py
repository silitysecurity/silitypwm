from termcolor import colored
import os
from os import stat, system, name
import pathlib
from getpass4 import getpass
from hashlib import sha256
import json
import pyAesCrypt
import pyperclip

current_directory = pathlib.Path(__file__).parent.resolve()
data_directory = os.path.join(current_directory, r"data")
master_password_file_path = data_directory+"/master.json"
password_folder_path = data_directory+"/passwords"
bufferSize = 128 * 1024


def clear():
  
    # for windows
    if name == 'nt':
        _ = system('cls')
  
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')


def setup():
    clear()
    print(colored("Welcome to sility password manager.", "cyan"))
    os.makedirs(data_directory, exist_ok=True)
    print("To start using the password manager you'll have to create a master password which will be used to unlock your other passwords.\nWithout it you can't access your passwords anymore, so don't forget it!")
    print(colored("WARNING: never delete the data folder or any files inside or your can't access your passwords anymore!", "red"))
    print("")
    master_password = getpass("Enter your master password: ")
    verfiy_master_password = getpass("Verify your master password: ")
    if master_password == verfiy_master_password:
        hashed_master_password = sha256(
            master_password.encode("UTF-8")).hexdigest()
        data = {"master": {}}
        data["master"] = hashed_master_password
        with open(master_password_file_path, "w") as master_password_file:
            json.dump(data, master_password_file, indent=4)
        print(colored(
            "sility password manager is now setup! Please restart the program to start using it.", "green"))

    else:
        print("Your passwords do not match. Please start the set up again.")


def login():
    clear()
    print(colored("Welcome to sility password manager.", "cyan"))
    with open(master_password_file_path, "r") as master_password_file:
        global master_password
        data = json.load(master_password_file)
        stored_master_password = data["master"]
        master_password = getpass("Please enter your master password: ")
        if sha256(master_password.encode("UTF-8")).hexdigest() == stored_master_password:
            clear()
            print(colored("Access granted.", "green"))
            menu()
        else:
            print(colored("Wrong password.", "red"))


def menu():
    print("Menu:\n1 - Add password\n2 - Remove password\n3 - Access a password\n4 - Exit\n")
    option = int(input(colored("Choose an option: ", "green")))

    if option == 1:
        addPassword()
    elif option == 2:
        removePassword()
    elif option == 3:
        accessPassword()
    elif option == 4:
        exit()
    else:
        clear()
        print("Invalid option.")
        menu()


def addPassword():
    clear()
    names = os.listdir(password_folder_path)
    names = [x.split('.')[0] for x in names]
    name = input(colored("Under what name should the password be saved?: ", "green"))

    if name not in names:
        password = getpass("Please enter the password: ")
        password_confirm = getpass("Please enter the password again: ")

        if name not in names:
            if password == password_confirm:
                if password != "":
                    data = {"password": {}}
                    data["password"] = password
                    temporary_path = password_folder_path + \
                        str("/{}_temp.json").format(name)
                    password_file_path = password_folder_path + \
                        str("/{}.json").format(name)
                    with open(temporary_path, "w") as password_file:
                        json.dump(data, password_file, indent=4)
                    pyAesCrypt.encryptFile(
                        temporary_path, password_file_path, master_password)
                    os.remove(temporary_path)
                    clear()
                    print(colored("Password added.", "green"))
                    menu()
                else:
                    clear()
                    print(colored("Password can't be empty! Try again.", "red"))
                    menu()
            else:
                clear()
                print(colored("Passwords didn't match. Try again.", "red"))
                menu()
    else: 
        clear()
        print(colored("A password with that name already exists", "red"))
        menu()


def removePassword():
    names = os.listdir(password_folder_path)
    names = [x.split('.')[0] for x in names]
    clear()
    print("Saved passwords:")
    for name in names:
        print(name)
    print("")
    which_password = input(
        colored("Which password do you want to remove?: ", "red"))
    if which_password in names:
        path = password_folder_path + \
            str("/{}.json").format(which_password)
        os.remove(path)
        clear()
        print(colored("Password removed.", "green"))
        menu()
    else:
        clear()
        print(colored("That password doesn't exist.", "red"))
        menu()


def accessPassword():
    names = os.listdir(password_folder_path)
    names = [x.split('.')[0] for x in names]
    clear()
    print("Saved passwords:")
    for name in names:
        print(name)
    print("")
    which_password = input(
        colored("Which password do you want to access? :", "green"))
    print(which_password)
    if which_password in names:
        password_file_path = password_folder_path + \
            str("/{}.json").format(which_password)
        temporary_path = password_folder_path + \
            str("/{}_temp.json").format(which_password)
        pyAesCrypt.decryptFile(
            password_file_path, temporary_path, master_password)
        with open(temporary_path, "r") as decrypted_file:
            data = json.load(decrypted_file)
            password = data["password"]
            pyperclip.copy(password)
        os.remove(temporary_path)
        clear()
        print(colored("The password was copied to your clipboard.", "green"))
        menu()

    else:
        clear()
        print(colored("That password doesn't exist.", "red"))
        menu()


if __name__ == "__main__":
    if os.path.isfile(master_password_file_path):
        login()
    else:
        setup()
