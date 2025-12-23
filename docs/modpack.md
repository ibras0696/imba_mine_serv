# Модпак проекта (Forge 1.20.1)

Этот документ - полный список модов, их назначение и зависимости. Он нужен и админам, и игрокам: где искать `.jar`, что ставить на сервер, а что только на клиент.

---

## Как читать таблицы

1. **Server + Client** - мод обязателен и на сервере, и у игрока.
2. **Client-only** - мод ставится только на клиент, на сервере он не нужен.
3. **Зависимости** - библиотеки/утилиты, которые должны быть установлены вместе с модом.

Файлы модов распределяем так:
- серверные `.jar` - в `mods/server/`
- клиентские `.jar` - в `mods/client/`

---

## 1. RPG и структуры

| # | Мод | Тип | Назначение | Зависимости |
|---|-----|-----|------------|-------------|
| 1 | When Dungeons Arise | Server + Client | большие структуры, замки, крепости | нет |
| 2 | Dungeons Plus | Server + Client | компактные RPG-структуры | нет |
| 3 | Structure Gel API | Server + Client | библиотека для структурных модов | нет |
| 4 | YUNG's Better Series (Dungeons/Mineshafts/Strongholds/Nether Fortresses) | Server + Client | улучшенные ванильные структуры | YUNG's API |
| 5 | YUNG's API | Server + Client | API для модов YUNG's | нет |
| 6 | DivineRPG | Server + Client | RPG-мод (измерения, мобы, боссы) | нет |

---

## 2. Магия

| # | Мод | Тип | Назначение | Зависимости |
|---|-----|-----|------------|-------------|
| 7 | Ars Nouveau | Server + Client | магия, ритуалы, големы | Patchouli, GeckoLib |
| 8 | Patchouli | Server + Client | книги/мануалы внутри игры | нет |
| 9 | GeckoLib | Server + Client | анимации и модели | нет |

---

## 3. Технологии, механизмы, индустрия

| # | Мод | Тип | Назначение | Зависимости |
|---|-----|-----|------------|-------------|
| 10 | Immersive Engineering | Server + Client | проводка, генераторы, производство | нет |
| 11 | Applied Energistics 2 | Server + Client | ME-сеть, автокрафт, хранение | нет |
| 12 | Industrial Upgrade | Server + Client | индустриальные механизмы и апгрейды | нет |
| 13 | Ad Astra (Forge) | Server + Client | космос, ракеты, планеты | Architectury API, Botarium, Resourceful Lib |
| 14 | Superb Warfare | Server + Client | техника, артиллерия, оружие | Curios API, GeckoLib |
| 15 | Architectury API | Server + Client | библиотека для мультиплатформенных модов | нет |
| 16 | Botarium | Server + Client | хранение ресурсов/энергии | нет |
| 17 | Resourceful Lib | Server + Client | библиотека для Ad Astra и др. | нет |
| 18 | Resourceful Config | Server + Client | библиотека конфигов Resourceful | нет |
| 19 | Advanced Mining Dimension | Server + Client | отдельное шахтерское измерение | нет |

---

## 4. Генерация мира

| # | Мод | Тип | Назначение | Зависимости |
|---|-----|-----|------------|-------------|
| 20 | Terralith | Server + Client | дополнительные биомы | нет |

---

## 5. Утилиты и геймплей

| # | Мод | Тип | Назначение | Зависимости |
|---|-----|-----|------------|-------------|
| 21 | Sophisticated Backpacks | Server + Client | продвинутые рюкзаки | нет |
| 22 | Sophisticated Storage | Server + Client | сундуки/хранилища с сортировкой | Sophisticated Core |
| 23 | Sophisticated Core | Server + Client | библиотека для Sophisticated Storage/Backpacks | нет |
| 24 | Curios API | Server + Client | доп. слоты для аксессуаров | нет |
| 25 | Cloth Config API | Server + Client | настройки модов | нет |
| 26 | Balm | Server + Client (если нужен модом) | техническая библиотека | нет |
| 27 | FallingTree | Server + Client | удобная вырубка деревьев | нет |
| 28 | Ore Excavation | Server + Client | вейнмайнинг руд | нет |

---

## 6. Client-only (не ставить на сервер)

| # | Мод | Тип | Назначение | Зависимости |
|---|-----|-----|------------|-------------|
| 29 | Inventory Profiles Next | Client-only | сортировка/перенос предметов | LibIPN |
| 30 | LibIPN | Client-only | библиотека для Inventory Profiles Next | нет |
| 31 | AppleSkin | Client-only | индикаторы голода/сытости | нет |
| 32 | JEI (Just Enough Items) | Client-only | просмотр рецептов | нет |
| 33 | Jade / Hwyla | Client-only | инфо о блоке при наведении | нет |
| 34 | Embeddium | Client-only | оптимизация FPS (Forge аналог Sodium) | нет |
| 35 | Oculus | Client-only | шейдеры | Embeddium |
| 36 | FerriteCore | Client-only (можно на сервер, но лучше нет) | экономия RAM | нет |
| 37 | JourneyMap | Client-only | карта мира | нет |
| 38 | Shader Packs | Client-only | графические улучшения | через Oculus |
| 39 | GUI-моды | Client-only | улучшение интерфейса | нет |

---

## Краткая сводка

### Обязательны на сервере и клиенте

When Dungeons Arise, Dungeons Plus, Structure Gel API, YUNG's Better Series, YUNG's API, Ars Nouveau, Patchouli, GeckoLib, Immersive Engineering, Applied Energistics 2, Industrial Upgrade, Ad Astra, Superb Warfare, Architectury API, Botarium, Resourceful Lib, Resourceful Config, Advanced Mining Dimension, Terralith, Sophisticated Backpacks, Sophisticated Storage, Sophisticated Core, Curios API, Cloth Config API, Balm, FallingTree, Ore Excavation.

### Только на клиенте

Inventory Profiles Next, LibIPN, AppleSkin, JEI, Jade, Embeddium, Oculus, FerriteCore, JourneyMap, Shader Packs, GUI-моды.

### Опционально

AppleSkin можно не ставить, но он полезен игрокам.

---

## Важные замечания

1. Если добавляешь новый мод, проверь его зависимости и укажи их в списке.
2. Оптимизационные моды (Embeddium, FerriteCore) лучше не ставить на сервер.
3. Списки для авто-скачивания лежат в `mods/sources/` и должны соответствовать этому файлу.
