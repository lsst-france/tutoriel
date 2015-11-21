# -*- python -*-

import os
import sys
import subprocess

def run(cmd):
    print "running:"
    print cmd
    print "--------------"
    theproc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out = theproc.stdout.read()
    theproc.stdout.close()
    return out

def build_package(home, package, dep='', lib=False):
    if os.path.exists(home + '/' + package):
        import shutil
        shutil.rmtree(home + '/' + package)
    os.mkdir(home + '/' + package)

    for b in ('include', 'src', 'lib', 'tests', 'ups'):
        os.mkdir(home + '/' + package + '/' + b)

    with open(home + '/' + package + '/SConstruct', 'w') as f:
        f.write('''# -*- python -*-
from lsst.sconsUtils import scripts
scripts.BasicSConstruct("%s")
''' % package)

    with open(home + '/' + package + '/ups/%s.build' % package, 'w') as f:
        f.write('''@LSST BUILD@
build_lsst @PRODUCT@ @VERSION@ @REPOVERSION@

''')

    required = ""
    if dep != "":
        required = '"%s"' % dep

    with open(home + '/' + package + '/ups/%s.cfg' % package, 'w') as f:
        f.write('''# -*- python -*-

import lsst.sconsUtils

# Dependencies that provide heard files and or libraries should be included here.
# Pure-Python dependencies do not need to be included.
# Packages that use swig or boost_tests should declare them as build dependencies.
# Otherwise, the rules for which packages to list here are the same as those for
# table files.

dependencies = {
    "required": [%s],
}

# For packages that build a C++ library and a SWIG module, the below should be sufficient.
# Pure-Python packages should set headers=[], libs=[] (not libs=None). and hasSwigFiles=False.
# For more information, see the sconsUtils Doxygen documentation.
config = lsst.sconsUtils.Configuration(
    __file__,
    hasDoxygenInclude=False,
    hasSwigFiles=False,
)

''' % required)

    required = ''
    if dep != '':
        required = 'setupRequired(%s)' % dep

    with open(home + '/' + package + '/ups/%s.table' % package, 'w') as f:
        f.write('''%s

envPrepend(LD_LIBRARY_PATH, ${PRODUCT_DIR}/lib)
envPrepend(DYLD_LIBRARY_PATH, ${PRODUCT_DIR}/lib)
envPrepend(PYTHONPATH, ${PRODUCT_DIR}/python)
envAppend(PATH, ${PRODUCT_DIR}/bin)

''' % required)

    with open(home + '/' + package + '/tests/SConscript', 'w') as f:
        f.write('''# -*- python -*-
from lsst.sconsUtils import scripts
scripts.BasicSConscript.tests()

''')

    decl = ''
    call = ''

    if dep != '':
        decl = 'void a();'
        call = '  a();'

    with open(home + '/' + package + '/tests/hello.cc', 'w') as f:
        f.write('''#include <iostream>

%s

int main ()
{
  std::cout << "hello world" << std::endl;
  %s
}   

''' % (decl, call))

    if lib:
        with open(home + '/' + package + '/lib/a.cc', 'w') as f:
            f.write('''#include <iostream>

void a ()
{
  std::cout << "a" << std::endl;
}

''')

    with open(home + '/' + package + '/lib/SConscript', 'w') as f:
        f.write('''# -*- python -*-
from lsst.sconsUtils import scripts, targets, env

objs = env.SourcesForSharedLibrary(Glob("#lib/*.cc"))

targets["lib"].extend(env.SharedLibrary(env["packageName"], objs, LIBS=env.getLibs("self")))

''')

def declare(home, package, version):
    print run('''
source %(stack)s/loadLSST.bash;
echo "======= eups path"
export EUPS_PATH=%(home)s:$EUPS_PATH;
eups path;
eups declare --nolocks -v -F -r %(home)s/%(package)s %(package)s %(version)s;
eups list -D %(package)s;
pwd''' % {'stack':stack, 'home':home, 'package':package, 'version':version})

def undeclare(home, package, version):
    print run('''
source %(stack)s/loadLSST.bash;
export EUPS_PATH=%(home)s:$EUPS_PATH;
unsetup $(package)s;
eups undeclare --nolocks -F %(package)s %(version)s;
echo "======= end";
pwd''' % {'stack':stack, 'home':home, 'package':package, 'version':version})


def make_package(home, package, version, dep=""):
    if dep != "":
        dep = "setup %s;" % dep

    print run('''
source %(stack)s/loadLSST.bash;
export EUPS_PATH=%(home)s:$EUPS_PATH;
eups path;
%(dep)s
setup %(package)s;
cd %(package)s;
scons;
tests/hello;
''' % {'stack':stack, 'home':home, 'package':package, 'version':version, 'dep':dep})



if __name__ == '__main__':

    stack = '/sps/lsst/Library/stack_v11_0'
    home = '/sps/lsst/dev/carnault'
    package = 'my_pack'
    version = '1.0'

    build_package(home, 'my_lib', lib=True)
    build_package(home, 'my_pack', dep='my_lib')

    declare(home, 'my_lib', '1.0')
    declare(home, 'my_pack', '1.0')

    make_package(home, 'my_lib', '1.0')
    make_package(home, 'my_pack', '1.0', dep='my_lib')

    undeclare(home, 'my_lib', '1.0')
    undeclare(home, 'my_pack', '1.0')


