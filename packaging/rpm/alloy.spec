%global debug_package %{nil}
%undefine _debugsource_packages
%undefine dist

# Default (same name in RPM and Go)
%global goarch %{_arch}

%ifarch x86_64
%global goarch amd64
%endif

%ifarch aarch64
%global goarch arm64
%endif

Name:           alloy
Version:        1.16.0
Release:        1%{?dist}
Summary:        OpenTelemetry Collector distribution with programmable pipelines
License:        Apache-2.0
URL:            https://github.com/grafana/alloy

Source0:        https://github.com/grafana/alloy/archive/refs/tags/v%{version}.tar.gz#/alloy-%{version}.tar.gz
Source1:        alloy.sysusers

BuildRequires:  golang >= 1.22
BuildRequires:  git
BuildRequires:  make
BuildRequires:  redhat-rpm-config
BuildRequires:  systemd-rpm-macros
BuildRequires:  systemd-devel
BuildRequires:  which
BuildRequires:  npm
BuildRequires:  hostname

%description
Grafana Alloy is Grafana Labs' distribution of the OpenTelemetry Collector.
It supports metrics, logs, traces, and profiles with built-in Prometheus optimizations.

%prep
%setup -q -n alloy-%{version}

%build
VERSION=%{version}  make dist/alloy-linux-%{goarch}

%install
# main binary
install -Dm0755 dist/alloy-linux-%{goarch} %{buildroot}%{_bindir}/alloy

# sysusers (user alloy)
install -Dm0644 packaging/rpm/%{name}.sysusers %{buildroot}%{_sysusersdir}/alloy.conf

# main service
install -Dm0644 packaging/rpm/%{name}.service %{buildroot}%{_unitdir}/%{name}.service

# default config
install -Dm0644 packaging/environment-file %{buildroot}%{_sysconfdir}/sysconfig/alloy
install -Dm0644 packaging/config.alloy %{buildroot}%{_sysconfdir}/%{name}/config.alloy

# runtime dirs
install -dm0770 %{buildroot}%{_sharedstatedir}/%{name}
install -dm0770 %{buildroot}%{_sharedstatedir}/%{name}/data

# systemd preset file
install -Dm0644 packaging/rpm/%{name}.preset %{buildroot}%{_presetdir}/90-alloy.preset

%pre
# create system user and group via systemd-sysusers
%sysusers_create_package %{name} %SOURCE1

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%license LICENSE
%doc README.md CHANGELOG.md

%{_bindir}/alloy
%{_unitdir}/%{name}.service
%{_sysusersdir}/alloy.conf
%dir %attr(0770,%{name},%{name}) %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/config.alloy
%config(noreplace) %{_sysconfdir}/sysconfig/alloy
%config %{_presetdir}/90-alloy.preset

%dir %attr(0770,%{name},%{name}) %{_sharedstatedir}/%{name}
%dir %attr(0770,%{name},%{name}) %{_sharedstatedir}/%{name}/data

%changelog
* Thu Nov 13 2025 Eugen <evgeniy.berladin@nga911.com>
- Converted user creation to systemd-sysusers
- Added systemd override 00-override.conf
- Added alloy.preset
- Revised CoreOS user creation fix
