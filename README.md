# CEE Server  using python

## What is Common Event Expression (CEE)

CEE was developed by MITRE as an extension for Syslog, based on JSON. MITRE’s work on CEE was discontinued in 2013.


```Dec 20 12:42:20 syslog-relay serveapp[1335]: @cee: {"pri":10,"id":121,"appname":"serveapp","pid":1335,"host":"syslog-relay","time":"2011-12-20T12:38:05.123456-05:00","action":"login","domain":"app","object":"account","status":"success"}```


### Required Tools

* On Redhat / CentOS / Fedora
```
dnf install python3 python3-tools -y
```

## Collecting and parsing CEE logs using python 



### References
- [ ] https://docs.nxlog.co/integrate/cee.html
