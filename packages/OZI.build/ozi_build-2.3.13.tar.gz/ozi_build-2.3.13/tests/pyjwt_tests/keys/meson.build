pyjwt_tests_files_keys = [
    '__init__.py',
    'jwk_ec_key_P-256.json',
    'jwk_ec_key_P-384.json',
    'jwk_ec_key_P-521.json',
    'jwk_ec_key_secp256k1.json',
    'jwk_ec_pub_P-256.json',
    'jwk_ec_pub_P-384.json',
    'jwk_ec_pub_P-521.json',
    'jwk_ec_pub_secp256k1.json',
    'jwk_empty.json',
    'jwk_hmac.json',
    'jwk_keyset_only_unknown_alg.json',
    'jwk_keyset_with_unknown_alg.json',
    'jwk_okp_key_Ed448.json',
    'jwk_okp_key_Ed25519.json',
    'jwk_okp_pub_Ed448.json',
    'jwk_okp_pub_Ed25519.json',
    'jwk_rsa_key.json',
    'jwk_rsa_pub.json',
    'testkey_ec_secp192r1.priv',
    'testkey_ec_ssh.pub',
    'testkey_ec.priv',
    'testkey_ec.pub',
    'testkey_ed25519',
    'testkey_ed25519.pub',
    'testkey_pkcs1.pub.pem',
    'testkey_rsa.cer',
    'testkey_rsa.priv',
    'testkey_rsa.pub',
    'testkey2_rsa.pub.pem',
]
foreach file: pyjwt_tests_files_keys
    if file != 'ozi.phony'
        fs.copyfile(file)
        if not meson.is_subproject() or get_option('install-subprojects').enabled()
            python.install_sources(file, subdir: 'ozi_build' / 'tests' / 'pyjwt_tests')
        endif
    endif
endforeach
