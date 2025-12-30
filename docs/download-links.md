# Обновление списков модов

## Где править списки

- `mods/sources/modrinth-server.json` — моды, которые должны быть на сервере
- `mods/sources/modrinth-client.json` — только клиентские моды
- `mods/sources/server-mods.txt` — прямые ссылки на .jar (сервер)
- `mods/sources/client-mods.txt` — прямые ссылки на .jar (клиент)
- `mods/sources/curseforge.json` — моды с CurseForge (если есть API-ключ)

## Как обновлять

```bash
make fetch-mods
```

Если нужно скачать только серверные моды:

```bash
make fetch-mods-server
```
