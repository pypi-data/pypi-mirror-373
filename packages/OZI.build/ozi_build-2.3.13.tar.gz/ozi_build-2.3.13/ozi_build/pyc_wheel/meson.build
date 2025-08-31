sources = [
    '__init__.py',
    '_pyc_wheel.py',
]
foreach source: sources
    fs.copyfile(source)
    python.install_sources(
        source,
        pure : true,
        subdir : 'ozi_build' / 'pyc_wheel'
    )
endforeach
