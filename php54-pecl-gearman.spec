%{!?__pecl: %{expand: %%global __pecl %{_bindir}/pecl}}

%global php_zendabiver %((echo 0; php -i 2>/dev/null | sed -n 's/^PHP Extension => //p') | tail -1)
%global php_version %((echo 0; php-config --version 2>/dev/null) | tail -1)
%global basepkg   php54w
%global pecl_name gearman

%global extver 1.1.2
%global libver 1.1.0

# Build ZTS extension or only NTS
%global with_zts      1

Summary:       PHP wrapper to libgearman
Name:          %{basepkg}-pecl-%{pecl_name}
Version:       %{extver}
Release:       2%{?dist}
License:       PHP
Group:         Development/Languages
URL:           http://pecl.php.net/package/%{pecl_name}
Source:        http://pecl.php.net/get/%{pecl_name}-%{version}.tgz
BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires: %{basepkg}-devel >= 5.1.0, %{basepkg}-pear
BuildRequires:  libgearman-devel > %{libver}
Requires(post): %{__pecl}
Requires(postun): %{__pecl}
%if %{?php_zend_api}0
# Require clean ABI/API versions if available (Fedora)
Requires:      php(zend-abi) = %{php_zend_api}
Requires:      php(api) = %{php_core_api}
%else
%if "%{rhel}" == "5"
# RHEL5 where we have php-common providing the Zend ABI the "old way"
Requires:      php-zend-abi = %{php_zendabiver}
%else
# RHEL4 where we have no php-common and nothing providing the Zend ABI...
Requires:      php = %{php_version}
%endif
%endif
Provides:      php-pecl(%{pecl_name}) = %{version}
Provides:      php-pecl(%{pecl_name})%{?_isa} = %{version}

Requires(post): %{__pecl}
Requires(postun): %{__pecl}

%if 0%{?fedora} < 20 && 0%{?rhel} < 7
# Filter private shared
%{?filter_provides_in: %filter_provides_in %{_libdir}/.*\.so$}
%{?filter_setup}
%endif

%description
This extension uses libgearman library to provide API for
communicating with gearmand, and writing clients and workers

Documentation: http://php.net/%{pecl_name}

%prep
%setup -q -c

%if %{with_zts}
cp -r %{pecl_name}-%{version} %{pecl_name}-%{version}-zts
%endif

%build
pushd %{pecl_name}-%{version}
%{_bindir}/phpize
%configure --with-php-config=%{_bindir}/php-config
%{__make} %{?_smp_mflags}
popd

%if %{with_zts}
pushd %{pecl_name}-%{version}-zts
%{_bindir}/zts-phpize
%configure --with-php-config=%{_bindir}/zts-php-config
%{__make} %{?_smp_mflags}
popd
%endif

%install
%{__rm} -rf %{buildroot}

pushd %{pecl_name}-%{version}
%{__make} install INSTALL_ROOT=%{buildroot}

popd

%if %{with_zts}
pushd %{pecl_name}-%{version}-zts
%{__make} install INSTALL_ROOT=%{buildroot}
popd

%endif

# Install the package XML file
%{__mkdir_p} %{buildroot}%{pecl_xmldir}
%{__install} -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml

# Drop in the bit of configuration
%{__mkdir_p} %{buildroot}%{php_inidir}
%{__cat} > %{buildroot}%{php_inidir}/%{pecl_name}.ini << 'EOF'
; Enable %{pecl_name} extension module
extension = %{pecl_name}.so
EOF

%if %{with_zts}
%{__mkdir_p} %{buildroot}%{php_ztsinidir}
%{__cp} %{buildroot}%{php_inidir}/%{pecl_name}.ini %{buildroot}%{php_ztsinidir}/%{pecl_name}.ini
%endif

%check
pushd %{pecl_name}-%{version}
TEST_PHP_EXECUTABLE=$(which php) php run-tests.php \
    -n -q -d extension_dir=modules \
    -d extension=%{pecl_name}.so
popd

%if %{with_zts}
pushd %{pecl_name}-%{version}-zts
TEST_PHP_EXECUTABLE=$(which zts-php) zts-php run-tests.php \
    -n -q -d extension_dir=modules \
    -d extension=%{pecl_name}.so
popd
%endif


%if 0%{?pecl_install:1}
%post
%{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :
%endif


%if 0%{?pecl_uninstall:1}
%postun
if [ $1 -eq 0 ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi
%endif


%clean
%{__rm} -rf %{buildroot}


%files
%defattr(-, root, root, 0755)
%doc %{pecl_name}-%{version}/{CREDITS,LICENSE,README}
%config(noreplace) %{php_inidir}/%{pecl_name}.ini
%{php_extdir}/%{pecl_name}.so
%{pecl_xmldir}/%{name}.xml

%if %{with_zts}
%config(noreplace) %{php_ztsinidir}/%{pecl_name}.ini
%{php_ztsextdir}/%{pecl_name}.so
%endif

%changelog
* Sun Sep 14 2014 Andy Thompson <andy@webtatic.com> - 1.1.2-2
- Filter .so provides < EL7

* Sat Jun 21 2014 Andy Thompson <andy@webtatic.com> - 1.1.2-1
- Add pecl spec for gearman extension version 1.1.2
