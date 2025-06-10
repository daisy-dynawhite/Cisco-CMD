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
		hsrpvars = config_data.get('hsrpvars',[])

		for vars in hsrpvars:
			xephysip1 = vars['xephysip1']
			xephysip2 = vars['xephysip2']
			xrphysip1 = vars['xrphysip1']
			xrphysip2 = vars['xrphysip2']
			xevip = vars['xevip']
			xrvip = vars['xrvip']
			mask = vars['mask']
			vrf = vars['vrf']
			actpri = vars['actpri']
			sbypri = vars['sbypri']
			podel = vars['podel']
			poadd = vars['poadd']
			xegroup = vars['xegroup']
			xrgroup = vars['xrgroup']
			encap = vars['encap']

		delvipxe = (f"no int po{podel}.{encap}")
		delhsrp = (f"no router hsrp interface bundle-Ether {podel}.{encap}")
		delvipxr = (f"no int bundle-ether {podel}.{encap}") 

		addvip1xe = [
		f"int po{poadd}.{encap}",
		f"encapsulation dot1q {encap}",
		f"vrf forwarding {vrf}",
		f"ip address {xephysip1} {mask}",
		f"standby version 2",
		f"standby {xegroup} ip {xevip}",
		f"standby {xegroup} timers msec 600 2",
		f"standby {xegroup} priority {actpri}",
		f"standby {xegroup} preempt",
		"no shut",
		]

		addvip2xe = [
		f"int po{poadd}.{encap}",
		f"encapsulation dot1q {encap}",
		f"vrf forwarding {vrf}",
		f"ip address {xephysip2} {mask}",
		f"standby version 2",
		f"standby {xegroup} ip {xevip}",
		f"standby {xegroup} timers msec 600 2",
		f"standby {xegroup} priority {sbypri}",
		f"standby {xegroup} preempt",
		"no shut",
		]

		addvip1xr = [
		f"int bundle-ether{poadd}.{encap}",
		f"ipv4 address {xrphysip1} {mask}",
		f"encapsulation dot1q {encap}",
		"no shut",
		]

		addvip2xr = [
		f"int bundle-ether{poadd}.{encap}",
		f"ipv4 address {xrphysip2} {mask}",
		f"encapsulation dot1q {encap}",
		"no shut",
		]

		addhsrp1xr = [
		f"router hsrp interface bundle-ether{poadd}.{encap} hsrp redirects disable",
		f"router hsrp interface bundle-ether{poadd}.{encap} address-family ipv4",
		f"hsrp {xrgroup} version 2",
		f"prempt",
		f"priority {actpri}",
		f"address {xrvip}",
		]

		addhsrp2xr = [
		f"router hsrp interface bundle-ether{poadd}.{encap} hsrp redirects disable",
		f"router hsrp interface bundle-ether{poadd}.{encap} address-family ipv4",
		f"hsrp {xrgroup} version 2",
		f"prempt",
		f"priority {sbypri}",
		f"address {xrvip}",
		]

		checkhsrpxe = "do show standby brief"
		checkhsrpxr = "do show hsrp brief"
		
		#Delete VIPs on XE devices
		print ("\nIOS-XE VIP Cutover\n")
		connections['nc_rtr1'].send_config_set(delvipxe)
		print (f"Po{podel}.{encap} deleted from IOS-XE router 1")
		file.write(f"Po{podel}.{encap} deleted from XE router 1 \n\n")

		connections['nc_rtr2'].send_config_set(delvipxe)
		print (f"Po{podel}.{encap} deleted from IOS-XE router 2")
		file.write(f"Po{podel}.{encap} deleted from XE router 2 \n\n")
		
		#Create VIPs on XE devices

		connections['nc_rtr1'].send_config_set(addvip1xe)
		print (f"Po{poadd}.{encap} created on IOS-XE router 1")
		file.write(f"Po{poadd}.{encap} created on XE router 1 \n\n")
		
		connections['nc_rtr2'].send_config_set(addvip2xe)
		print (f"Po{poadd}.{encap} created on IOS-XE router 2 \n")
		file.write(f"Po{poadd}.{encap} created on XE router 2 \n\n")
		
		#Delete VIPs on XR devices
		print ("IOS-XR VIP Cutover\n")
		connections['nc_rtr3'].config_mode()
		connections['nc_rtr3'].send_config_set(delvipxr)
		connections['nc_rtr3'].send_config_set(delhsrp)	  
		print (f"Bundle-Ether{podel}.{encap} and HSRP config deleted from XR router 1")
		file.write(f"Po{podel}.{encap} deleted from XR router 1 \n\n")

		connections['nc_rtr4'].config_mode()
		connections['nc_rtr4'].send_config_set(delvipxr)
		connections['nc_rtr4'].send_config_set(delhsrp)			
		print (f"Bundle-Ether{podel}.{encap} and HSRP config  deleted from XR router 2")
		file.write(f"Po{podel}.{encap} deleted from XR router 2 \n\n")

		#Create VIPs on XR devices
				   
		connections['nc_rtr3'].config_mode()		
		connections['nc_rtr3'].send_config_set(addvip1xr)
		connections['nc_rtr3'].send_config_set(addhsrp1xr)
		connections['nc_rtr3'].commit()		   
		print (f"Bundle-Ether{poadd}.{encap} and HSRP config created on XR router 1")
		file.write(f"Po{poadd}.{encap} created on XR router 1 \n\n")
		
		connections['nc_rtr4'].config_mode()
		connections['nc_rtr4'].send_config_set(addvip2xr)
		connections['nc_rtr4'].send_config_set(addhsrp2xr)
		connections['nc_rtr4'].commit()
		print (f"Bundle-Ether{poadd}.{encap} and HSRP config created on XR router 2 \n")
		file.write(f"Po{poadd}.{encap} created on XR router 2")
		
		#Await HSRP convergence

		print ("Script sleeping 20s whilst HSRP converges \n")
		time.sleep(20.0)
		hsrp1 = connections['nc_rtr1'].send_config_set(checkhsrpxe)
		hsrp2 = connections['nc_rtr2'].send_config_set(checkhsrpxe)
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
