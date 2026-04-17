# Skill: VPN Free Libertis

## Description

Ce skill configure automatiquement un VPN SSH avec support du payload Libertis pour le zero-rating (free browsing).

## Utilisation

Pour utiliser ce skill, invoquez-le simplement dans la conversation :

```
Utilise le skill vpn-free-libertis
```

Le skill vous demandera les informations nécessaires :
- IP du VPS
- Port SSH actuel
- Méthode d'authentification

## Ce que fait le skill

1. ✅ Crée l'utilisateur `gosen` avec mot de passe `gosen`
2. ✅ Configure SSH sur le port interne 2222
3. ✅ Crée et démarre un Proxy Python (port 9999)
4. ✅ Configure sslh pour multiplexer HTTP/SSH sur le port 443
5. ✅ Fournit toutes les informations de connexion

## Architecture

```
Client Android (avec payload)
    ↓ (port 443)
sslh (multiplexeur)
    ↓ (HTTP)
Proxy Python (envoie "200 OK")
    ↓
sshd (port 2222)
```

## Informations de connexion finales

| Champ | Valeur |
|-------|--------|
| Host | IP de votre VPS |
| Port | 443 |
| Username | gosen |
| Password | gosen |
| Protocol | ssh-direct |

## Payload à utiliser

```
GET http://41.159.3.107 HTTP/1.0[crlf]Host: http://41.159.3.105.[crlf]Connection: keep-alive[crlf]User-Agent: Dalvik/2.1.0 (Linux; U; Android 13; TECNO CI8 Build/TP1A.220624.014)[crlf]X-Online-Host: 41.159.3.107[crlf][crlf]
```

## Applications compatibles

- npv tunnel
- HTTP Injector
- SSH Custom
- Postern

## Fichiers créés sur le VPS

- `/root/proxy.py` - Script Proxy Python
- `/etc/sslh.cfg` - Configuration sslh
- `/etc/default/sslh` - Configuration du service sslh

## Ports utilisés

| Port | Service | Rôle |
|------|---------|------|
| 443 | sslh | Port public (HTTP + SSH) |
| 2222 | sshd | SSH interne |
| 9999 | Proxy Python | Intercepte payload et envoie "200 OK" |

## Version

**v1.0.0** (2026-04-08)
