Name: cee-server
Version: 1.0
Release: 1%{?dist}
Summary: A CEE log server for capturing and managing Common Event Expressions
License: MIT
URL: https://github.com/allamiro/cee-server
Source0: %{name}-%{version}.tar.gz

BuildArch: noarch
Requires: python3, systemd

%description
CEE Server is a Python-based application that captures Common Event Expressions
(CEE) logs via HTTP PUT requests and writes them to a rotating log file.

%prep
%setup -q

%build
# No compilation is needed for this Python-based script

%install
mkdir -p %{buildroot}/usr/local/bin
mkdir -p %{buildroot}/etc/cee-server
mkdir -p %{buildroot}/var/log/cee-server

install -m 755 cee_log_server.py %{buildroot}/usr/local/bin/cee_log_server
install -m 755 configure_service.bash %{buildroot}/usr/local/bin/configure_service
install -m 644 LICENSE %{buildroot}/etc/cee-server/LICENSE
install -m 644 README.md %{buildroot}/etc/cee-server/README.md
install -m 644 rpm/SOURCES/cee-server.service %{buildroot}/usr/lib/systemd/system/cee-server.service

%post
systemctl daemon-reload
systemctl enable cee-server

%preun
if [ "$1" -eq 0 ]; then
    systemctl disable cee-server
    systemctl stop cee-server
    rm -rf /var/log/cee-server
fi
systemctl daemon-reload

%files
/usr/local/bin/cee_log_server
/usr/local/bin/configure_service
/etc/cee-server/LICENSE
/etc/cee-server/README.md
/usr/lib/systemd/system/cee-server.service
/var/log/cee-server/

%changelog
* Thu Dec 19 2024 Tamir Suliman <allamiro@gmail.com> - 1.0-1
- Initial package release
- Added support for creating and cleaning up the log directory at /var/log/cee-server
