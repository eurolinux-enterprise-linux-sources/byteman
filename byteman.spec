%global homedir %{_datadir}/%{name}
%global bindir %{homedir}/bin
%global hash 373601b4e608ea622b2fec947824b99cd0edb124
%global __requires_exclude ^mvn\(.*\)$

Name:             byteman
Version:          2.1.4.1
Release:          3%{?dist}
Summary:          Java agent-based bytecode injection tool
License:          LGPLv2+
URL:              http://www.jboss.org/byteman
Source0:          https://github.com/bytemanproject/byteman/archive/%{hash}.tar.gz

BuildArch:        noarch

BuildRequires:    jpackage-utils
BuildRequires:    javapackages-tools
BuildRequires:    java-devel
BuildRequires:    maven-local
BuildRequires:    maven-shade-plugin
BuildRequires:    maven-failsafe-plugin
BuildRequires:    maven-jar-plugin
BuildRequires:    maven-surefire-plugin
BuildRequires:    maven-surefire-provider-testng
BuildRequires:    maven-surefire-provider-junit4
BuildRequires:    maven-verifier-plugin
BuildRequires:    java_cup
BuildRequires:    jarjar
BuildRequires:    objectweb-asm
BuildRequires:    junit4
BuildRequires:    testng

Requires:         jpackage-utils
Requires:         java-devel

# Bundled at build time
Provides:         bundled(java_cup) = 1:0.11a-16
Provides:         bundled(objectweb-asm) = 0:3.3.1-9

%description
Byteman is a tool which simplifies tracing and testing of Java programs.
Byteman allows you to insert extra Java code into your application,
either as it is loaded during JVM startup or even after it has already
started running. The injected code is allowed to access any of your data
and call any application methods, including where they are private.
You can inject code almost anywhere you want and there is no need to
prepare the original source code in advance nor do you have to recompile,
repackage or redeploy your application. In fact you can remove injected
code and reinstall different code while the application continues to execute.

%package javadoc
Summary:          Javadocs for %{name}

%description javadoc
This package contains the API documentation for %{name}.

%prep
%setup -q -n byteman-%{hash}

# Fix the gid:aid for java_cup
sed -i "s|net.sf.squirrel-sql.thirdparty-non-maven|java_cup|" agent/pom.xml
sed -i "s|java-cup|java_cup|" agent/pom.xml

# com.sun:tools dependency has scope "system", which should not used
# in RHEL.
%pom_remove_dep com.sun:tools

%pom_xpath_inject  "pom:plugin[pom:artifactId = 'maven-javadoc-plugin']/pom:configuration" "<additionalparam>\${doclintparam}</additionalparam>"
%pom_xpath_inject  "pom:profiles" "<profile>
        <id>disable-java-8-doclint</id>
        <activation>
            <jdk>[1.8,)</jdk>
        </activation>
        <properties>
            <doclintparam>-Xdoclint:none</doclintparam>
        </properties>
      </profile>"

%build
%mvn_build

%install
%mvn_install

install -d -m 755 $RPM_BUILD_ROOT%{_bindir}

install -d -m 755 $RPM_BUILD_ROOT%{homedir}
install -d -m 755 $RPM_BUILD_ROOT%{homedir}/lib
install -d -m 755 $RPM_BUILD_ROOT%{bindir}

install -m 755 bin/bmsubmit.sh $RPM_BUILD_ROOT%{bindir}/bmsubmit
install -m 755 bin/bminstall.sh  $RPM_BUILD_ROOT%{bindir}/bminstall
install -m 755 bin/bmjava.sh  $RPM_BUILD_ROOT%{bindir}/bmjava
install -m 755 bin/bmcheck.sh  $RPM_BUILD_ROOT%{bindir}/bmcheck

for f in bmsubmit bmjava bminstall bmcheck; do
cat > $RPM_BUILD_ROOT%{_bindir}/${f} << EOF
#!/bin/sh

export BYTEMAN_HOME=/usr/share/byteman
export JAVA_HOME=/usr/lib/jvm/java

\$BYTEMAN_HOME/bin/${f} \$*
EOF
done

chmod 755 $RPM_BUILD_ROOT%{_bindir}/*

for m in bmunit dtest install sample submit; do
  ln -s %{_javadir}/byteman/byteman-${m}.jar $RPM_BUILD_ROOT%{homedir}/lib/byteman-${m}.jar
done

ln -s %{_javadir}/byteman/byteman.jar $RPM_BUILD_ROOT%{homedir}/lib/byteman.jar

%files -f .mfiles
%dir %{_javadir}/%{name}
%{homedir}/*
%{_bindir}/*
%doc README docs/ProgrammersGuide.pdf docs/copyright.txt

%files javadoc -f .mfiles-javadoc
%doc docs/copyright.txt

%changelog
* Mon Jul 02 2018 Severin Gehwolf <sgehwolf@redhat.com> - 2.1.4.1-3
- Allow rebuild with JDK-8.

* Wed Jun 06 2018 Severin Gehwolf <sgehwolf@redhat.com> - 2.1.4.1-2
- Don't filter provides. Update bundled java_cup and
  asm versions.

* Wed May 30 2018 Severin Gehwolf <sgehwolf@redhat.com> - 2.1.4.1-1
- Rebase to version 2.1.4.1. Resolves RHBZ#1408898.

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 2.0.4-5
- Mass rebuild 2013-12-27

* Wed Nov 13 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.0.4-4
- Remove system-scoped dependency on tools.jar

* Thu Apr 25 2013 Marek Goldmann <mgoldman@redhat.com> - 2.0.4-3
- Fixes to the launch scripts

* Wed Apr 24 2013 Marek Goldmann <mgoldman@redhat.com> - 2.0.4-2
- Added bmsubmit, bminstall and bmjava scripts, RHBZ#951560

* Thu Feb 21 2013 Marek Goldmann <mgoldman@redhat.com> - 2.0.4-1
- Upstream release 2.0.4
- Switched to Maven
- Bundling java_cup and objectweb-asm (fpc#226)

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.2-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.2-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Sep 20 2011 Marek Goldmann <mgoldman@redhat.com> 1.5.2-3
- Removed binary files from src.rpm

* Mon Sep 19 2011 Marek Goldmann <mgoldman@redhat.com> 1.5.2-2
- Cleaned spec file

* Wed Jul 27 2011 Marek Goldmann <mgoldman@redhat.com> 1.5.2-1
- Upstream release: 1.5.2

* Thu Jul 21 2011 Marek Goldmann <mgoldman@redhat.com> 1.5.1-1
- Initial packaging

