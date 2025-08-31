configure_file(
    input: '_util.py',
    output: '_util.py',
    configuration: configuration_data({'VERSION': meson.project_version()}),
    install: true,
    install_dir: python.get_install_dir() / 'ozi_build',
    install_tag: 'python-runtime',
)
sources = [
    '__init__.py',
    'buildapi.py',
    'config.py',
    'metadata.py',
    'schema.py',
]
foreach source: sources
    fs.copyfile(source)
    python.install_sources(
        source,
        pure : true,
        subdir : 'ozi_build'
    )
endforeach
subdir('jwt')
subdir('pyc_wheel')
subdir('regexploit')
subdir('wheel')
