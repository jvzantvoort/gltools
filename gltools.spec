Summary: GLTools a gitlab wrapper
Name: gltools
Version: 0.3.3
Release: 1
Source0: %{name}-%{version}.tar.gz
License: MIT
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: John van Zantvoort <john.van.zantvoort@proxy.nl>
Url: https://github.com/jvzantvoort/gltools

%description
This tool is created to quickly and easily setup and maintain a
source tree. It's geared towards an Ansible related source tree so
there are some tweaks supporting that (specially when exporting) but
should work on others too.

%prep
%setup -n %{name}-%{version}

%build
python setup.py build

%install
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)

%changelog
* Wed Jul 01 2020 John van Zantvoort <john@vanzantvoort.org> 0.3.3-1
- minor update (john@vanzantvoort.org)

