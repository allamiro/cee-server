Name:           cee_log_server
Version:        0.1
Release:        1%{?dist}
Summary:        CEE Log Server application

License:        MIT
URL:            https://github.com/allamiro/cee-servever
Source0:        cee_log_server-0.1.tar.gz

BuildArch:      noarch
BuildRequires:  python3
Requires:       python3

%description
A simple Python-based HTTP server for receiving CEE audit events.

%prep
%setup -q -n cee_log_server-0.1

%build
# No compilation needed for Python scripts.

%install
mkdir -p %{buildroot}/usr/local/bin
mkdir -p %{buildroot}/usr/lib/systemd/system

install -m 0755 cee_log_server.py %{buildroot}/usr/local/bin/
install -m 0644 systemd/cee_log_server.service %{buildroot}/usr/lib/systemd/system/


%files
%license
%doc
/usr/local/bin/cee_log_server.py
/usr/lib/systemd/system/cee_log_server.service

%changelog
* Thu Dec 19 2024 Your Name <you@example.com> - 0.1-1
- Initial RPM packaging.
