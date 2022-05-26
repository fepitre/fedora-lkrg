Name:           lkrg
Version:        0.9.1
Release:        1%{?dist}

Summary:        Kernel module for Linux Kernel Runtime Guard (LKRG)
License:        GPLv2
URL:            https://www.openwall.com/lkrg

Source0:        lkrg-%{version}.tar.gz
Source1:        lkrg-%{version}.tar.gz.sign
Source2:        lkrg-signing-key.asc

BuildRequires:  gnupg2
BuildRequires:  systemd

Provides:       %{name}-kmod-common = %{version}


%description
LKRG performs runtime integrity checking of the Linux kernel and detection of
security vulnerability exploits against the kernel.

LKRG is a kernel module (not a kernel patch), so it can be built for and loaded
on top of a wide range of mainline and distros' kernels, without needing to
patch those.

That is only a dependency package to install the LKRG kernel module and also
some systemd service in order to help to manage loading/unloading the module at
system boot/shutdown.


%prep
%{gpgverify} --keyring='%{SOURCE2}' --signature='%{SOURCE1}' --data='%{SOURCE0}'
%setup -q


%install
rm -rf ${RPM_BUILD_ROOT}
mkdir -p ${RPM_BUILD_ROOT}

for doc in README LICENSE CHANGES CONCEPTS PERFORMANCE ; do
    install -D -m 0664 ${doc} ${RPM_BUILD_ROOT}/%{_pkgdocdir}/${doc}
done

install -D -m 0664 scripts/bootup/lkrg.conf "$RPM_BUILD_ROOT"/etc/sysctl.d/lkrg.conf
install -D -m 0664 scripts/bootup/systemd/lkrg.service "$RPM_BUILD_ROOT"/%{_unitdir}/lkrg.service


%files
%doc README LICENSE CHANGES CONCEPTS PERFORMANCE
/etc/sysctl.d/lkrg.conf
%{_unitdir}/lkrg.service


%post
%systemd_post lkrg.service


%preun
%systemd_preun lkrg.service


%clean
rm -rf $RPM_BUILD_ROOT


%changelog
* Sat Dec 04 2021 Frédéric Pierret (fepitre) <frederic.pierret@qubes-os.org> - 0.9.1-1
- Initial RPM packaging.
