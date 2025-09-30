#!/usr/bin/env python3
"""
Script para testar conectividade de rede e diagnosticar problemas
"""

import socket
import webbrowser
import time
import subprocess
import sys

def get_local_ip():
    """Obtém o endereço IP local da máquina"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def check_port_availability(ip, port):
    """Verifica se a porta está disponível"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((ip, port))
        sock.close()

        if result == 0:
            return False, f"Porta {port} ESTA EM USO por outro processo"
        else:
            return True, f"Porta {port} esta DISPONIVEL"
    except Exception as e:
        return False, f"Erro ao verificar porta: {e}"

def check_firewall_status():
    """Verifica status do firewall do Windows"""
    try:
        # Tentar executar netsh para verificar regras de firewall
        result = subprocess.run(['netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name=all'],
                              capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            # Procurar por regras relacionadas à porta 5000
            rules_text = result.stdout.lower()
            if '5000' in rules_text or 'python' in rules_text:
                return "VERIFICAR", "Encontradas regras possivelmente relacionadas"
            else:
                return "OK", "Nenhuma regra bloqueando encontrada"
        else:
            return "ERRO", "Nao foi possivel verificar firewall"
    except Exception as e:
        return "ERRO", f"Falha ao verificar firewall: {e}"

def test_server_binding():
    """Testa se consegue fazer bind na porta"""
    local_ip = get_local_ip()
    port = 5000

    print("="*60)
    print("DIAGNOSTICO DE CONECTIVIDADE DE REDE")
    print("="*60)

    print(f"IP Local Detectado: {local_ip}")
    print(f"Porta Testada: {port}")
    print()

    # 1. Verificar disponibilidade da porta
    print("1. Verificando disponibilidade da porta...")
    port_available, port_msg = check_port_availability(local_ip, port)
    print(f"   {port_msg}")
    print()

    # 2. Verificar status do firewall
    print("2. Verificando firewall do Windows...")
    firewall_status, firewall_msg = check_firewall_status()
    print(f"   Status Firewall: {firewall_status}")
    print(f"   {firewall_msg}")
    print()

    # 3. Tentar fazer bind de teste
    print("3. Testando bind na porta...")
    try:
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        test_sock.bind((local_ip, port))
        test_sock.close()
        print(f"   [SUCESSO] Bind realizado com sucesso em {local_ip}:{port}")
        print("   O servidor Flask deveria conseguir iniciar nesta porta")
    except Exception as e:
        print(f"   [FALHA] Nao foi possivel fazer bind: {e}")
        print("   Pode haver problema de permissoes ou firewall")
    print()

    # 4. Interfaces de rede disponíveis
    print("4. Interfaces de rede disponiveis:")
    try:
        hostname = socket.gethostname()
        addresses = socket.getaddrinfo(hostname, None)
        unique_ips = set()

        for addr in addresses:
            if addr[0] == socket.AF_INET:  # IPv4 only
                unique_ips.add(addr[4][0])

        for ip in unique_ips:
            print(f"   - {ip}")
    except Exception as e:
        print(f"   Erro ao obter interfaces: {e}")
    print()

    # 5. Recomendações
    print("5. Recomendacoes:")
    if not port_available:
        print("   - Feche outros processos que possam estar usando a porta 5000")
        print("   - Reinicie o sistema se necessario")
    else:
        print("   - Porta disponivel para uso")

    if firewall_status != "OK":
        print("   - Considere desabilitar temporariamente o firewall para teste:")
        print("     netsh advfirewall set allprofiles state off")
        print("   - Ou adicione regra para permitir conexoes na porta 5000:")
        print("     netsh advfirewall firewall add rule name=\"Alphaclin QMS\" dir=in action=allow protocol=TCP localport=5000")

    print()
    print("="*60)
    print("Para iniciar o servidor Alphaclin QMS:")
    print(f"   python app.py")
    print("="*60)

if __name__ == "__main__":
    test_server_binding()