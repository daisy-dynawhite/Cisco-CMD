#!/usr/bin/env python3

# Import libraries
import warnings
warnings.filterwarnings(action='ignore', module='.*paramiko.*')

from netmiko import ConnectHandler
import getpass, yaml, time, logging, sys

# Function to setup global / YAML variables
def setup_vars():

	# Create global VARS
	global admin
	global adminpword
	global config_data

	# Print banner
	print("\n*** HSRP VIP Migration Script ***\n\nPlease enter credentials!\n")

	# Setup logging
	logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%d %b %y - %H:%M:%S')

	# Capture credentials
	admin = getpass.getpass('Admin Username: ')
	adminpword = getpass.getpass(prompt='\nAdmin Password: ')

	# Load script variables via YAML
	try:
		with open('cisco.yaml', 'r') as vars:
			config_data = yaml.safe_load(vars)
			return True

	except Exception as e:
		logging.info(f"Error importing YAML vars: {e}")
		return False

# Setup Netmiko constructs
def setup_connections(config_data, admin, adminpword):

	# Import devices list of dictionaries
	devicevars = config_data.get('devices',[])[0]

	devices = {
		'nc_rtr1': {'host': devicevars['xe1'], 'device_type': 'cisco_xe'},
		'nc_rtr2': {'host': devicevars['xe2'], 'device_type': 'cisco_xe'},
		'nc_rtr3': {'host': devicevars['xr1'], 'device_type': 'cisco_xr'},
		'nc_rtr4': {'host': devicevars['xr2'], 'device_type': 'cisco_xr'},
	}

	connections = {}

	try:
		for name, device_info in devices.items():
			connections[name] = ConnectHandler(
			device_type=device_info['device_type'],
			host=device_info['host'],
			username=admin,
			password=adminpword
			)

	except Exception as e:
		logging.info(f"Error connecting to devices: {e}")
		sys.exit(100)

	time.sleep(0.5)
	return connections

# Function to migrate L3 VIPs
def process_rtrs(config_data, connections):
	try:
		#Iterate through YAML vars and execute
		hsrp = config_data.get('hsrp',[])

		for vars in hsrp:
			physip1 = vars['physip1']
			physip2 = vars['physip2']
			vip = vars['vip']
			mask = vars['mask']
			vrf = vars['vrf']
			actpri = vars['actpri']
			sbypri = vars['sbypri']
			podel = vars['podel']
			poadd = vars['poadd']
			group = vars['group']
			encap = vars['encap']

		delvip = (f"no int po{podel}.{encap}")

		addvip1 = [
		f"int po{poadd}.5",
		"encapsulation dot1q 5",
		f"vrf forwarding {vrf}",
		f"ip address {physip1} {mask}",
		"standby version 2",
		f"standby {group} ip {vip}",
		"standby {group} timers msec 600 2",
		f"standby {group} priority {actpri}",
		"standby {group} preempt delay minimum 40 reload 60",
		"no shut",
		]

		addvip2 = [
		f"int po{poadd}.5",
		"encapsulation dot1q 5",
		f"vrf forwarding {vrf}",
		f"ip address {physip2} {mask}",
		"standby version 2",
		f"standby {group} ip {vip}",
		"standby {group} timers msec 600 2",
		f"standby {group} priority {sbypri}",
		"standby {group} preempt delay minimum 40 reload 60",
		"no shut",
		]

		checkhsrp = "do show standby brief"

		connections['nc_rtr1'].send_config_set(delvip)
		print (f"Po{podel}.{encap} deleted from router 1")
		file.write(f"Po{podel}.{encap} deleted from XE router 1 \n\n")
		connections['nc_rtr2'].send_config_set(delvip)
		print (f"Po{podel}.{encap} deleted from router 2")
		file.write(f"Po{podel}.{encap} deleted from XE router 2 \n\n")
		connections['nc_rtr1'].send_config_set(addvip1)
		print (f"Po{poadd}.{encap} created on router 1")
		file.write(f"Po{poadd}.{encap} created on router 1 \n\n")
		connections['nc_rtr2'].send_config_set(addvip2)
		print (f"Po{poadd}.{encap} created on router 2 \n\n")
		file.write(f"Po{poadd}.{encap} created on router 2 \n")
		print ("Script sleeping 20s whilst HSRP converges \n")
		time.sleep(20.0)
		hsrp1 = connections['nc_rtr1'].send_config_set(checkhsrp)
		hsrp2 = connections['nc_rtr2'].send_config_set(checkhsrp)
		file.write(f"HSRP on router 1 \n\n{hsrp1}")
		file.write(f"\n\n HSRP on router 2 \n\n{hsrp2}")

	except Exception as e:
		logging.info(f"Error creating route: {e}")
		sys.exit(200)

# Main process function
def main():

	print("\nScript output: \n")

	# Load PVT TXT file
	global file
	file = open('L3-Migration-PVT.txt','w')
	file.write('\n*** L3 Migration PVT Script *** \n\n')

	# Connect to devices via function
	logging.info("Device connections:\n")
	connections = setup_connections(config_data, admin, adminpword)
	logging.info("Netmiko connections established\n")
	input("All connections are established, hit enter to continue, CTRL-Z to exit")
	print("\n")

	# Start duration timer
	start_time = time.perf_counter()

	# Process routing
	process_rtrs(config_data, connections)

	#Process script duration
	end_time = time.perf_counter()
	timediff = end_time - start_time
	print(f"Time elapsed: {timediff:.2f} seconds.")

	# Close PVT
	file.close()

# Call main function
if __name__ == "__main__":
	if setup_vars():
		main()
		print("\nScript completed\n")
	else:
		print("Main script not started, issue with vars")
