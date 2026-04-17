---
name: vpn-free-libertis
description: Configure un VPN SSH avec support payload Libertis pour le zero-rating (free browsing)
author: Claude Code
version: 1.0.0
---

# Skill: VPN Free Libertis

Ce skill configure un VPN SSH complet avec support du payload Libertis pour surfer gratuitement (zero-rating).

## Configuration requise

L'utilisateur doit fournir :
- **IP du VPS** : L'adresse IP du serveur
- **Port SSH actuel** : Le port SSH actuel du VPS (par défaut 22)
- **Mot de passe root** : Le mot de passe root du VPS (si auth par mot de passe)

## Ce que fait ce skill

1. Crée l'utilisateur VPN avec authentification par mot de passe
2. Configure SSH sur un port interne (2222)
3. Crée et démarre un Proxy Python qui envoie "HTTP/1.1 200 Connection Established"
4. Configure sslh pour multiplexer HTTP et SSH sur le port 443
5. Vérifie que tout fonctionne correctement
6. Fournit les informations de connexion et le payload à utiliser

## Architecture

```
Client (avec payload) → sslh (443) → Proxy Python (9999) → "200 OK" → sshd (2222)
```

## Procédure

### ÉTAPE 1 : Récupérer les informations de connexion

Demander à l'utilisateur :
- IP du VPS
- Port SSH actuel (22 par défaut)
- Méthode d'authentification (clé ou mot de passe)

### ÉTAPE 2 : Créer l'utilisateur VPN

```bash
# Se connecter au VPS
ssh -p PORT root@IP_VPS

# Créer l'utilisateur
useradd -m -s /bin/bash gosen
echo "gosen:gosen" | chpasswd
```

### ÉTAPE 3 : Configurer SSH

```bash
# Activer l'authentification par mot de passe
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Changer le port SSH à 2222
sed -i '/^Port 22/d' /etc/ssh/sshd_config
echo "Port 2222" >> /etc/ssh/sshd_config

# Redémarrer SSH
systemctl restart sshd

# Vérifier
netstat -tlnp | grep 2222
```

### ÉTAPE 4 : Créer le Proxy Python

Créer le fichier `/root/proxy.py` avec ce contenu :

```python
import socket, threading

LISTEN_PORT = 9999
SSH_PORT = 2222

def handle_client(client_socket):
    try:
        data = client_socket.recv(1024)
        client_socket.send(b"HTTP/1.1 200 Connection Established\r\n\r\n")
        target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target_socket.connect(('127.0.0.1', SSH_PORT))

        def forward(source, destination):
            while True:
                chunk = source.recv(4096)
                if not chunk: break
                destination.sendall(chunk)

        threading.Thread(target=forward, args=(client_socket, target_socket)).start()
        threading.Thread(target=forward, args=(target_socket, client_socket)).start()
    except:
        pass

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', LISTEN_PORT))
server.listen(100)
print(f"Proxy actif sur le port {LISTEN_PORT}...")
while True:
    client, _ = server.accept()
    threading.Thread(target=handle_client, args=(client,)).start()
```

Démarrer le proxy :
```bash
nohup python3 /root/proxy.py > /tmp/proxy.log 2>&1 &
```

### ÉTAPE 5 : Installer et configurer sslh

```bash
# Installer sslh
apt update && apt install -y sslh

# Créer la configuration
cat > /etc/sslh.cfg << 'EOF'
timeout: 5;
listen: 0.0.0.0:443;
listen: [::]:443;
protocol:
    {
        name: ssh;
        host: localhost;
        port: 2222;
        log_level: 0;
    }
    {
        name: http;
        host: localhost;
        port: 9999;
        log_level: 0;
    }
EOF

# Configurer le service
cat > /etc/default/sslh << 'EOF'
RUN=yes
DAEMON=/usr/sbin/sslh
DAEMON_OPTS="--listen 0.0.0.0:443 --ssh localhost:2222 --http localhost:9999 --pidfile /var/run/sslh/sslh.pid --verbose"
EOF

# Démarrer sslh
systemctl start sslh
systemctl enable sslh
```

### ÉTAPE 6 : Vérification

```bash
# Vérifier tous les ports
netstat -tlnp | grep -E ':443|:2222|:9999'

# Résultat attendu :
# tcp  0  0.0.0.0:9999  0.0.0.0:*  LISTEN  python3
# tcp  0  0.0.0.0:2222  0.0.0.0:*  LISTEN  sshd
# tcp  0  0.0.0.0:443   0.0.0.0:*  LISTEN  sslh
```

### ÉTAPE 7 : Test du proxy

```bash
echo -e 'GET / HTTP/1.0\r\nHost: test.com\r\n\r\n' | nc localhost 9999
```

Résultat attendu :
```
HTTP/1.1 200 Connection Established

SSH-2.0-OpenSSH_8.9p1
```

### ÉTAPE 8 : Fournir les informations de connexion

À la fin, fournir ces informations à l'utilisateur :

| Champ | Valeur |
|-------|--------|
| **Host** | `IP_VPS` |
| **Port** | `443` |
| **Username** | `gosen` |
| **Password** | `gosen` |
| **Protocol** | `ssh-direct` |
| **Payload** | `GET http://41.159.3.107 HTTP/1.0[crlf]Host: http://41.159.3.105.[crlf]Connection: keep-alive[crlf]User-Agent: Dalvik/2.1.0 (Linux; U; Android 13; TECNO CI8 Build/TP1A.220624.014)[crlf]X-Online-Host: 41.159.3.107[crlf][crlf]` |

### ÉTAPE 9 : Applications compatibles

Mentionner que cela fonctionne avec :
- npv tunnel
- HTTP Injector
- SSH Custom
- Postern

## Dépannage

### Le port 9999 est déjà utilisé
Changer `LISTEN_PORT = 9999` dans `/root/proxy.py` pour un autre port (ex: 8888, 7777) et mettre à jour `/etc/sslh.cfg` et `/etc/default/sslh`.

### Le proxy ne démarre pas
Vérifier les logs :
```bash
cat /tmp/proxy.log
```

### sslh ne démarre pas
Vérifier la configuration :
```bash
sshd -t
systemctl status sslh
journalctl -u sslh -n 50
```

## Notes importantes

1. **Toujours tester la configuration SSH avant de changer le port**
2. **Garder une connexion SSH existante ouverte pendant les modifications**
3. **Utiliser `sshd -t` pour valider la configuration avant de redémarrer**
4. **Le port 443 est utilisé car rarement bloqué par les opérateurs**

## Historique des versions

- **v1.0.0** (2026-04-08) : Version initiale
