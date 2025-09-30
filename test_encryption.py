#!/usr/bin/env python3
"""
Testes automatizados para o serviço de criptografia AES-256-GCM
"""

import unittest
import json
import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from encryption_service import EncryptionService

class TestEncryptionService(unittest.TestCase):
    """Testes para o serviço de criptografia"""

    def setUp(self):
        """Configuração inicial dos testes"""
        # Dados de teste
        self.test_data = "Dados sensíveis de teste para criptografia AES-256-GCM"
        self.context = "test_context"

        # Configurar chave mestra para testes
        os.environ['ALPHACLINIC_ENCRYPTION_KEY'] = 'test-master-key-for-unit-tests-32-chars'

    def test_encrypt_decrypt_basic(self):
        """Teste básico de criptografia e descriptografia"""
        # Criptografar
        encrypted = EncryptionService.encrypt_data(self.test_data, self.context)

        # Verificar que o resultado é um JSON válido
        encrypted_obj = json.loads(encrypted)
        self.assertIn('version', encrypted_obj)
        self.assertIn('salt', encrypted_obj)
        self.assertIn('iv', encrypted_obj)
        self.assertIn('ciphertext', encrypted_obj)
        self.assertEqual(encrypted_obj['version'], 'AES-256-GCM-1.0')

        # Descriptografar
        decrypted = EncryptionService.decrypt_data(encrypted, self.context)

        # Verificar que os dados são idênticos
        self.assertEqual(decrypted, self.test_data)

    def test_encrypt_decrypt_empty_string(self):
        """Teste com string vazia"""
        test_data = ""

        encrypted = EncryptionService.encrypt_data(test_data, self.context)
        decrypted = EncryptionService.decrypt_data(encrypted, self.context)

        self.assertEqual(decrypted, test_data)

    def test_encrypt_decrypt_special_characters(self):
        """Teste com caracteres especiais"""
        test_data = "Teste com ção, áéíóú, 日本語, русский, 🚀, ñoño"

        encrypted = EncryptionService.encrypt_data(test_data, self.context)
        decrypted = EncryptionService.decrypt_data(encrypted, self.context)

        self.assertEqual(decrypted, test_data)

    def test_encrypt_different_keys_same_data(self):
        """Teste que dados iguais com chaves diferentes produzem criptografias diferentes"""
        encrypted1 = EncryptionService.encrypt_data(self.test_data, self.context)
        encrypted2 = EncryptionService.encrypt_data(self.test_data, self.context)

        # Devem ser diferentes (devido a IVs e salts únicos)
        self.assertNotEqual(encrypted1, encrypted2)

        # Mas descriptografar deve dar o mesmo resultado
        decrypted1 = EncryptionService.decrypt_data(encrypted1, self.context)
        decrypted2 = EncryptionService.decrypt_data(encrypted2, self.context)

        self.assertEqual(decrypted1, self.test_data)
        self.assertEqual(decrypted2, self.test_data)

    def test_key_derivation(self):
        """Teste da derivação de chaves"""
        password = b"test-password"
        salt = b"test-salt-123456789"

        key1, salt1 = EncryptionService.derive_key(password, salt)
        key2, salt2 = EncryptionService.derive_key(password, salt)

        # Mesmo password e salt devem gerar mesma chave
        self.assertEqual(key1, key2)
        self.assertEqual(salt1, salt2)

        # Salt diferente deve gerar chave diferente
        key3, _ = EncryptionService.derive_key(password, b"different-salt-123")
        self.assertNotEqual(key1, key3)

    def test_rsa_key_generation(self):
        """Teste de geração de par de chaves RSA"""
        key_pair = EncryptionService.generate_key_pair()

        self.assertIn('private_key', key_pair)
        self.assertIn('public_key', key_pair)
        self.assertIn('key_size', key_pair)
        self.assertIn('algorithm', key_pair)

        self.assertEqual(key_pair['key_size'], 2048)
        self.assertEqual(key_pair['algorithm'], 'RSA-2048')

        # Verificar formato PEM
        self.assertIn('-----BEGIN PRIVATE KEY-----', key_pair['private_key'])
        self.assertIn('-----BEGIN PUBLIC KEY-----', key_pair['public_key'])

    def test_rsa_sign_and_verify(self):
        """Teste de assinatura e verificação RSA"""
        # Gerar par de chaves
        key_pair = EncryptionService.generate_key_pair()

        # Assinar dados
        signature = EncryptionService.sign_data(self.test_data, key_pair['private_key'])

        # Verificar assinatura
        is_valid = EncryptionService.verify_signature(
            self.test_data,
            signature,
            key_pair['public_key']
        )

        self.assertTrue(is_valid)

        # Verificar que assinatura de dados diferentes falha
        is_valid_wrong = EncryptionService.verify_signature(
            "Dados diferentes",
            signature,
            key_pair['public_key']
        )

        self.assertFalse(is_valid_wrong)

    def test_invalid_encrypted_data(self):
        """Teste com dados criptografados inválidos"""
        with self.assertRaises((json.JSONDecodeError, ValueError, Exception)):
            EncryptionService.decrypt_data("dados_inválidos", self.context)

    def test_master_key_configuration(self):
        """Teste de configuração da chave mestra"""
        # Deve funcionar com chave de teste
        key = EncryptionService.get_master_key()
        self.assertIsInstance(key, bytes)
        self.assertEqual(len(key), 39)  # Tamanho da chave de teste

    def test_encryption_context_logging(self):
        """Teste que contexto é usado para auditoria"""
        # Este teste verifica que não há erros quando contexto é fornecido
        # Em produção, seria verificado se o log foi criado corretamente
        encrypted = EncryptionService.encrypt_data(self.test_data, "test_context")
        decrypted = EncryptionService.decrypt_data(encrypted, "test_context")

        self.assertEqual(decrypted, self.test_data)

if __name__ == '__main__':
    # Configurar logging para testes
    import logging
    logging.basicConfig(level=logging.ERROR)

    # Executar testes
    unittest.main(verbosity=2)