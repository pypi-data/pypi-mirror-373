import os
import sys


def setup():
    home_directory = os.path.expanduser("~")
    mridumanda_directory = ".mridumanda"
    
    if os.path.isdir(os.path.join(home_directory, mridumanda_directory)) and os.path.isfile(os.path.join(home_directory, mridumanda_directory, "api.txt")):
        exit
    else:
        os.system("mkdir -p $HOME/.mridumanda")
        api_key = input("Enter your api key: ")
        
        with open(os.path.join(home_directory, mridumanda_directory, "api.txt"), "w") as file:
            file.write(f"api_key:{api_key}\n")
        
        print("API key saved successfully")
        print("Rerun the program again to enjoy the service.")
        sys.exit(0)