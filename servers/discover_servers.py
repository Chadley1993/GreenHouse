from directory_server import find_servers
import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        num_retries = int(sys.argv[1])
    if len(sys.argv) > 2:
        num_threads = int(sys.argv[2])
    if len(sys.argv) > 3:
        ip_limit = int(sys.argv[3])
    
    find_servers(num_retries=num_retries, num_threads=4, ip_limit=65)