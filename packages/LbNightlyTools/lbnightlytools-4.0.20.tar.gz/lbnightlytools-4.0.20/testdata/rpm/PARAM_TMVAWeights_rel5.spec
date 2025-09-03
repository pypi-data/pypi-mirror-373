
%define lhcb_maj_version 1
%define lhcb_min_version 4
%define lhcb_patch_version 0
%define lhcb_release_version 5
%define buildarea /tmp/rpmV9kRzW
%define project PARAM
%define projectUp PARAM
%define normfulldatapkg TMVAWeights
%define fulldatapkg TMVAWeights
%define fullname PARAM_TMVAWeights
%define fullnameWithVer PARAM_TMVAWeights_v1r4
%define package TMVAWeights
%define lbversion v1r4
%define _postshell /bin/bash
%define prefix /opt/LHCbSoft
%define versiondir PARAM/TMVAWeights

%global __os_install_post /usr/lib/rpm/check-buildroot

%define _topdir %{buildarea}/rpmbuild
%define tmpdir %{buildarea}/tmpbuild
%define _tmppath %{buildarea}/tmp

Name: %{fullnameWithVer}
Version: 1.0.0
Release: %{lhcb_release_version}
Vendor: LHCb
Summary: %{project}
License: GPL
Group: LHCb
BuildRoot: %{tmpdir}/%{name}-buildroot
BuildArch: noarch
AutoReqProv: no
Prefix: %{prefix}
Provides: /bin/sh
Provides: /bin/bash

Provides: %{package} = %{lhcb_maj_version}.%{lhcb_min_version}.%{lhcb_patch_version}
Provides: %{fullname} = %{lhcb_maj_version}.%{lhcb_min_version}.%{lhcb_patch_version}
Provides: %{package}_v%{lhcb_maj_version} = %{lhcb_maj_version}.%{lhcb_min_version}.%{lhcb_patch_version}
Provides: %{fullname}_v%{lhcb_maj_version} = %{lhcb_maj_version}.%{lhcb_min_version}.%{lhcb_patch_version}
Provides: %{package}_v%{lhcb_maj_version}r%{lhcb_min_version} = %{lhcb_maj_version}.%{lhcb_min_version}.%{lhcb_patch_version}
Provides: %{fullname}_v%{lhcb_maj_version}r%{lhcb_min_version} = %{lhcb_maj_version}.%{lhcb_min_version}.%{lhcb_patch_version}
Requires: %{projectUp}_common
Requires(post): LBSCRIPTS

%description
%{fullname} %{version}

%install
mkdir -p ${RPM_BUILD_ROOT}%{prefix}/lhcb/%{versiondir}
cd  ${RPM_BUILD_ROOT}%{prefix}/lhcb && unzip -q -o None



%clean

%post -p /bin/bash

if [ "$MYSITEROOT" ]; then
PREFIX=$MYSITEROOT
else
PREFIX=%{prefix}
fi

if [ -f $PREFIX/etc/update.d/%{package}_Update.py ]; then
rm -f $PREFIX/etc/update.d/%{package}_Update.py
fi

if [ -f $PREFIX/lhcb/%{versiondir}/%{lbversion}/cmt/Update.py ]; then
echo "Creating link in update.d"
mkdir -p -v $PREFIX/etc/update.d
ln -s $PREFIX/lhcb/%{versiondir}/%{lbversion}/cmt/Update.py $PREFIX/etc/update.d/%{package}_Update.py
echo "Running Update script"
. $PREFIX/LbEnv.sh --siteroot $PREFIX 2>/dev/null
echo "Now using python:"
which python
echo "PYTHONPATH: $PYTHONPATH"
echo "PATH: $PATH"
echo "LD_LIBRARY_PATH: $LD_LIBRARY_PATH"
python $PREFIX/lhcb/%{versiondir}/%{lbversion}/cmt/Update.py
fi

if [ -f $PREFIX/lhcb/%{versiondir}/%{lbversion}/cmt/PostInstall.py ]; then
echo "Running PostInstall script"
. $PREFIX/LbEnv.sh --siteroot $PREFIX 2>/dev/null
python $PREFIX/lhcb/%{versiondir}/%{lbversion}/cmt/PostInstall.py
fi

%postun -p /bin/bash
if [ "$MYSITEROOT" ]; then
PREFIX=$MYSITEROOT
else
PREFIX=%{prefix}
fi
echo "In uninstall script"
if [ -h $PREFIX/etc/update.d/%{package}_Update.py ]; then
echo "Removing link to update script:  $PREFIX/etc/update.d/%{package}_Update.py"
rm $PREFIX/etc/update.d/%{package}_Update.py
fi

%files
%defattr(-,root,root)
%{prefix}/lhcb/%{versiondir}/%{lbversion}


%define date    %(echo `LC_ALL="C" date +"%a %b %d %Y"`)

%changelog

* %{date} User <ben.couturier..rcern.ch>
- first Version
