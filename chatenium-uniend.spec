Name:           python3-chatenium-uniend
Version:        0.3.2
Release:        1%{?dist}
Summary:        Chatenium UniEnd

License:        GPL-3.0-or-later
URL:            https://chtn.hu
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:	python3-setuptools
BuildRequires:  python3-wheel
BuildRequires:	expat-devel
BuildRequires:  python3-build

Requires:	python3-requests
Requires:	python3-keyring
Requires:	python3-aiohttp
Requires:       python3
Requires:	python3-websocket-client

%global debug_package %{nil}

%description
Chatenium On Linux is a GTK4 client built with libadwaita, implemented
in Python and built using Meson.

%prep
%autosetup

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%files
%license LICENSE
%doc README.md

%{python3_sitelib}/backend*
%{python3_sitelib}/chatenium_uniend-*.dist-info/

%changelog
* Tue Jan 06 2026 chatenium <personal@alms.hu> - 0.3.1-1
- Initial Fedora RPM release

