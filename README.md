# kyrgyz-normalizer

[![PyPI version](https://img.shields.io/pypi/v/kyrgyz-normalizer.svg)](https://pypi.org/project/kyrgyz-normalizer/)
[![Python](https://img.shields.io/pypi/pyversions/kyrgyz-normalizer.svg)](https://pypi.org/project/kyrgyz-normalizer/)
[![Tests](https://img.shields.io/badge/tests-1019%20passed-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Кыргызча текст нормализатор — TTS системасы үчүн.**

Сандарды, даталарды, убакытты, акча бирдиктерин, аббревиатураларды жана башка форматтарды кыргыз тилинде сөзгө айландырат.

## Орнотуу / Installation

```bash
pip install kyrgyz-normalizer
```

## Колдонуу / Usage

```python
from kyrgyz_normalizer import normalize

normalize("2024-жылы 15 км жол курулду")
# → "эки миң жыйырма төртүнчү жылы он беш километр жол курулду"

normalize("Баасы 1500 сом")
# → "Баасы бир миң беш жүз сом"

normalize("01.02.2024")
# → "эки миң жыйырма төртүнчү жыл биринчи февраль"

normalize("Саат 12:30да башталат")
# → "Саат он эки отузда башталат"

normalize("КР Президенти БУУнун жыйынында")
# → "кыргыз республикасы Президенти бириккен улуттар уюмунун жыйынында"
```

### KyrgyzTextNormalizer классы

```python
from kyrgyz_normalizer import KyrgyzTextNormalizer

normalizer = KyrgyzTextNormalizer()

normalizer.number_to_words(2024)    # "эки миң жыйырма төрт"
normalizer.number_to_ordinal(5)     # "бешинчи"
normalizer.roman_to_number("XIV")   # 14
normalizer.decimal_to_words("3,14") # "үч бүтүн жүздөн он төрт"
```

### CLI

```bash
# Бир текстти нормализациялоо
kyrgyz-normalizer "Баасы 1500 сом"

# Интерактивдүү режим
kyrgyz-normalizer
```

## Мүмкүнчүлүктөр / Features

| Категория | Мисал | Жыйынтык |
|-----------|-------|-----------|
| Сандар | `2024` | эки миң жыйырма төрт |
| Иреттик сандар | `3-класс` | үчүнчү класс |
| Даталар | `01.02.2024` | эки миң жыйырма төртүнчү жыл биринчи февраль |
| Убакыт | `12:30да` | он эки отузда |
| Акча | `1500 сом` | бир миң беш жүз сом |
| Өлчөм бирдиктери | `100 км/ч` | жүз километр саатына |
| Пайыздар | `15,5%` | он беш бүтүн ондон беш пайыз |
| Кыргызча аббревиатуралар | `КР`, `БУУ` | кыргыз республикасы |
| Англисче аббревиатуралар | `IT`, `GPS` | ай ти, жи пи эс |
| Телефон номерлери | `+996 555 123 456` | плюс тогуз тогуз алты ... |
| Римские цифры | `XXI кылым` | жыйырма биринчи кылым |
| Математика | `5+3=8` | беш кошуу үч барабар сегиз |
| Ондук бөлчөктөр | `3,14` | үч бүтүн жүздөн он төрт |
| Сингармонизм | суффикстер | кыргыз тилинин үндөшүүк закону |

## Тесттер / Tests

Долбоор **1019 тест** менен текшерилген (1000 параметрленген + 19 unit/regression):

```bash
pip install pytest
pytest tests/ -v
```

```
============================= 1019 passed in 0.35s =============================
```

Тесттер `tests/test_data.txt` файлында сакталган — ар бир категория үчүн ~50 тест-кейс.

## Долбоордун структурасы / Project Structure

```
kyrgyz-normalizer/
├── src/kyrgyz_normalizer/
│   ├── __init__.py          # Public API: normalize(), KyrgyzTextNormalizer
│   └── normalizer.py        # Негизги нормализатор классы
├── tests/
│   ├── test_normalizer.py   # pytest тесттери (1019 тест)
│   └── test_data.txt        # Тест маалыматтары (1000 кейс)
├── pyproject.toml
├── LICENSE                  # MIT
└── README.md
```

## Лицензия / License

MIT — [LICENSE](LICENSE)
