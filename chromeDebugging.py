import argparse
import os
import platform
import re
import sys
import time
import subprocess

def check_if_remote_system_is_live(ip):
    hostname = ip
    print ("hostname is", hostname)
    try:
        response = os.system("ping -c 1 " + hostname)
    except:
        return False

    if response == 0:
        return True
    else:
        return False

def run_command(command, dut_ip, username="root", password="test0000"):
    
    if check_if_remote_system_is_live(dut_ip):
        sshpassCmd = "sshpass -p " + password + " ssh " + username + "@" + dut_ip + " '" + command +  "'"
        print (sshpassCmd)
        p = subprocess.Popen(sshpassCmd, stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        
        ## Wait for command to terminate. Get return returncode ##
        p_status = p.wait()
        # print ("Command output : ", output)
        # print ("Command exit status/return code : ", p_status)
        if p_status != 0:
            return False
        else:
            return output.decode('ascii')

def run_reboot(dut_ip, username="root", password="test0000", reboot_wait_time=60):
    
    if check_if_remote_system_is_live(dut_ip):
        sshpassCmd = "sshpass -p " + password + " ssh -o StrictHostKeyChecking=no " + username + "@" + dut_ip + " 'reboot'"
        print (sshpassCmd)
        p = subprocess.Popen(sshpassCmd, stdout=subprocess.PIPE, shell=True)
        time.sleep(3)
        if check_if_remote_system_is_live(dut_ip):
            print ("System reboot didn't happen.")
            return False
        else:
            for i in range(reboot_wait_time):
                time.sleep(1)
                if check_if_remote_system_is_live(dut_ip):
                    time.sleep(10)
                    return True
            print ("system didn't reboot back on after %d seconds wait delay" % (reboot_wait_time))
            return False
    else:
        print ("DUT is not live")
        return False

def run_suspend(dut_ip, username="root", password="test0000"):
    if check_if_remote_system_is_live(dut_ip):
        suspendCmd = 'suspend_stress_test -c 1'
        suspend_output = run_command(suspendCmd, dut_ip )
        if suspend_output:
            if searchPatternMatched(suspend_output, pattern_list=["syuspend_failures: 0", "firmware log errors: 0"]):
                return True 
            else:
                print ("No suspend failures observed!")
                return False   
        else:
            return False    

def searchPatternMatched(searchInString, pattern_list=None):
    if not pattern_list:
        return False
    
    matched = []
    for search_item in pattern_list:
        if re.search(search_item, searchInString, re.IGNORECASE):
            print ("MATCHED ON [%s]" % (search_item))
            matched.append(search_item)
    if len(matched) >= 1:
        return matched
    else:
        return False

def is_tool(name):
    """Check whether `name` is on PATH."""

    from distutils.spawn import find_executable

    return find_executable(name) is not None


if __name__ == "__main__":

    if not is_tool("sshpass"):
	print ("sshpass is not installed. Please install sshpass with sudo apt-get install")
	print ("Exiting test!")
	exit(1)	
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', dest='test_to_run', default = "reboot", help='test to run is either "reboot" or "suspend"')
    parser.add_argument('--IP', dest='ip_address', help='provide remote system ip')
    parser.add_argument('--COUNT', dest='iteration_count', default = 5, help='Provide iteration count!')
    parser.add_argument('--command', dest='cmd_to_run', default = "dmesg --level=err", help='Please mention the command to check in double quotes!')
    parser.add_argument('--search_for', dest='search_patterns', help='provide one or many search strings with space. If found, test will FAIL/STOP.', nargs='+')
    args = parser.parse_args()

    pattern_list = args.search_patterns
    cmd_to_run = args.cmd_to_run
    if args.ip_address:
        ip_address = args.ip_address
    else:
        ip_address = False
        print ("check with --help or give cmd argument --IP <ip_address>")
        sys.exit(1)
    iteration_count = args.iteration_count
    test_to_run = args.test_to_run
    print ("Test selected to run          :", test_to_run)
    print ("system ip address is          :", ip_address)
    print ("Iteration_count is            :", iteration_count)
    print ("cmd to run                    :", cmd_to_run)
    print ("stop test if pattern matches  :", pattern_list)
    print ("****************************")
    if (sys.version_info > (3, 0)):
	input("Press Enter to continue...")
    else:
	raw_input("Press Enter to continue...")
    count = 0
    while (count < int(iteration_count)):
        print ("******************************")
        print ("current count is: %d"%(count))
        print ("******************************")
        if test_to_run == "suspend":
            print (run_suspend(ip_address))
        else:
            print (run_reboot(ip_address))    
        count = count + 1
        cmd_output = run_command(cmd_to_run, ip_address, username="root", password="test0000")
        print (cmd_output)
        if cmd_output:       
            if searchPatternMatched(cmd_output, pattern_list):
                break
            else:
                print ("cmd %s successfull!"%(cmd_to_run))
        else:
            print ("please check the command you are trying!")
            break


    

            
