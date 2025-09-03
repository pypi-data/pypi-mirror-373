
import os
import shutil
import sys

import numpy as np

def prepare():
    target_dir = "./"
    extern_target = f"{target_dir}/extern/build"
    # HACK: create a shim python entry in extern_target/bin so that Karabo
    # will not build its own Python environment. Similarly, link conan
    os.makedirs(f"{extern_target}/bin/", exist_ok=True)
    bin_path, _ = sys.executable.rsplit("/", 1)
    if os.path.exists(f"{extern_target}/bin/python"):
        os.remove(f"{extern_target}/bin/python")
    os.symlink(sys.executable, f"{extern_target}/bin/python")
    if os.path.exists(f"{extern_target}/bin/conan"):
        os.remove(f"{extern_target}/bin/conan")
    os.symlink(f"{bin_path}/conan", f"{extern_target}/bin/conan")

    # HACK: we don't need relocatable libs here
    with open(f"{target_dir}/extern/relocate_deps.sh", "w") as f:
        f.write('echo "Not relocating dependencies!"\n')

    # HACK(ish): reduce the number of dependencies to the bare minimum
    shutil.copyfile(f"{target_dir}/mod_extern_conanfile.txt", f"{target_dir}/extern/conanfile.txt")
    
    # HACK(ish): we need to more explicityl configure our tool chain
    # in the karabo profile file for it to work with manylinux
    with open(f"{target_dir}/extern/conanprofile.karabo", "r") as f:
        profile_contents = f.read()

    # HACK: this is to prevent needing to go to ManyLinux_2_34 because
    # of b2 > 5.2.0 requiring a newer GLIBC than ManyLinux_2_28 provides.
    # We currently avoid the newer ManyLinux flavor as it will lead
    # to auditwheel problems as a result of the X64_V2 architecture being
    # used as default compilation target on AlmaLinux9. There's an active
    # debate on how to resolve this:
    #
    # https://github.com/pypa/manylinux/issues/1725
    #
    # and for now we take the time to see where the community goes.
    profile_contents = profile_contents.replace(
        "b2/5.3.2",
        "b2/5.2.0"
    )

    # The CMake 4.0.1 version from the framework does not have an aarch64
    # package in place
    profile_contents = profile_contents.replace(
        "cmake/4.0.1",
        "cmake/4.0.3"
    )

    with open(f"{target_dir}/extern/conanprofile.karabo", "w") as f:
        f.write(profile_contents)

    # HACK(ish): modify a few things in the build script to ensure
    # 1) there's a steady output stream, and the pip to the container
    #    doesn't time out in cibuildwheel
    # 2) conan picks up the correct build profile
    with open(f"{target_dir}/extern/build.sh", "r") as f:
        build_contents = f.read()

    # we actually want to see outputs here
    # a) for debugging
    # b) so that cibuildwheel does not time out on its output pipe
    build_contents = build_contents.replace(
        'safeRunCommandQuiet "$INSTALL_PREFIX/bin/conan',
        'safeRunCommand "$INSTALL_PREFIX/bin/conan')

    build_contents = build_contents.replace(
        'local profile_opts="-pr:h=./conanprofile.karabo"',
        'local profile_opts="-pr:b=default -pr:h=./conanprofile.karabo"')
    
    with open(f"{target_dir}/extern/build.sh", "w") as f:
        f.write(build_contents)

    # fix-in python and numpy paths for cmak
    with open(f"{target_dir}/pyproject.toml", "r") as f:
        pyproject = f.read()

    # we do simple replacements here, as to not have to install jinja2 just
    # for this. Formatting codes won't work, as {...} is a valid syntactic
    # structure in a TOML file, and would lead to conflicts.
    pyproject = pyproject.replace("{{ python_root_prefix }}", sys.base_prefix)
    pyproject = pyproject.replace("{{ python_executable }}", sys.executable)
    pyproject = pyproject.replace("{{ numpy_incude_dir }}", np.get_include())
   
    with open(f"{target_dir}/pyproject.toml", "w") as f:
        f.write(pyproject)

    # HACK(ish): manylinux builds should not link against libpython.so
    # Accordingly, the reference package does not expose the library,
    # and thus
    # find_package(
    #    Python3 3.12 EXACT REQUIRED
    #    COMPONENTS Interpreter Development NumPy
    # )
    # will fail because of `Development`
    # We don't actually need it for compiling and thus remove it
    
    with open(f"{target_dir}/src/karabind/CMakeLists.txt", "r") as f:
        karabind_cmake = f.read()

    karabind_cmake = karabind_cmake.replace(
        "COMPONENTS Interpreter Development NumPy",
        "COMPONENTS Interpreter NumPy")
    
    with open(f"{target_dir}/src/karabind/CMakeLists.txt", "w") as f:
        f.write(karabind_cmake)

    print("Prepared extern dir!")