# CEE Server Using Python

## What is Common Event Expression (CEE)?
CEE was developed by MITRE as an extension for Syslog, based on JSON. MITRE’s work on CEE was discontinued in 2013. Below is an example of a CEE log message:

```
Dec 20 12:42:20 syslog-relay serveapp[1335]: @cee: {"pri":10,"id":121,"appname":"serveapp","pid":1335,"host":"syslog-relay","time":"2011-12-20T12:38:05.123456-05:00","action":"login","domain":"app","object":"account","status":"success"}
```
## Required Tools

To set up the CEE Server on Redhat/CentOS/Fedora systems, ensure the following tools are installed:

```dnf install python3 python3-tools -y ```

## How to Use the Tool
### Run Manually

1. Clone the Repository

Clone the repository to your preferred location:

```git clone https://github.com/allamiro/cee-server.git```

2. Navigate to the Directory and Run the Script

Change the directory to the cee-server directory and run the script:

```cd cee-server```

```python3 cee_log_server.py```

3. Create a Service for Continuous Execution (Optional)

If you want the script to run as a persistent service:

* Make the ```configure_service.bash``` script executable:

```chmod +x configure_service.bash```

* Execute the script to create the service:

```./configure_service.bash ```

This will create and enable a systemd service for the CEE server.

## Build and Deploy the RPM

### Steps to Build the RPM

1. Install Required Tools

* Install the RPM build tools:

``` sudo dnf install rpm-build rpmlint -y ```

2. Set Up the RPM Build Environment

* Create the directory structure for RPM packaging:

```mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}```

3. Create the Source Tarball

Package the repository into a tarball:

```
cd cee-server
mkdir cee-server-1.0
cp -r ./* cee-server-1.0/
tar --exclude-vcs -czf ~/rpmbuild/SOURCES/cee-server-1.0.tar.gz cee-server-1.0
rm -rf cee-server-1.0
```

4. Copy the Spec File

Place the spec file in the appropriate directory:

```cp rpm/SPECS/cee-server.spec ~/rpmbuild/SPECS/```

5. Build the RPM

Run the RPM build process:

```cd ~/rpmbuild/SPECS
rpmbuild -ba cee-server.spec
```

5. Verify the RPM

Check if the RPM was created successfully:

```ls ~/rpmbuild/RPMS/noarch/```

6. Install and Test the RPM

Install the built RPM:

```sudo rpm -ivh ~/rpmbuild/RPMS/noarch/cee-server-1.0-1.noarch.rpm```

7. Verify the systemd service is installed and enabled:


```systemctl status cee-server```

8. Start the service if it is not running:

```sudo systemctl start cee-server```


## References

* MITRE CEE Documentation
* NXLog Integration with CEE
