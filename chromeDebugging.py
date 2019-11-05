import argparse
import os
import platform
import re
import sys
import time
import subprocess
from datetime import datetime
import logging
import logging.handlers


LOG_FILENAME = datetime.now().strftime('coldboot_logfile_%H_%M_%d_%m_%Y.log')
LOG_FILENAME_STR = os.path.abspath(LOG_FILENAME)
# print ("Log file name is: %s"% LOG_FILENAME)
logging.basicConfig(filename=LOG_FILENAME, stream=sys.stdout, level=logging.DEBUG, )

#CONFIG PARAMETERS FOR USER TO CHANGE
cros_sdk_path = '/home/cssdesk/google_source'
abs_cros_sdk_path = '/home/cssdesk/depot_tools/cros_sdk --no-ns-pid'
shutdown_wait_time = 16
reboot_wait_time = 1500
#END CONFIG PARAMETERS FOR USER TO CHANGE

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

def run_reboot(dut_ip, username="root", password="test0000", reboot_wait_time=60, wait_device_initialization=20):
    
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
                    print ("Waiting for device initialization after test in seconds: ", wait_device_initialization)
                    time.sleep(wait_device_initialization)
                    return True
            print ("system didn't reboot back on after %d seconds wait delay" % (reboot_wait_time))
            return False
    else:
        print ("DUT is not live")
        return False

def rtc_cold_reboot(dut_ip, username="root", password="test0000", shutdown_wait_time=10, reboot_wait_time=80, wait_device_initialization=20):
    
    if check_if_remote_system_is_live(dut_ip):
	sshpassCmd1 = "sshpass -p " + password + " ssh -o StrictHostKeyChecking=no " + username + "@" + dut_ip + " 'echo +8 > /sys/class/rtc/rtc0/wakealarm'"
        print (sshpassCmd1)
        p = subprocess.Popen(sshpassCmd1, stdout=subprocess.PIPE, shell=True)

        sshpassCmd2 = "sshpass -p " + password + " ssh -o StrictHostKeyChecking=no " + username + "@" + dut_ip + " 'shutdown -h now'"
        print (sshpassCmd2)
        p = subprocess.Popen(sshpassCmd2, stdout=subprocess.PIPE, shell=True)
        time.sleep(shutdown_wait_time)
        if not check_if_remote_system_is_live(dut_ip):
            print ("System shutdown successfull.")
            for i in range(reboot_wait_time):
                time.sleep(1)
                if check_if_remote_system_is_live(dut_ip):
                    print ("Waiting for device initialization after test in seconds: ", wait_device_initialization)
                    time.sleep(wait_device_initialization)
                    return True
        else:
            print ("system didn't shutdown after %d seconds wait delay" % (shutdown_wait_time))
            return False
    else:
        print ("DUT is not live")
        return False

def ec_cold_reboot(dut_ip, username="root", password="test0000", shutdown_wait_time=10, reboot_wait_time=60, wait_device_initialization=10):
    
    if check_if_remote_system_is_live(dut_ip):
        sshpassCmd1 = "sshpass -p " + password + " ssh -o StrictHostKeyChecking=no " + username + "@" + dut_ip + " 'ectool reboot_ec cold at-shutdown'"
        print (sshpassCmd1)
        p = subprocess.Popen(sshpassCmd1, stdout=subprocess.PIPE, shell=True)
        sshpassCmd2 = "sshpass -p " + password + " ssh -o StrictHostKeyChecking=no " + username + "@" + dut_ip + " 'shutdown -P now'"
        print (sshpassCmd2)
        p = subprocess.Popen(sshpassCmd2, stdout=subprocess.PIPE, shell=True)
        time.sleep(shutdown_wait_time)
        if not check_if_remote_system_is_live(dut_ip):
            print ("System shutdown successfull.")
            for i in range(reboot_wait_time):
                time.sleep(1)
                if check_if_remote_system_is_live(dut_ip):
                    print ("Waiting for device initialization after test in seconds: ", wait_device_initialization)
                    time.sleep(wait_device_initialization)
                    return True
        else:
            print ("system didn't shutdown after %d seconds wait delay" % (shutdown_wait_time))
            return False
    else:
        print ("DUT is not live")
        return False


def run_suspend(dut_ip, username="root", password="test0000"):
    if check_if_remote_system_is_live(dut_ip):
        suspendCmd = 'suspend_stress_test -c 1'
        suspend_output = run_command(suspendCmd, dut_ip )
        if suspend_output:
            if searchPatternMatched(suspend_output, pattern_list=["suspend_failures: 0", "firmware log errors: 0"]):
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

