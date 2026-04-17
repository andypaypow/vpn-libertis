# Aide demandée - VPN SSH avec Payload Libertis

## 📋 Contexte

Besoin d'aide pour configurer un VPN SSH qui permet de surfer gratuitement avec l'opérateur Libertis en utilisant un payload spécifique.

## ✅ Ce qui fonctionne

### Configuration VPN actuelle

**Serveur :** VPS chez Hostinger (72.62.181.239)

**Architecture configurée :**
- **Multiplexeur :** sslh (SSL/SSH multiplexer)
- **Port public :** 443 (sslh écoute)
- **Port SSH interne :** 2222
- **Utilisateur :** gosen
- **Mot de passe :** gosen

## ❌ Le problème

### Payload utilisé

```
GET http://41.159.3.107 HTTP/1.0[crlf]Host: http://41.159.3.105.[crlf]Connection: keep-alive[crlf]User-Agent: Dalvik/2.1.0 (Linux; U; Android 13; TECNO CI8 Build/TP1A.220624.014)[crlf]X-Online-Host: 41.159.3.107[crlf][crlf]
```

### Comportement attendu
- Ce payload fonctionne avec le VPN d'un ami
- Permet de surfer gratuitement (zero-rating) avec Libertis

### Comportement actuel
- Le VPN se connecte ✅
- Le tunnel est établi ✅
- MAIS le trafic n'est pas "zero-rated" ❌
- Les données sont décomptées du forfait ❌

## 🎯 Ce qui est demandé à l'ami

1. **Partager sa configuration VPN complète** (scripts, fichiers de config)
2. **Expliquer comment son architecture permet le zero-rating**
3. **Donner les étapes exactes pour reproduire sa configuration**

## 📞 Informations de contact du VPS

- **IP :** 72.62.181.239
- **Hébergeur :** Hostinger
- **Accès SSH :** root (port 443) ou gosen (port 443)
- **OS :** Ubuntu 22.04

---

**Date de création :** 2026-04-08
**Statut :** En attente d'aide
