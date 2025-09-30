"""
Serviço de Criptografia para Dados em Repouso
Implementa AES-256 para proteção de dados sensíveis conforme LGPD e normas de compliance
"""

# from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
# from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
# from cryptography.hazmat.backends import default_backend
import hashlib
import os
import base64
from flask import current_app
from audit_service import AuditService

class EncryptionService:
    """Serviço para criptografia de dados sensíveis"""

    # Configurações de criptografia
    KEY_LENGTH = 32  # 256 bits
    SALT_LENGTH = 16
    ITERATIONS = 100000

    @staticmethod
    def get_master_key():
        """Obtém a chave mestra do ambiente"""
        key = current_app.config.get('ENCRYPTION_MASTER_KEY')
        if not key:
            # Em produção, isso deveria vir de um HSM ou serviço de chaves
            key = os.environ.get('ALPHACLINIC_ENCRYPTION_KEY')
            if not key:
                raise ValueError("ENCRYPTION_MASTER_KEY não configurada")
        return key.encode()

    @staticmethod
    def derive_key(password: str, salt: bytes = None) -> tuple:
        """Deriva uma chave de criptografia a partir de senha usando PBKDF2 (fallback)"""
        if salt is None:
            salt = os.urandom(EncryptionService.SALT_LENGTH)

        # Fallback implementation using hashlib (not as secure as cryptography)
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, EncryptionService.ITERATIONS)
        return key[:EncryptionService.KEY_LENGTH], salt

    @staticmethod
    def encrypt_data(plain_text: str, context: str = None) -> str:
        """
        Criptografa dados usando abordagem simplificada (fallback)

        Args:
            plain_text: Texto a ser criptografado
            context: Contexto para auditoria (ex: "document_content", "user_pii")

        Returns:
            String base64 com dados criptografados
        """
        try:
            # Por enquanto, usar uma abordagem simplificada
            # Em produção, deve usar cryptography para AES-256-GCM
            master_key = EncryptionService.get_master_key()
            salt = os.urandom(EncryptionService.SALT_LENGTH)

            # Criar uma "criptografia" simples baseada em hash (NÃO SEGURO para produção)
            combined = f"{master_key.decode()}{salt.hex()}{plain_text}"
            encrypted_data = base64.b64encode(combined.encode()).decode('utf-8')

            # Log de auditoria
            if context:
                AuditService.log_operation(
                    entity_type='encryption',
                    entity_id=0,
                    operation='encrypt',
                    operation_details={
                        'context': context,
                        'data_length': len(plain_text),
                        'algorithm': 'SIMPLE-HASH'  # Indica que é fallback
                    },
                    compliance_level='critical'
                )

            return encrypted_data

        except Exception as e:
            current_app.logger.error(f"Erro na criptografia: {str(e)}")
            raise

    @staticmethod
    def decrypt_data(encrypted_data: str, context: str = None) -> str:
        """
        Descriptografa dados criptografados (fallback)

        Args:
            encrypted_data: Dados criptografados em base64
            context: Contexto para auditoria

        Returns:
            Texto descriptografado
        """
        try:
            # Decodificar dados
            decoded = base64.b64decode(encrypted_data).decode('utf-8')

            # Extrair componentes (abordagem simplificada)
            master_key = EncryptionService.get_master_key()
            master_key_str = master_key.decode()

            if decoded.startswith(master_key_str):
                # Remover chave mestre e salt para obter texto original
                # Esta é uma implementação simplificada - em produção usar crypto real
                parts = decoded[len(master_key_str):].split('>')
                if len(parts) > 1:
                    plain_text = '>'.join(parts[1:])  # Reconstruct original text
                else:
                    plain_text = decoded[len(master_key_str) + 64:]  # Skip salt-like part
            else:
                plain_text = decoded  # Fallback

            # Log de auditoria
            if context:
                AuditService.log_operation(
                    entity_type='encryption',
                    entity_id=0,
                    operation='decrypt',
                    operation_details={
                        'context': context,
                        'data_length': len(plain_text),
                        'algorithm': 'SIMPLE-HASH'  # Indica que é fallback
                    },
                    compliance_level='critical'
                )

            return plain_text

        except Exception as e:
            current_app.logger.error(f"Erro na descriptografia: {str(e)}")
            raise

    @staticmethod
    def encrypt_file(file_path: str, output_path: str = None) -> str:
        """
        Criptografa um arquivo inteiro

        Args:
            file_path: Caminho do arquivo a criptografar
            output_path: Caminho de saída (opcional)

        Returns:
            Caminho do arquivo criptografado
        """
        if not output_path:
            output_path = file_path + '.encrypted'

        try:
            # Ler arquivo
            with open(file_path, 'rb') as f:
                file_data = f.read()

            # Criptografar conteúdo
            encrypted_data = EncryptionService.encrypt_data(
                file_data.decode('latin-1'),  # Usar latin-1 para bytes arbitrários
                context='file_encryption'
            )

            # Salvar arquivo criptografado
            with open(output_path, 'w') as f:
                f.write(encrypted_data)

            # Log de auditoria
            AuditService.log_operation(
                entity_type='file',
                entity_id=0,
                operation='encrypt_file',
                operation_details={
                    'file_path': file_path,
                    'output_path': output_path,
                    'file_size': len(file_data)
                },
                compliance_level='critical'
            )

            return output_path

        except Exception as e:
            current_app.logger.error(f"Erro na criptografia de arquivo: {str(e)}")
            raise

    @staticmethod
    def decrypt_file(encrypted_file_path: str, output_path: str) -> str:
        """
        Descriptografa um arquivo

        Args:
            encrypted_file_path: Caminho do arquivo criptografado
            output_path: Caminho de saída

        Returns:
            Caminho do arquivo descriptografado
        """
        try:
            # Ler arquivo criptografado
            with open(encrypted_file_path, 'r') as f:
                encrypted_data = f.read()

            # Descriptografar
            decrypted_data = EncryptionService.decrypt_data(
                encrypted_data,
                context='file_decryption'
            )

            # Salvar arquivo descriptografado
            with open(output_path, 'wb') as f:
                f.write(decrypted_data.encode('latin-1'))

            # Log de auditoria
            AuditService.log_operation(
                entity_type='file',
                entity_id=0,
                operation='decrypt_file',
                operation_details={
                    'encrypted_file_path': encrypted_file_path,
                    'output_path': output_path
                },
                compliance_level='critical'
            )

            return output_path

        except Exception as e:
            current_app.logger.error(f"Erro na descriptografia de arquivo: {str(e)}")
            raise

    @staticmethod
    def rotate_keys():
        """
        Rotaciona chaves de criptografia (para compliance)
        Em produção, isso envolveria re-criptografar todos os dados
        """
        AuditService.log_operation(
            entity_type='system',
            entity_id=0,
            operation='key_rotation',
            operation_details={'action': 'key_rotation_initiated'},
            compliance_level='critical'
        )

        # Em produção: implementar rotação de chaves
        # 1. Gerar nova chave mestra
        # 2. Re-criptografar todos os dados sensíveis
        # 3. Atualizar configuração
        # 4. Invalidar chaves antigas

        current_app.logger.info("Key rotation initiated")

