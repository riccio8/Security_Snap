import os
import platform
import pefile as pe
import peutils as pes
import time
from scapy.all import sniff
import psutil
import argparse

parser = argparse.ArgumentParser(description='Process analysis tool.')
parser.add_argument('--logfile', help='Optional. Save output to a log file. Usage: python proc_analysis.py --logfile=log.txt', default=None)
args = parser.parse_args()


if platform.system() == 'Linux':
    os.system("clear")
else:
    os.system("cls")


def log(message):
    print(message)
    try:
        if args.logfile:
            with open(args.logfile, 'a') as logfile:
                logfile.write(message + '\n')
    except Exception as e:
        print("[ERROR]Error occurred: \n", e)


def insecure_net():
    for conn in psutil.net_connections(kind='inet'):
        if conn.laddr.port == 21 or conn.laddr.port == 23 or conn.laddr.port == 24:
            print(f"[INFO]Process {conn.pid} is using an insecure port: {conn.laddr.port}")
        elif conn.laddr.port == 80:
            print(f"[INFO]Process {conn.pid} is using HTTP on port 80")
    
    # log("[X]Analyzing http connection... \n")
    # time.sleep(1)
    # log(f"[INFO]Connection: \t {psutil.net_connections(kind='all')}")




proc_name = input("[X] Name of the process...: \n")

def get_process_path(pid):
    try:
        process = psutil.Process(pid)
        return process.exe()  
    except psutil.NoSuchProcess:
        return f"[ERROR] Process with PID {pid} not found."
    except psutil.AccessDenied:
        return "[ERROR] AccessDenied to the process."
    except Exception as e:
        return str(e)

def main():  
    log(f"[WANRING] Current user: {psutil.users()} \n")
    found_process = False
    try: 
        for processes in psutil.process_iter():
            if processes.name() == proc_name:
                found_process = True
                log(f"[INFO]: {processes}")
                process_pid = processes.pid
                kill = input("[*] Do you want to kill the process? (Y/N): \n")
                if kill.lower() == "y":
                    os.system("taskkill /pid " + str(processes.pid))
                    if platform.system() == 'Linux':
                        os.system("clear")
                    else:
                        os.system("cls")
                    os.abort()

                else:
                    if platform.system() == 'Linux':
                        os.system("clear")
                    else:
                        os.system("cls")
                    log(f"[X] Analysis of {proc_name}.")
                    log("[X] Analysis could take some time, please wait...")
                    time.sleep(2)
                    log("[X] Analysis in progress...")
                    log(f"[INFO]General infos: {psutil.cpu_times()} \n")

                    time.sleep(1)
                    log("-----------------------------------------------------------------------------------------------------------------------------------------------")
                    path1 = get_process_path(process_pid)

                    try:
                        path = pe.PE(path1, True)
                        suspicious = pes.is_suspicious(path)
                        if suspicious:
                            log(f"[INFO] {proc_name} is suspicious...")
                            log("[INFO] It could be that: import tables are in unusual locations, or section names are unrecognized, or there is a presence of long ASCII strings....")
                        else:
                            log("[INFO] File is not suspicious...\n")


                        time.sleep(2)

                        log("-----------------------------------------------------------------------------------------------------------------------------------------------")

                        time.sleep(1)
                        log("[X] Analyzing signature... \n")
                        time.sleep(1)
                        valid = pes.is_valid(path)
                        if valid == True:
                            log("[INFO] File's signature is not valid...\n")
                        else:
                            log("[INFO] File's signature is valid...\n")


                        log("-----------------------------------------------------------------------------------------------------------------------------------------------")

                        log("[X] Analyzing sections...\n")

                        for section in path.sections:
                            time.sleep(1)
                            log(f"[INFO] Section: {section.Name}, Virtual Address: {hex(section.VirtualAddress)}, Virtual Size: {hex(section.Misc_VirtualSize)}, Size of Raw Data: {section.SizeOfRawData}")

                        log("-----------------------------------------------------------------------------------------------------------------------------------------------")

                        log("[INFO] Analysis of the libraries... \n")
                        time.sleep(1)

                        path.parse_data_directories()
                        for entry in path.DIRECTORY_ENTRY_IMPORT:
                            log(f"[INFO] Libraries loaded: {entry.dll}")
                            for imp in entry.imports:
                                log(f"\t {hex(imp.address)} {imp.name}")

                        log("-----------------------------------------------------------------------------------------------------------------------------------------------")

                        log("[X] Analyzing the file format... \n")

                        time.sleep(2)    

                        strip = pes.is_probably_packed(path)
                        if strip:   
                            log("[INFO] File is probably packed or contains compressed data... \n")
                        else:
                            log("[INFO] File isn't compressed or packed... \n")
                        
                        log("----------------------------------------------------------------------------------------------------------------------------------------------- ")
                        
                        insecure_net()

                        log("-----------------------------------------------------------------------------------------------------------------------------------------------")

                        pobj = psutil.Process(process_pid)
                        conn_list = pobj.net_connections(kind='all')

                        if conn_list != None:
                                for conn in conn_list:
                                    log(f"[INFO] Connections:\t{conn} \n")
                        else:
                            log("[INFO] No Connections for this process...\n")

                        log("-----------------------------------------------------------------------------------------------------------------------------------------------")

                        time.sleep(1)

                        log("[X] Analyzing thread...\n")

                        time.sleep(1)

                        log(f"[INFO] Thread analysis: \t {pobj.threads()}...\n")

                        log("-----------------------------------------------------------------------------------------------------------------------------------------------")

                        log("[X] Saving the PE dump file... \n")

                        with open(proc_name + "_dump.txt", 'w') as dump:
                            dump.write(path.dump_info())
                            dump.close()
                        
                        test = input("[TEST] Do u want more info? \n")
                        if test.lower() == "y":
                            psutil.test()

                            winservice = list(psutil.win_service_iter()) 
                            for service in winservice:
                                log(f"[INFO] Win service running: {service} \n")
                            os.abort()

                        else:
                            os.abort()

                    except Exception as e:
                        log("[ERROR] " + str(e))

        if not found_process:
            log(f"[INFO] No processes found with the name {proc_name}.")
    except Exception as e:
        log("[ERROR] " + str(e))
   
if __name__ == "__main__":
    main()