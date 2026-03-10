#!/usr/bin/env python3
"""
Тесттер — kyrgyz-normalizer
1000 тест-кейс: сандар, даталар, убакыт, акча, аббревиатуралар ж.б.
"""

import os
import pytest
from kyrgyz_normalizer import KyrgyzTextNormalizer, normalize

TESTS_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(TESTS_DIR, "test_data.txt")


# ── Fixtures ─────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def normalizer():
    return KyrgyzTextNormalizer()


# ── Parametrized tests from test_data.txt ────────────────────────────

def _load_test_cases():
    cases = []
    category = ""
    with open(DATA_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            if line.startswith("#"):
                category = line[2:].strip()
                continue
            if " | " not in line:
                continue
            input_text, expected = line.split(" | ", 1)
            cases.append(pytest.param(
                input_text.strip(), expected.strip(),
                id=f"{category}: {input_text.strip()[:50]}"
            ))
    return cases


@pytest.mark.parametrize("input_text,expected", _load_test_cases())
def test_normalize(input_text, expected):
    assert normalize(input_text) == expected


# ── Unit tests: number_to_words ──────────────────────────────────────

class TestNumberToWords:
    def test_zero(self, normalizer):
        assert normalizer.number_to_words(0) == "нөл"

    def test_ones(self, normalizer):
        assert normalizer.number_to_words(1) == "бир"
        assert normalizer.number_to_words(9) == "тогуз"

    def test_tens(self, normalizer):
        assert normalizer.number_to_words(10) == "он"
        assert normalizer.number_to_words(99) == "токсон тогуз"

    def test_hundreds(self, normalizer):
        assert normalizer.number_to_words(100) == "жүз"
        assert normalizer.number_to_words(999) == "тогуз жүз токсон тогуз"

    def test_thousands(self, normalizer):
        assert normalizer.number_to_words(1000) == "бир миң"
        assert normalizer.number_to_words(2024) == "эки миң жыйырма төрт"

    def test_millions(self, normalizer):
        assert normalizer.number_to_words(1000000) == "бир миллион"

    def test_negative(self, normalizer):
        assert normalizer.number_to_words(-5) == "минус беш"


# ── Unit tests: number_to_ordinal ────────────────────────────────────

class TestNumberToOrdinal:
    def test_first(self, normalizer):
        assert normalizer.number_to_ordinal(1) == "биринчи"

    def test_tenth(self, normalizer):
        assert normalizer.number_to_ordinal(10) == "онунчу"

    def test_year(self, normalizer):
        assert normalizer.number_to_ordinal(2024) == "эки миң жыйырма төртүнчү"


# ── Unit tests: roman_to_number ──────────────────────────────────────

class TestRomanToNumber:
    def test_basic(self, normalizer):
        assert normalizer.roman_to_number("I") == 1
        assert normalizer.roman_to_number("IV") == 4
        assert normalizer.roman_to_number("XIV") == 14
        assert normalizer.roman_to_number("XXI") == 21

    def test_large(self, normalizer):
        assert normalizer.roman_to_number("MCMXCIX") == 1999


# ── Unit tests: decimal_to_words ─────────────────────────────────────

class TestDecimalToWords:
    def test_simple(self, normalizer):
        assert normalizer.decimal_to_words("3,14") == "үч бүтүн жүздөн он төрт"

    def test_one_decimal(self, normalizer):
        assert normalizer.decimal_to_words("5,5") == "беш бүтүн ондон беш"


# ── Unit tests: apply_suffix_harmony ─────────────────────────────────

class TestSuffixHarmony:
    def test_back_vowel(self, normalizer):
        result = normalizer.apply_suffix_harmony("бир", "да")
        assert result == "бирде"

    def test_front_vowel(self, normalizer):
        result = normalizer.apply_suffix_harmony("беш", "да")
        assert result == "беште"


# ── Integration: regression tests ────────────────────────────────────

class TestRegression:
    def test_year_in_sentence(self):
        """Bug fix: 2018-жылдан inside sentence was split into 20+18."""
        result = normalize(
            "Кыргызстандын өнүгүүсүнүн 2018-жылдан 2040-жылга чейинки"
        )
        assert "эки миң он сегизинчи жылдан" in result
        assert "эки миң кыркынчы жылга" in result

    def test_multiple_years(self):
        result = normalize("2024-жылы 15 км жол курулду")
        assert "эки миң жыйырма төртүнчү жылы" in result
        assert "он беш километр" in result

    def test_abbreviation_with_suffix(self):
        result = normalize("КР Президенти БУУнун жыйынында")
        assert "кыргыз республикасы" in result
        assert "бириккен улуттар уюмунун" in result