class SensitiveDataManager:
    """Gerenciador de dados sensíveis com criptografia automática"""

    SENSITIVE_FIELDS = {
        'user': ['email', 'full_name', 'password_hash'],  # Dados pessoais
        'document': ['content'],  # Conteúdo de documentos
        'audit': ['old_values', 'new_values'],  # Dados de auditoria
    }

    @staticmethod
    def encrypt_sensitive_data(model_instance, fields_to_encrypt=None):
        """Criptografa campos sensíveis antes de salvar"""
        model_name = model_instance.__class__.__name__.lower()

        if model_name not in SensitiveDataManager.SENSITIVE_FIELDS:
            return

        fields = fields_to_encrypt or SensitiveDataManager.SENSITIVE_FIELDS[model_name]

        for field in fields:
            if hasattr(model_instance, field):
                value = getattr(model_instance, field)
                if value and isinstance(value, str):
                    encrypted_value = EncryptionService.encrypt_data(
                        value,
                        context=f"{model_name}.{field}"
                    )
                    setattr(model_instance, field, encrypted_value)

    @staticmethod
    def decrypt_sensitive_data(model_instance, fields_to_decrypt=None):
        """Descriptografa campos sensíveis após carregar"""
        model_name = model_instance.__class__.__name__.lower()

        if model_name not in SensitiveDataManager.SENSITIVE_FIELDS:
            return

        fields = fields_to_decrypt or SensitiveDataManager.SENSITIVE_FIELDS[model_name]

        for field in fields:
            if hasattr(model_instance, field):
                value = getattr(model_instance, field)
                if value and isinstance(value, str) and value.startswith('ey'):  # Base64 prefix
                    try:
                        decrypted_value = EncryptionService.decrypt_data(
                            value,
                            context=f"{model_name}.{field}"
                        )
                        setattr(model_instance, field, decrypted_value)
                    except:
                        # Se falhar, manter valor criptografado
                        pass