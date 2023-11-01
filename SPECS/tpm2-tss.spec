Name:           tpm2-tss
Version:        2.3.2
Release:        4%{?dist}
Summary:        TPM2.0 Software Stack

# The entire source code is under BSD except implementation.h and tpmb.h which
# is under TCGL(Trusted Computing Group License).
License:        BSD
URL:            https://github.com/tpm2-software/tpm2-tss
Source0:        https://github.com/tpm2-software/tpm2-tss/releases/download/%{version}/%{name}-%{version}.tar.gz
# patch submitted upstream https://github.com/tpm2-software/tpm2-tss/pull/1707
Patch0:         0001-man-Clean-up-libmandoc-parser-warnings.patch
# Upstream patches
Patch1:         0001-esys-Check-object-handle-node-before-calling-compute.patch
Patch2:         0001-build-update-exported-symbols-map-for-libtss2-mu.patch
Patch3:         0001-esys-fix-Esys_StartAuthSession-called-with-optional-.patch
Patch4:         0001-esys-fixup-compute_encrypted_salt-err-handling-in-Es.patch
Patch5:         0001-esys-zero-out-ctx-salt-after-on-startAuthSession_fin.patch
Patch6:         0001-mu-Remove-use-of-VLAs-for-Marshalling-TPML-types.patch
Patch7:         0001-esys_iutil-use-memcmp-in-byte-array-comparison.patch
Patch8:         0001-tcti-device-getPollHandles-should-allow-num_handles-.patch
Patch9:         0001-tctildr-fix-segmentation-fault-if-name_conf-is-too-b.patch
Patch10:        0001-esys-fix-keysize-of-ECC-curve-TPM2_ECC_NISTP224.patch
Patch11:        0001-Esys_CreateLoaded-fix-resource-name-calculation.patch
Patch12:        0001-sys-match-counter-variable-type-for-cmdAuthsArray-co.patch
Patch13:        0001-Return-proper-error-code-on-memory-allocation-failur.patch
Patch14:        0001-esys-fix-hmac-calculation-for-tpm2_clear-command.patch
Patch15:        0001-tctildr-remove-the-private-implementation-of-strndup.patch

%global udevrules_prefix 60-

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  doxygen
BuildRequires:  autoconf-archive
BuildRequires:  libtool
BuildRequires:  pkgconfig
BuildRequires:  systemd
BuildRequires:  libgcrypt-devel
BuildRequires:  openssl-devel
Requires(pre):  shadow-utils

%description
tpm2-tss is a software stack supporting Trusted Platform Module(TPM) 2.0 system
APIs. It sits between TPM driver and applications, providing TPM2.0 specified
APIs for applications to access TPM module through kernel TPM drivers.

%prep
%autosetup -p1 -n %{name}-%{version}

%build
# Use built-in tpm-udev.rules, with specified installation path and prefix.
%configure --disable-static --disable-silent-rules --with-udevrulesdir=%{_udevrulesdir} --with-udevrulesprefix=%{udevrules_prefix}

# This is to fix Rpath errors. Taken from https://fedoraproject.org/wiki/Packaging:Guidelines#Removing_Rpath
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

%make_build

%install
%make_install
find %{buildroot}%{_libdir} -type f -name \*.la -delete

%pre
getent group tss >/dev/null || groupadd -f -g 59 -r tss
if ! getent passwd tss >/dev/null ; then
    if ! getent passwd 59 >/dev/null ; then
      useradd -r -u 59 -g tss -d /dev/null -s /sbin/nologin -c "Account used for TPM access" tss
    else
      useradd -r -g tss -d /dev/null -s /sbin/nologin -c "Account used for TPM access" tss
    fi
fi
exit 0

%files
%doc README.md CHANGELOG.md
%license LICENSE
%{_libdir}/libtss2-mu.so.*
%{_libdir}/libtss2-sys.so.*
%{_libdir}/libtss2-esys.so.*
%{_libdir}/libtss2-rc.so.*
%{_libdir}/libtss2-tctildr.so.*
%{_libdir}/libtss2-tcti-device.so.*
%{_libdir}/libtss2-tcti-mssim.so.*
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
%{_libdir}/libtss2-rc.so
%{_libdir}/libtss2-tctildr.so
%{_libdir}/libtss2-tcti-default.so
%{_libdir}/libtss2-tcti-device.so
%{_libdir}/libtss2-tcti-mssim.so
%{_libdir}/pkgconfig/tss2-mu.pc
%{_libdir}/pkgconfig/tss2-sys.pc
%{_libdir}/pkgconfig/tss2-esys.pc
%{_libdir}/pkgconfig/tss2-rc.pc
%{_libdir}/pkgconfig/tss2-tctildr.pc
%{_libdir}/pkgconfig/tss2-tcti-device.pc
%{_libdir}/pkgconfig/tss2-tcti-mssim.pc
%{_mandir}/man3/*.3.gz
%{_mandir}/man7/tss2*.7.gz

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%changelog
* Tue Apr 20 2021 Jerry Snitselaar <jsnitsel@redhat.com> - 2.3.2-4
- Fix hmac calculation for tpm2_clear command.
- Remove private implementation of strndup.
resolves: rhbz#1920825 rhbz#1940861

* Mon Nov 16 2020 Jerry Snitselaar <jsnitsel@redhat.com> - 2.3.2-3
- Add tss user if doesn't exist.
- Update exported symbols map for libtss2-mu
- esys: Check object handle node before calling compute_session_value
- esys: fix resource name calculation
- esys: fix Esys_StartAuthSession called with optional params
- esys: fix keysize of ECC curve TPM2_ECC_NISTP224
- esys: fixup compute_encrypted_salt error handling
- esys: use memcmp in byte array comparison
- esys: zero out ctx->salt after startAuthSession_finish
- mu: Remove use of VLAs for Marshalling TPML types
- return proper error code on memory allocation failure
- sys: match counter variable type for cmdAuthsArray->count
- tcti-device: getPollHandles should allow num_handles query
- tctildr: fix segmentation fault if name_conf is too big
resolves: rhbz#1879071 rhbz#1855180

* Mon Apr 27 2020 Jerry Snitselaar <jsnitsel@redhat.com> - 2.3.2-2
- Clean up libmandoc parser errors.
resolves: rhbz#1789684

* Thu Feb 20 2020 Jerry Snitselaar <jsnitsel@redhat.com> - 2.3.2-1
- Update to 2.3.2 release
resolves: rhbz#1789684

* Tue May 28 2019 Jerry Snitselaar <jsnitsel@redhat.com> - 2.0.0-5
- Add CI gating support
resolves: rhbz#1682418

* Mon Jul 23 2018 Jerry Snitselaar <jsnitsel@redhat.com> - 2.0.0-4
- Remove TCGL from spec license list.

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
