# Skill: VPN Libertis

Gère et diagnostique le VPN SSH avec payload Libertis pour le zero-rating.

## Utilisation

```
Utilise le skill vpn-libertis
```

## État du VPN actuel

| Port | Service | Statut |
|------|---------|--------|
| 443 | sslh | Public |
| 2222 | sshd | Interne |
| 8888 | proxy_optimized.py | Proxy |

## Connexion

| Champ | Valeur |
|-------|--------|
| Host | 72.62.181.239 |
| Port | 443 |
| Username | gosen |
| Password | gosen |
| Protocol | ssh-direct |

## Payload

```
GET http://41.159.3.107 HTTP/1.0[crlf]Host: http://41.159.3.105.[crlf]Connection: keep-alive[crlf]User-Agent: Dalvik/2.1.0 (Linux; U; Android 13; TECNO CI8 Build/TP1A.220624.014)[crlf]X-Online-Host: 41.159.3.107[crlf][crlf]
```

## Apps compatibles

HTTP Injector, npv tunnel, SSH Custom, Postern

## Version

**v2.0.0** (2026-04-17)
