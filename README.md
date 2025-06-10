<div align='center'>

<h1>Netmiko - Cisco - Port-Channel Migration</h1>
<h4> <span> · </span> <a href="https://github.com/daisy-dynawhite/Cisco-CMD/blob/master/README.md"> Documentation </a> <span> · </span> <a href="https://github.com/daisy-dynawhite/Cisco-CMD/issues"> Report Bug </a> <span> · </span> <a href="https://github.com/daisy-dynawhite/Cisco-CMD/issues"> Request Feature </a> </h4>
</div>

# :star2: About the Project
    
- <p>This project is designed to automate the cutover of HSRP between port-channels on the same router. Connectivity between HSRP endpoints is via a standard L2 switch with corresponding port-channels and VLAN trunks. </p>
- <p>There are two pairs of routers participating in HSRP that must be moved to another port-channel on the same router, something that might be done when moving the traffic path for upstream devices concurrently.</p>
- <p>The routers are virtualised ASR1Ks (CSR1000v) and ASR9Ks (IOSXRv) and the switch is just an IOS-L2 image.</p>

## :dart: Languages
- Python3 and YAML.
  
## :camera: Screenshots
<div align="left"> <a href=""><img src="https://github.com/daisy-dynawhite/Cisco-CMD/blob/main/Cisco-CMD-Output.png" alt='image' width='293' height='419'/></a> </div>
