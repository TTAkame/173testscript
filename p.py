import subprocess
import time
import os
import signal

def run_server(script_name, log_file):
    """Start a server script in the background and return its process."""
    return subprocess.Popen(['python', '-u', script_name], stdout=open(log_file, 'w'), stderr=subprocess.STDOUT)

def run_curl(url):
    """Run a curl command and print its output."""
    result = subprocess.run(['curl', url], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Error:", result.stderr)

def kill_process(proc):
    """Kill a given process."""
    os.kill(proc.pid, signal.SIGKILL)

def main():
    # Start the web server
    print("Starting web server...")
    web_server_proc = run_server('web_server.py', 'server.log')

    # Start the proxy server
    #print("Starting proxy server...")
    #proxy_server_proc = run_server('proxy_server.py', 'proxy.log')

    # Wait for servers to start up
    time.sleep(5)  # Adjust this based on how quickly your servers start

    # Run curl to fetch a resource directly from the web server
    print("Fetching resource directly from web server...")
    run_curl('http://localhost:6789/helloworld.html')

    # Run curl to fetch a resource through the proxy server
    #print("Fetching resource through proxy server...")
    #run_curl('http://localhost:8888/localhost:6789/helloworld.html')

    # Kill the servers
    print("Killing the servers...")
    kill_process(web_server_proc)
    #kill_process(proxy_server_proc)
    print("Servers stopped.")

if __name__ == "__main__":
    main()

