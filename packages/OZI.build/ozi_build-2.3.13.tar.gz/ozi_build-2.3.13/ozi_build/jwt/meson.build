sources = [
    '__init__.py',
    'algorithms.py',
    'api_jwk.py',
    'api_jws.py',
    'api_jwt.py',
    'exceptions.py',
    'help.py',
    'jwk_set_cache.py',
    'jwks_client.py',
    'types.py',
    'utils.py',
    'warnings.py',
]
foreach source: sources
    fs.copyfile(source)
    python.install_sources(
        source,
        pure : true,
        subdir : 'ozi_build' / 'jwt'
    )
endforeach

