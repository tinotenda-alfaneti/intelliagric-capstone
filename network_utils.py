import subprocess

def connect_to_wifi(ssid, password):
    try:

        command = ['netsh', 'wlan', 'connect', 'name=', ssid]
        password_bytes = password.encode('utf-8')
        subprocess.run(command, input=password_bytes, check=True, shell=True)
        return True
    
    except subprocess.CalledProcessError as e:

        print(f"Error connecting to WiFi: {e}")

        return False

def is_connected_to_internet():
    try:

        ping_process = subprocess.Popen(["ping", "google.com"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = ping_process.communicate()

        return ping_process.returncode == 0
    
    except Exception as e:
        
        print(f"Error checking internet connectivity: {e}")

        return False


