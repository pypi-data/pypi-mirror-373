import os
from pathlib import Path
from click.testing import CliRunner
from gdcmd.cli import cli
from gdcmd.secrets import rsa_generate, hybrid_encrypt, hybrid_decrypt, get_repository_path


def test_encryption_decryption():
    private_key, public_key = rsa_generate()

    original_text = "Hello, GridDot!"
    encrypted_text = hybrid_encrypt(public_key, original_text.encode('utf-8'))
    assert encrypted_text != original_text  # Ensure encryption changed the text

    decrypted_bytes = hybrid_decrypt(private_key, encrypted_text)
    assert isinstance(decrypted_bytes, bytes)
    assert decrypted_bytes == original_text.encode('utf-8')


def test_cli_encrypt():
    runner = CliRunner()
    result = runner.invoke(cli, [
        'secrets',
        'encrypt'
    ])

    assert result.exit_code == 0, result.output


def test_cli():
    runner = CliRunner()

    try:
        for file in [p for p in Path(get_repository_path()).rglob("*") if p.is_file() and ".git" not in p.parts]:
            if file.name.endswith('.encrypted'):
                os.rename(file, file.with_suffix('.bak-encrypted-file-test'))

        # Generate keys
        result = runner.invoke(cli, [
            'secrets',
            'create'
        ])

        assert result.exit_code == 0, result.output

        # Test encryption
        with open('file1.txt', 'w') as f:
            f.write('This is a secret file 1.')

        with open('file2.txt', 'w') as f:
            f.write('This is a secret file 2.')

        file1_abs_path = os.path.abspath('file1.txt')
        file2_abs_path = os.path.abspath('file2.txt')

        result = runner.invoke(cli, [
            'secrets',
            'encrypt',
            '-f', file1_abs_path,
            '--file', file2_abs_path
        ])

        assert result.exit_code == 0, result.output

        # Test decryption
        result = runner.invoke(cli, [
            'secrets',
            'decrypt',
            '-f', file1_abs_path + '.encrypted',
            '--file', file2_abs_path + '.encrypted'
        ])

        assert result.exit_code == 0, result.output

        with open('file1.txt.encrypted', 'r') as f:
            encrypted_content1 = f.read()

        with open('file2.txt.encrypted', 'r') as f:
            encrypted_content2 = f.read()

        assert encrypted_content1 != 'This is a secret file 1.'
        assert encrypted_content2 != 'This is a secret file 2.'

        # Test decryption without specifying files
        os.remove('file1.txt')
        os.remove('file2.txt')

        result = runner.invoke(cli, [
            'secrets',
            'decrypt',
        ])

        assert result.exit_code == 0, result.output

        with open('file1.txt', 'r') as f:
            decrypted_content1 = f.read()
        with open('file2.txt', 'r') as f:
            decrypted_content2 = f.read()

        assert decrypted_content1 == 'This is a secret file 1.'
        assert decrypted_content2 == 'This is a secret file 2.'

        # Test encryption without specifying files
        with open('file1.txt.encrypted', 'w') as f:
            f.write('')
        with open('file2.txt.encrypted', 'w') as f:
            f.write('')

        result = runner.invoke(cli, [
            'secrets',
            'encrypt',
        ])

        assert result.exit_code == 0, result.output

        result = runner.invoke(cli, [
            'secrets',
            'decrypt',
        ])

        assert result.exit_code == 0, result.output

        with open('file1.txt', 'w') as f:
            f.write('This is a secret file 1.')
        with open('file2.txt', 'w') as f:
            f.write('This is a secret file 2.')

        os.remove('file1.txt')
        os.remove('file2.txt')
        os.remove('file1.txt.encrypted')
        os.remove('file2.txt.encrypted')
    finally:
        # After test rename all files which end with .encrypted.bak to .encrypted
        for file in [p for p in Path(get_repository_path()).rglob("*") if p.is_file() and ".git" not in p.parts]:
            if file.name.endswith('.bak-encrypted-file-test'):
                os.rename(file, file.with_suffix('.encrypted'))
