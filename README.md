Netmiko - Cisco Port-Channel Migration (IOS-XE / IOS-XR)
· Documentation · Report Bug · Request Feature
🌟 About the Project

    This project is designed to automate the cutover of HSRP between port-channels on the same router. Connectivity between HSRP endpoints is via a standard L2 switch with corresponding port-channels and VLAN trunks. 

    There are two pairs of routers participating in HSRP that must be moved to another port-channel on the same router, something that might be done when moving the traffic path for upstream devices concurrently.

    The routers are virtualised ASR1Ks (CSR1000v) and ASR9Ks (IOSXRv) and the switch is just an IOS-L2 image.
    
🎯 Languages

    Python3, YAML.
