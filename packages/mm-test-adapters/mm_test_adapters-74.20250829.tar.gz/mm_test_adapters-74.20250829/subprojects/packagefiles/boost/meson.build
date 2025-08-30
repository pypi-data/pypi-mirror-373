project('boost', 'cpp', version: '1.83.0', license: 'Boost')

# Use relative path for include directories.
boost_inc = include_directories('.')

# Declare dependency with both libraries.
boost_dep = declare_dependency(include_directories: boost_inc)

meson.override_dependency('boost', boost_dep)
