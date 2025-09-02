#################################
# Launch vis.exe
#################################
import http.client
import subprocess
import os
import psutil  # Make sure to import psutil

# Set the path to vis.exe in the current directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))
vis_exe_path = os.path.join(current_directory, "vis", "vis.exe")
print(vis_exe_path)
# Check if vis.exe is running
def is_vis_running():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'vis.exe':
            return True
    return False
    
# Send network message
def HTTPPOST(ip, phg):
    headers = {
        "Connection": "keep-alive",
        "Content-Type": "text/plain"
    }
    conn = http.client.HTTPConnection(f"{ip}:5088")
    conn.request('POST', '/phg', phg, headers)
    res = conn.getresponse()
    conn.close()
    
# Call HTTPPOST function to send network message
def vis(phg):
    if not is_vis_running():  # Check if the process is running
        subprocess.Popen(vis_exe_path)  # Start the process
    return HTTPPOST('127.0.0.1', phg.encode())    