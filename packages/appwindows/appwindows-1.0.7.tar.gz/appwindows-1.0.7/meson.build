project('appwindows', 'cpp',
        license : 'BSD 3-Clause License',
        meson_version : '>=0.56.0',
        default_options : [
            'cpp_std=c++17',
            'buildtype=release',
            'default_library=shared',
            'b_ndebug=if-release',
        ]
)

pybind11_dep = dependency('pybind11', required : true)
python_dep = dependency('python3', required : true)

py3 = import('python').find_installation('python3', pure : false)

python_install_dir = py3.get_install_dir()

appwindows_inc = include_directories('src/appwindows',
                                     'src/appwindows/core')
geometry_inc = include_directories('src/appwindows/core/geometry')
exceptions_inc = include_directories('src/appwindows/core/exceptions')


appwindows_sources = files(
    'src/appwindows/appwindows.cc',
    'src/appwindows/core/bind.cc',
    'src/appwindows/core/platform.cc',
    'src/appwindows/core/geometry/size.cc',
    'src/appwindows/core/geometry/point.cc',
)
geometry_sources = files(
    'src/appwindows/core/geometry/point.cc',
    'src/appwindows/core/geometry/size.cc',
    'src/appwindows/core/geometry/geometry.cc'
)
exceptions_sources = files('src/appwindows/core/exceptions/exceptions.cc')

platform_deps = []
platform_args = []

if host_machine.system() == 'windows'
    appwindows_sources += files(
        'src/appwindows/windows/window.getters.cc',
        'src/appwindows/windows/window.setters.cc',
        'src/appwindows/windows/finder.cc'
    )
    appwindows_inc = [appwindows_inc, include_directories('src/appwindows/windows')]
    platform_args = ['-DWINDOWS_USED=1']

elif host_machine.system() == 'linux'
    xdg_session_type = run_command('sh', '-c', 'loginctl show-session $(loginctl | grep $(whoami) | awk "{print $1}") -p Type', check: false)
    session_type = xdg_session_type.stdout().strip()
    message('!!!!!!!!!!!!!!!!!!!!!!!!!!')
    message(session_type)
    message('!!!!!!!!!!!!!!!!!!!!!!!!!!')
    if session_type == 'Type=wayland'
        wayland_dep = dependency('wayland-client', required : true)
        wayland_dep.found()
        appwindows_sources += files(
            'src/appwindows/wayland/window.getters.cc',
            'src/appwindows/wayland/window.setters.cc',
            'src/appwindows/wayland/finder.cc'
        )
        appwindows_inc = [appwindows_inc, include_directories('src/appwindows/wayland')]
        platform_deps += wayland_dep
        platform_args += ['-DWAYLAND_USED=1']
    elif session_type == 'Type=x11'
        x11_dep = dependency('x11', required : true)
        xext_dep = dependency('xext', required : false)
        xfixes_dep = dependency('xfixes', required : false)
        xinerama_dep = dependency('xinerama', required : false)
        x11_dep.found()
        xext_dep.found()
        xfixes_dep.found()
        xinerama_dep.found()
        appwindows_sources += files(
            'src/appwindows/x_server/window.getters.cc',
            'src/appwindows/x_server/window.setters.cc',
            'src/appwindows/x_server/finder.cc'
        )
        appwindows_inc = [appwindows_inc, include_directories('src/appwindows/x_server')]
        platform_deps += [x11_dep, xext_dep, xfixes_dep, xinerama_dep]
        platform_args += ['-DX_SERVER_USED=1']
    else
        warning('Neither Wayland nor X11 found, building without platform-specific features')
    endif

else
    error('Unsupported platform: ' + host_machine.system())
endif



appwindows_mod = py3.extension_module('appwindows',
                                      sources : appwindows_sources,
                                      dependencies : [pybind11_dep, platform_deps],
                                      include_directories : [appwindows_inc, exceptions_inc, geometry_inc],
                                      install : true,
                                      cpp_args : platform_args,
                                      subdir : 'appwindows')

geometry_mod = py3.extension_module('geometry',
                                    sources : geometry_sources,
                                    dependencies : [pybind11_dep],
                                    include_directories : geometry_inc,
                                    install : true,
                                    subdir : 'appwindows')

exceptions_mod = py3.extension_module('exceptions',
                                      sources : exceptions_sources,
                                      dependencies : [pybind11_dep],
                                      include_directories : exceptions_inc,
                                      install : true,
                                      subdir : 'appwindows')

configure_file(
    input : '__init__.py',
    output : '__init__.py',
    copy : true
)

install_data(
    '__init__.py',
    install_dir : python_install_dir / 'appwindows'
)