"""
Serviço de Blockchain para Auditoria Imutável
Implementa conceitos de blockchain para trilha de auditoria com hash chain
"""

import hashlib
import json
import base64
from datetime import datetime
from flask import current_app
from models import db, AuditLog
from audit_service import AuditService
from collections import OrderedDict

class Block:
    """Bloco da cadeia de auditoria"""

    def __init__(self, index, timestamp, data, previous_hash, nonce=0):
        self.index = index
        self.timestamp = timestamp
        self.data = data  # Dados do log de auditoria
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """Calcula hash do bloco"""
        block_string = json.dumps(OrderedDict([
            ('index', self.index),
            ('timestamp', self.timestamp.isoformat()),
            ('data', self.data),
            ('previous_hash', self.previous_hash),
            ('nonce', self.nonce)
        ]), sort_keys=True, default=str)

        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty=2):
        """Realiza proof-of-work para o bloco"""
        target = '0' * difficulty

        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

        return self.hash

class BlockchainService:
    """Serviço de blockchain para auditoria imutável"""

    def __init__(self):
        self.chain = []
        self.difficulty = 2  # Número de zeros iniciais para proof-of-work
        self.pending_logs = []

        # Carregar cadeia existente ou criar genesis block
        self._initialize_chain()

    def _initialize_chain(self):
        """Inicializa cadeia de blocos"""
        try:
            # Verificar se já existe cadeia no banco
            last_block = AuditLog.query.order_by(AuditLog.sequence_number.desc()).first()

            if last_block:
                # Reconstruir cadeia a partir do banco
                self._rebuild_chain_from_database()
            else:
                # Criar genesis block
                self._create_genesis_block()

        except Exception as e:
            current_app.logger.error(f"Erro ao inicializar cadeia de auditoria: {str(e)}")
            # Fallback: criar genesis block
            self._create_genesis_block()

    def _create_genesis_block(self):
        """Cria bloco genesis"""
        genesis_data = {
            'type': 'genesis_block',
            'message': 'Genesis block for Alphaclin QMS audit trail',
            'system_version': '1.0.0',
            'created_at': datetime.utcnow().isoformat()
        }

        genesis_block = Block(0, datetime.utcnow(), genesis_data, "0")
        genesis_block.mine_block(self.difficulty)

        self.chain.append(genesis_block)

        # Salvar no banco como registro especial
        self._save_genesis_to_database(genesis_block)

    def _save_genesis_to_database(self, block):
        """Salva bloco genesis no banco"""
        try:
            genesis_log = AuditLog(
                sequence_number=0,
                entity_type='system',
                entity_id=0,
                entity_code='GENESIS_BLOCK',
                operation='system_initialization',
                operation_details={
                    'block_hash': block.hash,
                    'block_index': block.index,
                    'type': 'genesis'
                },
                user_id=0,
                user_full_name='Sistema',
                user_role='system',
                data_hash=block.hash,
                previous_hash=block.previous_hash,
                chain_hash=block.hash,
                compliance_level='critical',
                retention_period=2555
            )

            db.session.add(genesis_log)
            db.session.commit()

        except Exception as e:
            current_app.logger.error(f"Erro ao salvar genesis block: {str(e)}")

    def _rebuild_chain_from_database(self):
        """Reconstrói cadeia a partir do banco de dados"""
        try:
            # Obter todos os logs ordenados por sequência
            logs = AuditLog.query.order_by(AuditLog.sequence_number).all()

            if not logs:
                self._create_genesis_block()
                return

            # Reconstruir cadeia
            for log in logs:
                block_data = {
                    'audit_log_id': log.id,
                    'entity_type': log.entity_type,
                    'entity_id': log.entity_id,
                    'operation': log.operation,
                    'timestamp': log.timestamp.isoformat(),
                    'user_id': log.user_id,
                    'compliance_level': log.compliance_level
                }

                block = Block(
                    index=log.sequence_number,
                    timestamp=log.timestamp,
                    data=block_data,
                    previous_hash=log.previous_hash or "0"
                )

                # Recalcular hash para verificação
                block.hash = log.chain_hash or block.calculate_hash()

                self.chain.append(block)

        except Exception as e:
            current_app.logger.error(f"Erro ao reconstruir cadeia: {str(e)}")

    def add_audit_log_to_chain(self, audit_log):
        """
        Adiciona log de auditoria à cadeia de blocos

        Args:
            audit_log: Registro de auditoria a ser adicionado
        """
        try:
            # Preparar dados do bloco
            block_data = {
                'audit_log_id': audit_log.id,
                'entity_type': audit_log.entity_type,
                'entity_id': audit_log.entity_id,
                'entity_code': audit_log.entity_code,
                'operation': audit_log.operation,
                'operation_details': audit_log.operation_details,
                'user_id': audit_log.user_id,
                'user_full_name': audit_log.user_full_name,
                'user_role': audit_log.user_role,
                'timestamp': audit_log.timestamp.isoformat(),
                'compliance_level': audit_log.compliance_level
            }

            # Obter último bloco
            last_block = self.chain[-1] if self.chain else None
            previous_hash = last_block.hash if last_block else "0"

            # Criar novo bloco
            new_block = Block(
                index=audit_log.sequence_number,
                timestamp=audit_log.timestamp,
                data=block_data,
                previous_hash=previous_hash
            )

            # Minerar bloco (proof-of-work)
            new_block.mine_block(self.difficulty)

            # Adicionar à cadeia
            self.chain.append(new_block)

            # Atualizar hashes no registro de auditoria
            audit_log.data_hash = new_block.hash
            audit_log.chain_hash = new_block.hash

            # Verificar integridade da cadeia
            is_valid = self.verify_chain_integrity()

            if not is_valid[0]:
                raise ValueError(f"Cadeia comprometida: {is_valid[1]}")

            return True

        except Exception as e:
            current_app.logger.error(f"Erro ao adicionar log à cadeia: {str(e)}")
            raise

    def verify_chain_integrity(self):
        """
        Verifica integridade de toda a cadeia

        Returns:
            Tupla (is_valid, message)
        """
        try:
            if not self.chain:
                return False, "Cadeia vazia"

            # Verificar genesis block
            if self.chain[0].index != 0:
                return False, "Genesis block inválido"

            # Verificar cada bloco
            for i in range(1, len(self.chain)):
                current_block = self.chain[i]
                previous_block = self.chain[i-1]

                # Verificar hash do bloco atual
                if current_block.hash != current_block.calculate_hash():
                    return False, f"Hash inválido no bloco {current_block.index}"

                # Verificar se bloco aponta para o anterior
                if current_block.previous_hash != previous_block.hash:
                    return False, f"Quebra na cadeia no bloco {current_block.index}"

                # Verificar proof-of-work
                if current_block.hash[:self.difficulty] != '0' * self.difficulty:
                    return False, f"Proof-of-work inválido no bloco {current_block.index}"

            return True, "Cadeia íntegra"

        except Exception as e:
            current_app.logger.error(f"Erro na verificação da cadeia: {str(e)}")
            return False, str(e)

    def get_chain_info(self):
        """Obtém informações da cadeia"""
        try:
            last_block = self.chain[-1] if self.chain else None

            return {
                'chain_length': len(self.chain),
                'last_block_index': last_block.index if last_block else 0,
                'last_block_hash': last_block.hash if last_block else None,
                'difficulty': self.difficulty,
                'is_valid': self.verify_chain_integrity()[0],
                'created_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            current_app.logger.error(f"Erro ao obter informações da cadeia: {str(e)}")
            return {'error': str(e)}

    def get_block_by_index(self, index):
        """Obtém bloco específico por índice"""
        try:
            if index < len(self.chain):
                block = self.chain[index]
                return {
                    'index': block.index,
                    'timestamp': block.timestamp.isoformat(),
                    'data': block.data,
                    'hash': block.hash,
                    'previous_hash': block.previous_hash,
                    'nonce': block.nonce
                }
            return None

        except Exception as e:
            current_app.logger.error(f"Erro ao obter bloco {index}: {str(e)}")
            return None

    def export_chain(self, format='json'):
        """
        Exporta cadeia completa para auditoria externa

        Args:
            format: Formato de exportação (json, csv, etc.)

        Returns:
            Dados da cadeia exportados
        """
        try:
            if format == 'json':
                chain_data = []
                for block in self.chain:
                    chain_data.append({
                        'index': block.index,
                        'timestamp': block.timestamp.isoformat(),
                        'data': block.data,
                        'hash': block.hash,
                        'previous_hash': block.previous_hash,
                        'nonce': block.nonce
                    })

                export_data = {
                    'export_info': {
                        'exported_at': datetime.utcnow().isoformat(),
                        'chain_length': len(chain_data),
                        'format': format,
                        'integrity_verified': self.verify_chain_integrity()[0]
                    },
                    'chain': chain_data
                }

                return json.dumps(export_data, indent=2, default=str)

            else:
                return json.dumps({
                    'error': f'Formato não suportado: {format}'
                })

        except Exception as e:
            current_app.logger.error(f"Erro na exportação da cadeia: {str(e)}")
            return json.dumps({'error': str(e)})

    def get_audit_trail_with_blockchain(self, start_date=None, end_date=None):
        """
        Obtém trilha de auditoria com informações de blockchain

        Args:
            start_date: Data inicial
            end_date: Data final

        Returns:
            Dados da trilha com informações de blockchain
        """
        try:
            # Query base
            query = AuditLog.query

            if start_date:
                query = query.filter(AuditLog.timestamp >= start_date)
            if end_date:
                query = query.filter(AuditLog.timestamp <= end_date)

            logs = query.order_by(AuditLog.sequence_number).all()

            trail_data = []

            for log in logs:
                # Encontrar bloco correspondente
                block_info = None
                for block in self.chain:
                    if (block.data.get('audit_log_id') == log.id or
                        block.index == log.sequence_number):
                        block_info = {
                            'block_index': block.index,
                            'block_hash': block.hash,
                            'block_timestamp': block.timestamp.isoformat()
                        }
                        break

                trail_data.append({
                    'sequence_number': log.sequence_number,
                    'timestamp': log.timestamp.isoformat(),
                    'entity_type': log.entity_type,
                    'entity_id': log.entity_id,
                    'operation': log.operation,
                    'user': {
                        'id': log.user_id,
                        'name': log.user_full_name,
                        'role': log.user_role
                    },
                    'blockchain_info': block_info,
                    'compliance_level': log.compliance_level,
                    'data_hash': log.data_hash,
                    'chain_hash': log.chain_hash
                })

            return {
                'audit_trail': trail_data,
                'blockchain_info': self.get_chain_info(),
                'total_records': len(trail_data),
                'integrity_verified': self.verify_chain_integrity()[0],
                'generated_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            current_app.logger.error(f"Erro ao obter trilha com blockchain: {str(e)}")
            return {'error': str(e)}

    def create_merkle_root(self, data_list):
        """
        Cria raiz de Merkle tree para lote de dados

        Args:
            data_list: Lista de dados para incluir na árvore

        Returns:
            Raiz da Merkle tree
        """
        try:
            if not data_list:
                return hashlib.sha256(b'empty').hexdigest()

            # Se apenas um item, retornar hash direto
            if len(data_list) == 1:
                return hashlib.sha256(str(data_list[0]).encode()).hexdigest()

            # Calcular hashes dos dados
            hashes = [hashlib.sha256(str(data).encode()).hexdigest() for data in data_list]

            # Construir árvore até ter uma raiz
            while len(hashes) > 1:
                if len(hashes) % 2 != 0:
                    # Duplicar último hash se número ímpar
                    hashes.append(hashes[-1])

                # Calcular próximo nível
                next_level = []
                for i in range(0, len(hashes), 2):
                    combined = hashes[i] + hashes[i+1]
                    next_level.append(hashlib.sha256(combined.encode()).hexdigest())

                hashes = next_level

            return hashes[0]

        except Exception as e:
            current_app.logger.error(f"Erro na criação de Merkle root: {str(e)}")
            return None

    def verify_log_in_chain(self, log_id):
        """
        Verifica se log específico está na cadeia e é válido

        Args:
            log_id: ID do log de auditoria

        Returns:
            Informações de verificação
        """
        try:
            # Encontrar log no banco
            log = AuditLog.query.get(log_id)
            if not log:
                return {
                    'found': False,
                    'message': 'Log não encontrado'
                }

            # Encontrar bloco correspondente
            for block in self.chain:
                if (block.data.get('audit_log_id') == log_id or
                    block.index == log.sequence_number):

                    # Verificar se dados do bloco correspondem ao log
                    block_data_matches = (
                        block.data.get('entity_type') == log.entity_type and
                        block.data.get('entity_id') == log.entity_id and
                        block.data.get('operation') == log.operation
                    )

                    return {
                        'found': True,
                        'block_index': block.index,
                        'block_hash': block.hash,
                        'data_matches': block_data_matches,
                        'chain_position': block.index,
                        'is_valid': block.hash == log.chain_hash,
                        'timestamp': block.timestamp.isoformat()
                    }

            return {
                'found': False,
                'message': 'Log não encontrado na cadeia'
            }

        except Exception as e:
            current_app.logger.error(f"Erro na verificação do log na cadeia: {str(e)}")
            return {
                'found': False,
                'error': str(e)
            }

# Instância global
blockchain_service = BlockchainService()