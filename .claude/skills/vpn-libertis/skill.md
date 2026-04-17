---
name: vpn-libertis
description: Gère et diagnostique le VPN SSH Libertis (zero-rating)
author: Claude Code
version: 2.0.0
---

# Skill: VPN Libertis

Ce skill gère et diagnostique le VPN SSH avec payload Libertis pour le zero-rating.

## Configuration actuelle

- **VPS IP:** 72.62.181.239
- **Ports:** 443 (public), 2222 (SSH), 8888 (proxy)
- **Utilisateur:** gosen / gosen
- **Fichier proxy:** /root/proxy_optimized.py

## Architecture

```
Client Android (HTTP Injector)
    ↓ port 443
sslh (multiplexeur)
    ↓ HTTP détecté → port 8888
Proxy Python Turbo (port 8888)
    ↓ envoie "HTTP/1.1 200 Connection Established"
sshd (port 2222)
```

## Ports VPN (NE JAMAIS MODIFIER)

| Port | Service | Protection |
|------|---------|------------|
| 443 | sslh | ⛔ CRITIQUE |
| 2222 | sshd | ⛔ CRITIQUE |
| 8888 | proxy_optimized.py | ⛔ CRITIQUE |

**Note:** Le port 9999 est utilisé par nginx - NE PAS l'utiliser pour le VPN.

## Procédures

### Vérifier l'état du VPN

```bash
ssh -i "$HOME/.ssh/id_ed25519_claude" -p 2222 root@72.62.181.239 "
netstat -tlnp | grep -E ':443|:2222|:8888'
systemctl status sslh --no-pager | head -10
ps aux | grep proxy_optimized | grep -v grep
"
```

### Tester le proxy

```bash
echo -e 'GET / HTTP/1.0\r\n\r\n' | nc localhost 8888
# Résultat attendu : HTTP/1.1 200 Connection Established
```

### Redémarrer le VPN

```bash
# 1. Arrêter le proxy
pkill -f 'python.*proxy'

# 2. Redémarrer sslh
systemctl restart sslh

# 3. Démarrer le proxy optimisé
nohup python3 /root/proxy_optimized.py > /tmp/proxy_turbo.log 2>&1 &

# 4. Vérifier
netstat -tlnp | grep -E ':443|:2222|:8888'
```

### Vérifier les logs

```bash
# Logs proxy
cat /tmp/proxy_turbo.log

# Logs sslh
journalctl -u sslh -n 20 --no-pager
```

### Informations de connexion

Fournir ces informations à l'utilisateur :

| Champ | Valeur |
|-------|--------|
| **Host** | `72.62.181.239` |
| **Port** | `443` |
| **Username** | `gosen` |
| **Password** | `gosen` |
| **Protocol** | `ssh-direct` |

### Payload Libertis

```
GET http://41.159.3.107 HTTP/1.0[crlf]Host: http://41.159.3.105.[crlf]Connection: keep-alive[crlf]User-Agent: Dalvik/2.1.0 (Linux; U; Android 13; TECNO CI8 Build/TP1A.220624.014)[crlf]X-Online-Host: 41.159.3.107[crlf][crlf]
```

### Applications compatibles

- HTTP Injector
- npv tunnel
- SSH Custom
- Postern

## Dépannage

### Le VPN ne fonctionne pas

1. Vérifier les ports : `netstat -tlnp | grep -E ':443|:2222|:8888'`
2. Vérifier sslh : `systemctl status sslh`
3. Vérifier le proxy : `ps aux | grep proxy_optimized`
4. Redémarrer si nécessaire (voir procédure ci-dessus)

### Le port 8888 est occupé

```bash
# Trouver le processus
lsof -i :8888
netstat -tlnp | grep 8888

# Si c'est un autre processus, l'arrêter
kill PID

# Redémarrer le proxy
nohup python3 /root/proxy_optimized.py > /tmp/proxy_turbo.log 2>&1 &
```

### sslh ne redirige pas vers le bon port

```bash
# Vérifier la configuration
cat /etc/default/sslh
cat /etc/sslh.cfg

# Doit pointer vers localhost:8888 (pas 9999)

# Corriger si nécessaire
sed -i 's/--http localhost:9999/--http localhost:8888/' /etc/default/sslh
sed -i 's/port: 9999/port: 8888/' /etc/sslh.cfg

# Redémarrer
systemctl restart sslh
```

## Optimisations Turbo

Le proxy_optimized.py inclut :
- Buffer 64KB (16x plus rapide)
- TCP_NODELAY (latence réduite)
- Keepalive TCP (moins de coupures)
- Pool de threads limité à 200
- SO_REUSEADDR (redémarrage rapide)
- Gestion d'erreurs améliorée

## Notes importantes

1. **La clé du zero-rating** : Le proxy DOIT envoyer "HTTP/1.1 200 Connection Established" avant le tunnel SSH
2. **Pourquoi 443** : Port HTTPS standard, rarement bloqué
3. **Pourquoi Proxy Python** : SSH seul ne peut pas répondre avec "200 OK"
4. **Pourquoi sslh** : Partage le port 443 entre HTTP et SSH
5. **Payload Libertis** : Trompe l'opérateur en simulant une connexion vers 41.159.3.107/105

## Historique

### 2026-04-17 - Réparation VPN
- Port changé de 9999 → 8888 (nginx occupait 9999)
- Utilisation de proxy_optimized.py

### 2026-04-09 - Optimisation Turbo
- Ajout de proxy_optimized.py avec performances 16x

### 2026-04-08 - Installation initiale
- Configuration complète VPN avec Proxy Python et sslh
