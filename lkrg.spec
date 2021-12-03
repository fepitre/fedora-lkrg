%global module lkrg

Name: lkrg
Version: 0.9.1
Release: 1%{?dist}
Summary: Linux Kernel Runtime Guard (LKRG)

License: GPLv2
Source0: https://www.openwall.com/lkrg/%{name}-%{version}.tar.gz
Source1: https://www.openwall.com/lkrg/%{name}-%{version}.tar.gz.sign
Source2: lkrg-signing-key.asc
Source3: lkrg-dkms.dkms
Source4: lkrg-dkms.modules

BuildRequires: gnupg2
BuildRequires: make
BuildRequires: gcc
BuildRequires: systemd

%description
LKRG performs runtime integrity checking of the Linux kernel and detection of
security vulnerability exploits against the kernel.

LKRG is a kernel module (not a kernel patch), so it can be built for and loaded
on top of a wide range of mainline and distros' kernels, without needing to
patch those.

That is only a dependency package to install the LKRG kernel module and also
some systemd service in order to help to manage loading/unloading the module at
system boot/shutdown.

%package dkms
Summary: Linux Kernel Runtime Guard (LKRG) Source Code and DKMS
Requires: dkms

%description dkms
This package uses DKMS to automatically build the LKRG kernel module.

%package systemd
Summary: Systemd integration for Linux Kernel Runtime Guard (LKRG)
Requires: systemd
Requires: %{name}-dkms

%description systemd
This package provides systemd integration for the LKRG kernel module.


%prep
%{gpgverify} --keyring='%{SOURCE2}' --signature='%{SOURCE1}' --data='%{SOURCE0}'
%setup -q

%install
# dkms
mkdir -p "$RPM_BUILD_ROOT"/usr/src/%{module}-%{version}/
cp -r scripts "$RPM_BUILD_ROOT"/usr/src/%{module}-%{version}/
cp -r src "$RPM_BUILD_ROOT"/usr/src/%{module}-%{version}/
install -D -m 0664 Makefile "$RPM_BUILD_ROOT"/usr/src/%{module}-%{version}/
install -D -m 0664 %{SOURCE3} "$RPM_BUILD_ROOT"/usr/src/%{module}-%{version}/dkms.conf
sed -i 's|@MODULE_VERSION@|%{version}|' "$RPM_BUILD_ROOT"/usr/src/%{module}-%{version}/dkms.conf
install -D -m 0664 %{SOURCE4} "$RPM_BUILD_ROOT"/etc/modules-load.d/lkrg-dkms.conf
install -D -m 0664 scripts/bootup/lkrg.conf "$RPM_BUILD_ROOT"/etc/sysctl.d/lkrg.conf

# systemd
install -D -m 0664 scripts/bootup/systemd/lkrg.service "$RPM_BUILD_ROOT"/%{_unitdir}/lkrg.service

%files dkms
%defattr(-,root,root)
/etc/modules-load.d/lkrg-dkms.conf
/etc/sysctl.d/lkrg.conf
/usr/src/%{module}-%{version}

%files systemd
%{_unitdir}/lkrg.service

%post dkms
dkms add -m %{module} -v %{version} --rpm_safe_upgrade
if [ -e /lib/modules/$(uname -r)/build/include ]; then
    dkms build -m %{module} -v %{version}
    dkms install -m %{module} -v %{version}
else
    echo -e ""
    echo -e "Cannot find kernel headers for this kernel."
    echo -e "Skipping build and install stages..."
fi

%preun dkms
dkms remove -m %{module} -v %{version} --all --rpm_safe_upgrade

%post systemd
%systemd_post lkrg.service

%preun systemd
%systemd_preun lkrg.service

%changelog
* Fri Dec 03 2021 Frédéric Pierret (fepitre) <frederic.pierret@qubes-os.org> - 0.9.1-1
	
- Initial RPM packaging.
