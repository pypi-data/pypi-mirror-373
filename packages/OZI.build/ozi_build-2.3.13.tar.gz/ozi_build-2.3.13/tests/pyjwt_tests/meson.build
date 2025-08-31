pyjwt_tests_files = [
    '__init__.py',
    'test_advisory.py',
    'test_algorithms.py',
    'test_api_jwk.py',
    'test_api_jws.py',
    'test_api_jwt.py',
    'test_compressed_jwt.py',
    'test_exceptions.py',
    'test_jwks_client.py',
    'test_jwt.py',
    'test_utils.py',
    'utils.py',
]
foreach file: pyjwt_tests_files
    if file != 'ozi.phony'
        fs.copyfile(file)
        if not meson.is_subproject() or get_option('install-subprojects').enabled()
            python.install_sources(file, subdir: 'ozi_build' / 'tests' / 'pyjwt_tests')
        endif
    endif
endforeach
subdir('keys')