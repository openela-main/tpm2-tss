Name:          tpm2-tss
Version:       3.2.2
Release:       2%{?dist}
Summary:       TPM2.0 Software Stack

License:       BSD
URL:           https://github.com/tpm2-software/tpm2-tss
Source0:       https://github.com/tpm2-software/tpm2-tss/releases/download/%{version}/%{name}-%{version}.tar.gz
Source1:       tpm2-tss-systemd-sysusers.conf
# doxygen patch
Patch0: tpm2-tss-3.0.0-doxygen.patch
Patch2: 0001-esys_iutil-fix-possible-NPD.patch
Patch3: 0001-tss2-rc-fix-unknown-layer-handler-dropping-bits.patch
Patch4: 0002-MU-Fix-unneeded-size-check-in-TPM2B-unmarshaling.patch
Patch5: 0003-FAPI-Fix-parameter-encryption-for-provisioning.patch
Patch6: 0004-FAPI-Fix-missing-parameter-encryption-for-policy-ses.patch
Patch7: 0005-FAPI-Fix-missing-parameter-encryption-for-some-HMAC-.patch
Patch8: 0006-FAPI-Fix-usage-of-persistent-handles.patch
Patch11: 0007-build-Fix-failed-build-with-disable-vendor.patch
Patch12: 0008-FAPI-Fapi_GetInfo-display-warning-for-SHA3-hash-algs.patch
Patch13: 0009-FAPI-Skip-provisioning-test-for-nv-ext-and-profile-p.patch
Patch14: 0010-FAPI-Fix-wrong-allocation-of-pcr-policy.patch

%global udevrules_prefix 60-

BuildRequires: make
BuildRequires: autoconf-archive
BuildRequires: doxygen
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: json-c-devel
BuildRequires: libcurl-devel
BuildRequires: libgcrypt-devel
BuildRequires: libtool
BuildRequires: openssl-devel
BuildRequires: pkgconfig
BuildRequires: systemd
BuildRequires: systemd-rpm-macros
Requires(pre): shadow-utils

%description
tpm2-tss is a software stack supporting Trusted Platform Module(TPM) 2.0 system
APIs. It sits between TPM driver and applications, providing TPM2.0 specified
APIs for applications to access TPM module through kernel TPM drivers.

%prep
%autosetup -p1 -n %{name}-%{version}

%build
# Use built-in tpm-udev.rules, with specified installation path and prefix.
%configure --disable-static --disable-silent-rules \
           --disable-tcti-pcap --disable-tcti-libtpms \
           --with-udevrulesdir=%{_udevrulesdir} --with-udevrulesprefix=%{udevrules_prefix} \
           --with-runstatedir=%{_rundir} --with-tmpfilesdir=%{_tmpfilesdir} --with-sysusersdir=%{_sysusersdir}

# This is to fix Rpath errors. Taken from https://fedoraproject.org/wiki/Packaging:Guidelines#Removing_Rpath
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

%make_build

%install
%make_install
find %{buildroot}%{_libdir} -type f -name \*.la -delete
rm %{buildroot}%{_sysusersdir}/tpm2-tss.conf
install -p -D -m 0644 %{SOURCE1} %{buildroot}%{_sysusersdir}/tpm2-tss.conf

%pre
%sysusers_create_compat %{SOURCE1}
exit 0

%ldconfig_scriptlets

%files
%doc README.md CHANGELOG.md
%license LICENSE
%{_sysconfdir}/tpm2-tss/
%{_libdir}/libtss2-mu.so.0*
%{_libdir}/libtss2-sys.so.1*
%{_libdir}/libtss2-esys.so.0*
%{_libdir}/libtss2-fapi.so.1*
%{_libdir}/libtss2-rc.so.0*
%{_libdir}/libtss2-tctildr.so.0*
%{_libdir}/libtss2-tcti-cmd.so.0*
%{_libdir}/libtss2-tcti-device.so.0*
%{_libdir}/libtss2-tcti-mssim.so.0*
%{_libdir}/libtss2-tcti-swtpm.so.0*
%{_sysusersdir}/tpm2-tss.conf
%{_tmpfilesdir}/tpm2-tss-fapi.conf
%{_udevrulesdir}/%{udevrules_prefix}tpm-udev.rules

%package        devel
Summary:        Headers and libraries for building apps that use tpm2-tss 
Requires:       %{name}%{_isa} = %{version}-%{release}

%description    devel
This package contains headers and libraries required to build applications that
use tpm2-tss.

