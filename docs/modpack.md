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
| 11 | Applied Energistics 2 | Server + Client | ME-сеть, автокрафт, хранение | GuideME |
| 12 | GuideME | Server + Client | библиотека/гайды для AE2 | нет |
| 13 | Industrial Upgrade | Server + Client | индустриальные механизмы и апгрейды | нет |
| 14 | Ad Astra (Forge) | Server + Client | космос, ракеты, планеты | Architectury API, Botarium, Resourceful Lib |
| 15 | Superb Warfare | Server + Client | техника, артиллерия, оружие | Curios API, GeckoLib |
| 16 | Architectury API | Server + Client | библиотека для мультиплатформенных модов | нет |
| 17 | Botarium | Server + Client | хранение ресурсов/энергии | нет |
| 18 | Resourceful Lib | Server + Client | библиотека для Ad Astra и др. | нет |
| 19 | Resourceful Config | Server + Client | библиотека конфигов Resourceful | нет |
| 20 | Advanced Mining Dimension | Server + Client | отдельное шахтерское измерение | нет |

---

## 4. Генерация мира

| # | Мод | Тип | Назначение | Зависимости |
|---|-----|-----|------------|-------------|
| 21 | Terralith | Server + Client | дополнительные биомы | нет |

---

## 5. Утилиты и геймплей

| # | Мод | Тип | Назначение | Зависимости |
|---|-----|-----|------------|-------------|
| 22 | Sophisticated Backpacks | Server + Client | продвинутые рюкзаки | нет |
| 23 | Sophisticated Storage | Server + Client | сундуки/хранилища с сортировкой | Sophisticated Core |
| 24 | Sophisticated Core | Server + Client | библиотека для Sophisticated Storage/Backpacks | нет |
| 25 | Curios API | Server + Client | доп. слоты для аксессуаров | нет |
| 26 | Cloth Config API | Server + Client | настройки модов | нет |
| 27 | Balm | Server + Client (если нужен модом) | техническая библиотека | нет |
| 28 | FallingTree | Server + Client | удобная вырубка деревьев | нет |
| 29 | Ore Excavation | Server + Client | вейнмайнинг руд | нет |

---

## 6. Client-only (не ставить на сервер)

| # | Мод | Тип | Назначение | Зависимости |
|---|-----|-----|------------|-------------|
| 30 | Inventory Profiles Next | Client-only | сортировка/перенос предметов | LibIPN, Kotlin For Forge |
| 31 | LibIPN | Client-only | библиотека для Inventory Profiles Next | Kotlin For Forge |
| 32 | Kotlin For Forge | Client-only | Kotlin рантайм для модов | нет |
| 33 | AppleSkin | Client-only | индикаторы голода/сытости | нет |
| 34 | JEI (Just Enough Items) | Client-only (опционально на сервер для автокрафта) | просмотр рецептов | нет |
| 35 | Jade / Hwyla | Client-only | инфо о блоке при наведении | нет |
| 36 | Embeddium | Client-only | оптимизация FPS (Forge аналог Sodium) | нет |
| 37 | Oculus | Client-only | шейдеры | Embeddium |
| 38 | FerriteCore | Client-only (можно на сервер, но лучше нет) | экономия RAM | нет |
| 39 | JourneyMap | Client-only | карта мира | нет |
| 40 | Shader Packs | Client-only | графические улучшения | через Oculus |
| 41 | GUI-моды | Client-only | улучшение интерфейса | нет |

---

## Краткая сводка

### Обязательны на сервере и клиенте

When Dungeons Arise, Dungeons Plus, Structure Gel API, YUNG's Better Series, YUNG's API, Ars Nouveau, Patchouli, GeckoLib, Immersive Engineering, Applied Energistics 2, GuideME, Industrial Upgrade, Ad Astra, Superb Warfare, Architectury API, Botarium, Resourceful Lib, Resourceful Config, Advanced Mining Dimension, Terralith, Sophisticated Backpacks, Sophisticated Storage, Sophisticated Core, Curios API, Cloth Config API, Balm, FallingTree, Ore Excavation.

### Только на клиенте

Inventory Profiles Next, LibIPN, Kotlin For Forge, AppleSkin, JEI, Jade, Embeddium, Oculus, FerriteCore, JourneyMap, Shader Packs, GUI-моды.

### Опционально

AppleSkin можно не ставить, но он полезен игрокам.

---

## Важные замечания

1. Если добавляешь новый мод, проверь его зависимости и укажи их в списке.
2. Оптимизационные моды (Embeddium, FerriteCore) лучше не ставить на сервер.
3. Списки для авто-скачивания лежат в `mods/sources/` и должны соответствовать этому файлу.
