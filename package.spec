%define _version 0.4.0
%define _release 1

Name:           jamjar
Version:        %{_version}
Release:        %{_release}%{?dist}
Summary:        JamJar is a CLI tool designed to "seal" the history of your Spotify playlists, just like a jar preserves your favorite jams. 
License:        MIT
URL:            https://github.com/AntonVanAssche/JamJar

Source0:        %{name}-%{_version}.tar.gz
Source1:        %{name}

BuildRequires:  python3.12-devel
Requires:       python3.12

%description
JamJar is a CLI tool designed to "seal" the history of your Spotify playlists,
just like a jar preserves your favorite jams. Whether it's a collaborative
playlist with friends or your personal collection, JamJar saves every track
and its details into a database. No more losing track of who added what or
what songs were removed—keep your playlist history fresh and intact, like
music in a jar!

%define _buildshell /usr/bin/bash
%define __python    /usr/bin/python3.12
%define python3_version 3.12

%prep
%{__python} -m venv --clear ./%{name}


%build
. ./%{name}/bin/activate
python -m pip install --disable-pip-version-check --no-cache-dir --no-compile %{SOURCE0}
deactivate
find ./%{name} -type d -name __pycache__ -exec rm -rf '{}' '+'
find ./%{name} -type f -exec %{__sed} -i 's|%{_builddir}|/usr/local/lib|g' '{}' '+'

%install
%{__mkdir_p} %{buildroot}/usr/local/lib
%{__cp} -r ./%{name} %{buildroot}/usr/local/lib
%{__mkdir_p} %{buildroot}/usr/local/bin
%{__install} -D -m 0755 %{SOURCE1} %{buildroot}/usr/local/bin/%{name}
%{py3_shebang_fix} %{buildroot}/usr/local/lib/%{name} &>/dev/null

%files
%defattr(-,root,root,-)
/usr/local/bin/%{name}
/usr/local/lib/%{name}