def servod_process(cros_sdk_path, abs_cros_sdk_path):
    import subprocess    
    script_working_directory = os.getcwd()
    # os.system("pgrep servod | xargs sudo kill -9")
    p = subprocess.Popen('pgrep servod', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    retval = p.wait()
    out, err = p.communicate()

    if out:
        servod_pid = int(out.strip())
        print('servod Process found.')
        logging.info('servod Process found.')	
        return True

    print('starting a fresh servod...')
    logging.info('starting a fresh servod...')

    os.chdir(cros_sdk_path)	
    print (os.getcwd())
    logging.info (os.getcwd())
    

    servod_cmd = 'python ' + abs_cros_sdk_path + ' ' + 'sudo ' + 'servod ' + '--board=cyan ' + '&'
    os.system(servod_cmd)
    time.sleep(15)
    
    
    output = subprocess.Popen(['pgrep', 'servod'], stdout=subprocess.PIPE).communicate()[0]

    if output:
        print "Servod started successfully"
        logging.info("Servod started successfully")
        return True
    else:
        print "Servod couldn't be started successfully. Exiting test."
        logging.info("Servod couldn't be started successfully. Exiting test.")
        return False
    

def servo_coldboot(dut_ip, username="root", password="test0000"):
    pwr_btn_command = 'python' + ' ' + abs_cros_sdk_path + ' ' + 'dut-control pwr_button:press sleep:0.5 pwr_button:release'
    print ("Sending shutdown command to the DUT")
    logging.info ("Sending shutdown command to the DUT")
    sshpassCmd = "sshpass -p " + password + " ssh -o StrictHostKeyChecking=no " + username + "@" + dut_ip + " 'shutdown -P now'"
    print (sshpassCmd)
    logging.info (sshpassCmd)
    p = subprocess.Popen(sshpassCmd, stdout=subprocess.PIPE, shell=True)
    time.sleep(shutdown_wait_time)
    if not check_if_remote_system_is_live(dut_ip):
        print ("System shutdown successfull.")
        logging.info ("System shutdown successfull.")
	
    os.chdir(cros_sdk_path)	
    print (os.getcwd())
    logging.info (os.getcwd())
    
    ec_uart_capture_enable_command = 'python' + ' ' + abs_cros_sdk_path + ' ' + 'dut-control ec_uart_capture:on'
    ec_uart_capture_disable_command = 'python' + ' ' + abs_cros_sdk_path + ' ' + 'dut-control ec_uart_capture:off'
    ec_console_system_status_command = 'python' + ' ' + abs_cros_sdk_path + ' ' + 'dut-control ec_uart_cmd:powerinfo'
    ec_console_system_status_output = 'python' + ' ' + abs_cros_sdk_path + ' ' + 'dut-control ec_uart_stream'
    os.system(ec_uart_capture_enable_command)
    os.system(ec_console_system_status_command)
    system_status_check = os.popen(ec_console_system_status_output).read()
    os.system(ec_uart_capture_disable_command)
    print (system_status_check)
    logging.info (system_status_check)
    
    if system_status_check.find("G3") != -1:
        print ("System successfully went to G3")
        logging.info ("System successfully went to G3")
    else:
        print ("System is not going to G3. Exiting test")
        logging.info ("System is not going to G3. Exiting test")
        return False
		
    print ("Pressing powerbtn to poweron system")
    logging.info ("Pressing powerbtn to poweron system")
    for i in range(3):
        os.system(pwr_btn_command)
        print ("Waiting 25 minutes for the system to come up.")
        logging.info ("Waiting 25 minutes for the system to come up.")
        for i in range(reboot_wait_time):
            time.sleep(1)
            if check_if_remote_system_is_live(dut_ip):
                print ("Waiting for device initialization after test in seconds: 10")
                logging.info ("Waiting for device initialization after test in seconds: 10")
                time.sleep(10)
                return True
    else:
        print ("Powerbtn wake didnt work even after 3 attempts. Exiting Test")
        logging.info ("Powerbtn wake didnt work even after 3 attempts. Exiting Test")
        return False
  




if __name__ == "__main__":

    if not is_tool("sshpass"):
        print ("sshpass is not installed. Please install sshpass with sudo apt-get install")
        logging.info ("Exiting test!")
        logging.info ("sshpass is not installed. Please install sshpass with sudo apt-get install")
        logging.info ("Exiting test!")
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument('--testcase', dest='testcase_to_run', default = "", help='testcase to run is before reboot or suspend test')
    parser.add_argument('--test', dest='test_to_run', default = "reboot", help='test to run is either "reboot" or "suspend" or "rtc_coldboot" or "ec_coldboot" or servo_coldboot')
    parser.add_argument('--ip', dest='ip_address', help='provide remote system ip')
    parser.add_argument('--after_test_delay', dest='wait_device_initialization', default = 10, help='Provide Device initialization delay in seconds after test!')
    parser.add_argument('--count', dest='iteration_count', default = 5, help='Provide iteration count!')
    parser.add_argument('--command', dest='cmd_to_run', default = "dmesg --level=err", help='Please mention the command to check in double quotes!')
    parser.add_argument('--search_for', dest='search_patterns', help='provide one or many search strings with space. If found, test will FAIL/STOP.', nargs='+')
    args = parser.parse_args()

    pattern_list = args.search_patterns

    testcase = args.testcase_to_run.lower()
    cmd_to_run = args.cmd_to_run
    
    if args.ip_address:
        ip_address = args.ip_address
    else:
        ip_address = False
        print ("check with --help or give cmd argument --IP <ip_address>")
        logging.info ("check with --help or give cmd argument --IP <ip_address>")
        sys.exit(1)
        
    
    
    wait_device_initialization = float(args.wait_device_initialization)
    iteration_count = args.iteration_count
    test_to_run = args.test_to_run
    
    if test_to_run == "servo_coldboot":
        if servod_process(cros_sdk_path, abs_cros_sdk_path):
            print ("Servod PASS. Will continue test.")
            logging.info ("Servod PASS. Will continue test.")
           
        else:
            print ("Servod not running.")
            print ("Unable to start servod. Exiting test.")
            logging.info ("Servod not running.")
            logging.info ("Unable to start servod. Exiting test.")
            sys.exit()

    print ("Testcase selected to run                                 :", testcase)
    print ("Test selected to run                                     :", test_to_run)
    print ("system ip address is                                     :", ip_address)
    print ("after_test_delay for device initialization in seconds    :", wait_device_initialization)
    print ("Iteration_count is                                       :", iteration_count)
    print ("cmd to run after selected test                           :", cmd_to_run)
    print ("stop test if pattern matches                             :", pattern_list)
    if test_to_run == "servo_coldboot":
        print ("cros_sdk_path is                                         :", cros_sdk_path)
        print ("abs_cros_sdk_path is                                     :", abs_cros_sdk_path)
        
    print ("**********************************************************")
    
        
    if (sys.version_info > (3, 0)):
        input("Press Enter to continue...")
    else:
        raw_input("Press Enter to continue...")
    
        
    count = 1
    
    while (count < int(iteration_count)):
        print ("******************************")
        print ("******************************")
        logging.info ("******************************")
        logging.info ("******************************")
        print ("STARTING ITERATION %d of %d" % (count, int(iteration_count)))
        logging.info ("STARTING ITERATION %d of %d" % (count, int(iteration_count)))
        print ("******************************")
        print ("******************************")
        logging.info ("******************************")
        logging.info ("******************************")

        if testcase:
            testcase_output = run_command(testcase, ip_address, username="root", password="test0000")
            print (testcase_output)
            logging.info (testcase_output)
            time.sleep(5)

        if test_to_run == "suspend":
            print (run_suspend(ip_address))
        elif test_to_run == "rtc_coldboot":
            print (rtc_cold_reboot(ip_address, wait_device_initialization=wait_device_initialization ))
        elif test_to_run == "ec_coldboot":
            print (ec_cold_reboot(ip_address, wait_device_initialization=wait_device_initialization ))
        elif test_to_run == "servo_coldboot":
            print (servo_coldboot(ip_address))
        else:
            print (run_reboot(ip_address, wait_device_initialization=wait_device_initialization))    
        
        count = count + 1
        cmd_output = run_command(cmd_to_run, ip_address, username="root", password="test0000")
        print (cmd_output)
        logging.info (cmd_output)
        if cmd_output:       
            if searchPatternMatched(cmd_output, pattern_list):
                break
            else:
                print ("cmd %s successfull!"%(cmd_to_run))
                logging.info ("cmd %s successfull!"%(cmd_to_run))
        else:
            print ("please check the command you are trying!")
            logging.info ("please check the command you are trying!")
            break
    print ("******************************")
    print ("******************************")
    logging.info ("******************************")
    logging.info ("******************************")
    print ("Completed ITERATION %d of %d" % (count, int(iteration_count))) 
    logging.info ("Completed ITERATION %d of %d" % (count, int(iteration_count)))        
    print ("******************************")
    print ("******************************")
    logging.info ("******************************")
    logging.info ("******************************")

            
