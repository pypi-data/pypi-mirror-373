sources = [
    '__init__.py',
    'pep425tags.py',
    'wheelfile.py',
]
foreach source: sources
    fs.copyfile(source)
    python.install_sources(
        source,
        pure : true,
        subdir : 'ozi_build' / 'wheel'
    )
endforeach
