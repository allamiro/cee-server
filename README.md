# CEE Server  using python

## What is Common Event Expression (CEE)

CEE was developed by MITRE as an extension for Syslog, based on JSON. MITRE’s work on CEE was discontinued in 2013.


```Dec 20 12:42:20 syslog-relay serveapp[1335]: @cee: {"pri":10,"id":121,"appname":"serveapp","pid":1335,"host":"syslog-relay","time":"2011-12-20T12:38:05.123456-05:00","action":"login","domain":"app","object":"account","status":"success"}```


### Required Tools

* On Redhat / CentOS / Fedora
```
dnf install python3 python3-tools -y
```


### How to use the tool

1. Clone the repository to your prefered location
```
git clone https://github.com/allamiro/cee-server.git
```

2. Change the directory to the CEE Server directory and run the script

```
cd cee-server
python3 cee_log_server.py 

```


3. If you want to create a service file which would allow the script to run non stop

```
chmod +x configure_service.bash

./configure_service.bash

```


### References
- [ ] https://docs.nxlog.co/integrate/cee.html
