# Сборка модов

Список модов хранится в двух местах:
- `mods/sources/modrinth-server.json` — моды, которые нужны и серверу, и клиенту
- `mods/sources/modrinth-client.json` — только клиентские моды

Дополнительно:
- `mods/sources/server-mods.txt` и `client-mods.txt` — прямые ссылки на .jar
- `mods/sources/curseforge.json` — моды с CurseForge (если используешь API-ключ)

Для быстрого просмотра списка смотри `mods.md`.

## Обновление модов

```bash
make fetch-mods
```

После обновления модов перезапусти сервер.