%files devel
%{_includedir}/tss2/
%{_libdir}/libtss2-mu.so
%{_libdir}/libtss2-sys.so
%{_libdir}/libtss2-esys.so
%{_libdir}/libtss2-fapi.so
%{_libdir}/libtss2-rc.so
%{_libdir}/libtss2-tctildr.so
%{_libdir}/libtss2-tcti-cmd.so
%{_libdir}/libtss2-tcti-device.so
%{_libdir}/libtss2-tcti-mssim.so
%{_libdir}/libtss2-tcti-swtpm.so
%{_libdir}/pkgconfig/tss2-mu.pc
%{_libdir}/pkgconfig/tss2-sys.pc
%{_libdir}/pkgconfig/tss2-esys.pc
%{_libdir}/pkgconfig/tss2-fapi.pc
%{_libdir}/pkgconfig/tss2-rc.pc
%{_libdir}/pkgconfig/tss2-tctildr.pc
%{_libdir}/pkgconfig/tss2-tcti-cmd.pc
%{_libdir}/pkgconfig/tss2-tcti-device.pc
%{_libdir}/pkgconfig/tss2-tcti-mssim.pc
%{_libdir}/pkgconfig/tss2-tcti-swtpm.pc
%{_mandir}/man3/*.3.gz
%{_mandir}/man5/*.5.gz
%{_mandir}/man7/tss2*.7.gz


%changelog
* Mon Jul 3 2023 Štěpán Horáček <shoracek@redhat.com> - 3.2.2-2
- Remove misapplied license
  Resolves: rhbz#2160307

* Fri Jun 23 2023 Štěpán Horáček <shoracek@redhat.com> - 3.2.2-1
- Rebase to 3.2.2
- Use systemd-sysusers to create user
  Resolves: CVE-2023-22745
  Resolves: rhbz#2095479
  Resolves: rhbz#2160307
  Resolves: rhbz#2162613

* Wed Aug 10 2022 Štěpán Horáček <shoracek@redhat.com> - 3.0.3-8
- Fix memory leaks, potential crashes, upgrade to OpenSSL 3
  Resolves: rhbz#2041919

* Thu Feb 17 2022 Štěpán Horáček <shoracek@redhat.com> - 3.0.3-7
- Rebuild with latest json-c library
  Related: rhbz#2023328

* Wed Aug 18 2021 Štěpán Horáček <shoracek@redhat.com> - 3.0.3-6
- Fix failures while using OpenSSL 3
  Resolves: rhbz#1984634

* Tue Aug 10 2021 Mohan Boddu <mboddu@redhat.com> - 3.0.3-5
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Wed Jun 16 2021 Mohan Boddu <mboddu@redhat.com> - 3.0.3-4
- Rebuilt for RHEL 9 BETA for openssl 3.0
  Related: rhbz#1971065

* Fri Apr 16 2021 Mohan Boddu <mboddu@redhat.com> - 3.0.3-3
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Wed Jan 27 2021 Fedora Release Engineering <releng@fedoraproject.org> - 3.0.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Thu Nov 26 2020 Peter Robinson <pbrobinson@fedoraproject.org> - 3.0.3-1
- Update to 3.0.2

* Sun Nov 22 2020 Peter Robinson <pbrobinson@fedoraproject.org> - 3.0.2-1
- Update to 3.0.2

* Wed Sep 23 2020 Peter Robinson <pbrobinson@fedoraproject.org> - 3.0.1-1
- Update to 3.0.1

* Tue Sep 15 2020 Than Ngo <than@redhat.com> - 3.0.0-4
- Fix doxygen crash

* Tue Sep 15 2020 Peter Robinson <pbrobinson@fedoraproject.org> - 3.0.0-3
- Create tss user, if it doesn't exist, for userspace TPM access

* Fri Aug 07 2020 Peter Robinson <pbrobinson@fedoraproject.org> - 3.0.0-2
- Install sysusers config in sysusersdir (rhbz #1834519)

* Wed Aug 05 2020 Peter Robinson <pbrobinson@fedoraproject.org> - 3.0.0-1
- Update to 3.0.0

* Wed Aug 05 2020 Peter Robinson <pbrobinson@fedoraproject.org> - 2.4.2-1
- Update to 2.4.2

* Wed Jul 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 2.4.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Thu May 14 2020 Peter Robinson <pbrobinson@fedoraproject.org> - 2.4.1-1
- Update to 2.4.1

* Fri May 08 2020 Paul Wouters <pwouters@redhat.com> - 2.4.0-3
- Use proper rundir and tmpfiles macros so proper directories are used

* Tue Apr 21 2020 Björn Esser <besser82@fedoraproject.org> - 2.4.0-2
- Rebuild (json-c)

* Thu Mar 12 2020 Peter Robinson <pbrobinson@fedoraproject.org> - 2.4.0-1
- Update to 2.4.0 release

* Mon Feb 24 2020 Peter Robinson <pbrobinson@fedoraproject.org> - 2.3.3-1
- Update to 2.3.3 release

* Fri Jan 31 2020 Fedora Release Engineering <releng@fedoraproject.org> - 2.3.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Fri Dec 13 2019 Yunying Sun <yunying.sun@intel.com> - 2.3.2-1
- Update to 2.3.2 release

* Fri Sep 6 2019 Yunying Sun <yunying.sun@intel.com> - 2.3.1-1
- Update to 2.3.1 release

* Thu Aug 15 2019 Yunying Sun <yunying.sun@intel.com> - 2.3.0-1
- Update to 2.3.0 release

* Sat Jul 27 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2.2.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Wed May 29 2019 Yunying Sun <yunying.sun@intel.com> - 2.2.3-1
- Update to 2.2.3 release

* Fri Mar 29 2019 Yunying Sun <yunying.sun@intel.com> - 2.2.2-1
- Update to 2.2.2 release

* Mon Mar  4 2019 Peter Robinson <pbrobinson@fedoraproject.org> 2.2.1-1
- Update to 2.2.1 release

* Wed Feb 06 2019 Javier Martinez Canillas <javierm@redhat.com> - 2.2.0-1
- Update to 2.2.0 release

* Sun Feb 03 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2.1.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Wed Oct 10 2018 Yunying Sun <yunying.sun@intel.com> - 2.1.0-1
- Update to 2.1.0 release

* Thu Aug 30 2018 Yunying Sun <yunying.sun@intel.com> - 2.0.1-1
- Update to 2.0.1 release

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Jul 4 2018 Yunying Sun <yunying.sun@intel.com> - 2.0.0-2
- Re-enable ESAPI since gcrypt dependency is not an issue for Fedora
- Bump release version to 2.0.0-2

* Mon Jul 2 2018 Yunying Sun <yunying.sun@intel.com> - 2.0.0-1
- Update to 2.0.0 release (RHBZ#1508870)
- Remove patch file 60-tpm-udev.rules, use upstream tpm-udev.rules instead
- Disable ESAPI to fix build errors caused by dependency to libgcrypt 1.6.0
- Add scriptlet to fix Rpath errors
- Update file installation paths and names accordingly 

* Sun Mar 04 2018 Javier Martinez Canillas <javierm@redhat.com> - 1.4.0-1
- Update URLs to point to the new project location
- Add README.md CHANGELOG.md to %%files directive
- Update to 1.4.0 release (RHBZ#1508870)

* Fri Feb 23 2018 Javier Martinez Canillas <javierm@redhat.com> - 1.3.0-4
- Install udev rule for TPM character devices

* Wed Feb 21 2018 Javier Martinez Canillas <javierm@redhat.com> - 1.3.0-3
- Remove ExclusiveArch: %%{ix86} x86_64 directive

* Fri Feb 09 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1.3.0-2
- Escape macros in %%changelog

* Fri Dec 08 2017 Javier Martinez Canillas <javierm@redhat.com> - 1.3.0-1
- Update to 1.3.0 release

* Wed Nov 29 2017 Javier Martinez Canillas <javierm@redhat.com> - 1.3.0-0.1.rc2
- Update to 1.3.0 release candidate 2 (RHBZ#1508870)
- Remove global pkg_prefix since now the upstream repo and package names match
- Update URLs to point to the new project location
- Remove -Wno-int-in-bool-context compiler flag since now upstream takes care
- Remove %%doc directive since README.md and CHANGELOG.md are not in the tarball
- Add patch to include a LICENSE since the generated tarball does not have it

* Mon Aug 28 2017 Javier Martinez Canillas <javierm@redhat.com> - 1.2.0-1
- Update to 1.2.0 release
- Use tpm2-tss instead of TPM2.0-TSS as prefix since project name changed
- Fix SPEC file access mode
- Include new man pages in %%files directive

* Fri Aug 18 2017 Javier Martinez Canillas <javierm@redhat.com> - 1.1.0-3
- Remove unneeded source tarballs (RHBZ#1482828)

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Sun Yunying <yunying.sun@intel.com> - 1.1.0-1
- Update to 1.1.0 release

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Dec 12 2016 Sun Yunying <yunying.sun@intel.com> - 1.0-2
- Remove global macro pkg_version to avoid duplicate of version
- Use ExclusiveArch instead of ExcludeArch
- Use less wildcard in %%files section to be more specific
- Add trailing slash at end of added directory in %%file section
- Remove autoconf/automake/pkgconfig(cmocka) from BuildRequires
- Increase release version to 2

* Fri Dec 2 2016 Sun Yunying <yunying.sun@intel.com> - 1.0-1
- Initial version of the package
