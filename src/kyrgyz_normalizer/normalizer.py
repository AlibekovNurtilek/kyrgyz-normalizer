#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Кыргызча текст нормализатор TTS системасы үчүн
Сандарды, даталарды, убакытты, акча бирдиктерин жана башка форматтарды сөзгө айландырат
"""

import re


class KyrgyzTextNormalizer:
    # Константы для дат
    YEAR_THRESHOLD = 50  # Граница для определения века (00-49 → 2000+, 50-99 → 1900+)
    CENTURY_2000 = 2000
    CENTURY_1900 = 1900

    def __init__(self):
        # Сандар 0-9
        self.ones = ['', 'бир', 'эки', 'үч', 'төрт', 'беш', 'алты', 'жети', 'сегиз', 'тогуз']
        self.tens = ['', 'он', 'жыйырма', 'отуз', 'кырк', 'элүү', 'алтымыш', 'жетимиш', 'сексен', 'токсон']
        self.hundreds = ['', 'жүз', 'эки жүз', 'үч жүз', 'төрт жүз', 'беш жүз',
                        'алты жүз', 'жети жүз', 'сегиз жүз', 'тогуз жүз']

        # Иреттик сандар (порядковые)
        self.ordinal_ones = ['', 'биринчи', 'экинчи', 'үчүнчү', 'төртүнчү', 'бешинчи',
                            'алтынчы', 'жетинчи', 'сегизинчи', 'тогузунчу']
        self.ordinal_tens = ['', 'онунчу', 'жыйырманчы', 'отузунчу', 'кыркынчы', 'элүүнчү',
                            'алтымышынчы', 'жетимишинчи', 'сексенинчи', 'токсонунчу']

        # Айлар
        self.months = {
            '01': 'январь', '02': 'февраль', '03': 'март', '04': 'апрель',
            '05': 'май', '06': 'июнь', '07': 'июль', '08': 'август',
            '09': 'сентябрь', '10': 'октябрь', '11': 'ноябрь', '12': 'декабрь',
            '1': 'январь', '2': 'февраль', '3': 'март', '4': 'апрель',
            '5': 'май', '6': 'июнь', '7': 'июль', '8': 'август',
            '9': 'сентябрь', '10': 'октябрь', '11': 'ноябрь', '12': 'декабрь'
        }

        # Кыскартылган айлар
        self.month_abbr = {
            'янв': 'январь', 'фев': 'февраль', 'мар': 'март', 'апр': 'апрель',
            'июн': 'июнь', 'июл': 'июль', 'авг': 'август',
            'сен': 'сентябрь', 'окт': 'октябрь', 'ноя': 'ноябрь', 'дек': 'декабрь'
        }

        # Кыскартуулар (чекиттүү)
        self.short_abbr = {
            'ж.б.у.с.': 'жана башка ушул сыяктуу',
            'ж.б.': 'жана башка',
            'б.з.ч.': 'биздин заманга чейин',
            'б.з.ч': 'биздин заманга чейин',
            'б.з.': 'биздин заман',
            'кк.': 'кылымдар',
            'жж.': 'жылдар',
            'к.': 'кылым',
            'көч.': 'көчөсү',
            'м-н': 'менен',
            'б-ча': 'боюнча',
            'ж-а': 'жана',
            'т.б.': 'тагыраак болсо',
            'ө.к.': 'өңдүү көп',
            'б.а.': 'башкача айтканда',
            'мис.': 'мисалы',
            # Адресные сокращения
            'ш.': 'шаары',
            'обл.': 'облусу',
            'р-н': 'району',
            'р.': 'району',
            'үй': 'үй',
            'кв.': 'квартира',
            'мкр.': 'микрорайон',
            'мкр': 'микрорайон'
        }

        # Кыргызча аббревиатуралар
        self.kyrgyz_abbr = {
            'КР': 'кыргыз республикасы',
            'КТЖ': 'кыргыз темир жолу',
            'ЖОЖ': 'жогорку окуу жайы',
            'КМШ': 'көз карандысыз мамлекеттердин шериктештиги',
            'ААК': 'ачык акционердик коом',
            'ЖЧК': 'жоопкерчилиги чектелген коом',
            'БУУ': 'бириккен улуттар уюму',
            'АКШ': 'америка кошмо штаттары',
            'БШК': 'борбордук шайлоо комиссиясы',
            'ШКУ': 'шанхай кызматташтык уюму',
            'ЕККУ': 'европа коопсуздук жана кызматташуу уюму',
            'ЕБ': 'европалык биримдик',
            'ЕАЭБ': 'евразия экономикалык биримдиги',
            'СССР': 'советтик социалисттик республикалар союзу',
            'ФСК': 'сорос кыргызстан фонду',
            'ЭЭА': 'эркин экономикалык аймак',
            'ПРООН': 'бириккен улуттар уюмунун өнүктүрүү программасы',
            'UNICEF': 'бириккен улуттар уюмунун балдар фонду',
            'USAID': 'америка кошмо штаттарынын эл аралык өнүктүрүү агенттиги',
            'ИДП': 'ички дүң продукциясы',
            # Жаңы аббревиатуралар
            'ЖМК': 'жалпыга маалымдоо каражаттары',
            'ЖАМК': 'жаза аткаруу мамлекеттик кызматы',
            'УКМК': 'улуттук коопсуздук мамлекеттик комитети',
            'ТИМ': 'тышкы иштер министрлиги',
            'ӨКМ': 'өзгөчө кырдаалдар министрлиги',
            'ИИМ': 'ички иштер министрлиги',
            'ОИИБ': 'облустук ички иштер башкармалыгы',
            'ШИИББ': 'шаардык ички иштер башкы башкармалыгы',
            'РИИБ': 'райондук ички иштер башкармалыгы',
            'ЧЧК': 'чоң чүй каналы'
        }

        # Англисче аббревиатуралар (тамга боюнча окулат)
        self.english_abbr = {
            'IT': 'ай ти',
            'AI': 'эй ай',
            'GPU': 'жи пи ю',
            'CPU': 'си пи ю',
            'ML': 'эм эл',
            'API': 'эй пи ай',
            'URL': 'ю ар эл',
            'HTTP': 'эйч ти ти пи',
            'HTTPS': 'эйч ти ти пи эс',
            'HTML': 'эйч ти эм эл',
            'CSS': 'си эс эс',
            'PDF': 'пи ди эф',
            'USB': 'ю эс би',
            'WiFi': 'вай фай',
            'GPS': 'жи пи эс',
            'SMS': 'эс эм эс',
            'SIM': 'сим',
            'PIN': 'пин',
            'ATM': 'эй ти эм',
            'VPN': 'ви пи эн',
            'iOS': 'ай о эс',
            'RAM': 'рам',
            'ROM': 'ром',
            'SSD': 'эс эс ди',
            'HDD': 'эйч ди ди',
            'LED': 'лед',
            'LCD': 'эл си ди',
            'TV': 'ти ви',
            'DVD': 'ди ви ди',
            'CD': 'си ди',
            'PR': 'пи ар',
            'HR': 'эйч ар',
            'CEO': 'си и о',
            'ID': 'ай ди',
            'OK': 'окей',
            'QR': 'кю ар'
        }

        # Өлчөм бирдиктери
        self.units = {
            # Кыргызча
            'км': 'километр',
            'м': 'метр',
            'см': 'сантиметр',
            'мм': 'миллиметр',
            'кг': 'килограмм',
            'г': 'грамм',
            'мг': 'миллиграмм',
            'т': 'тонна',
            'л': 'литр',
            'мл': 'миллилитр',
            'га': 'гектар',
            'м2': 'квадрат метр',
            'м3': 'куб метр',
            'км2': 'квадрат километр',
            'см2': 'квадрат сантиметр',
            'км/ч': 'километр саатына',
            'м/с': 'метр секундасына',
            'кВт': 'киловатт',
            'Вт': 'ватт',
            'МВт': 'мегаватт',
            'ГГц': 'гигагерц',
            'МГц': 'мегагерц',
            'кГц': 'килогерц',
            'Гц': 'герц',
            'ГБ': 'гигабайт',
            'МБ': 'мегабайт',
            'КБ': 'килобайт',
            'ТБ': 'терабайт',
            'мин': 'мүнөт',
            'сек': 'секунд',
            'саат': 'саат',
            # Англисче/Эл аралык
            'km': 'километр',
            'km²': 'квадрат километр',
            'm': 'метр',
            'm²': 'квадрат метр',
            'm³': 'куб метр',
            'cm': 'сантиметр',
            'mm': 'миллиметр',
            'kg': 'килограмм',
            'g': 'грамм',
            'mg': 'миллиграмм',
            'l': 'литр',
            'ml': 'миллилитр',
            'ha': 'гектар',
            'km/h': 'километр саатына',
            'm/s': 'метр секундасына',
            'kW': 'киловатт',
            'W': 'ватт',
            'MW': 'мегаватт',
            'GHz': 'гигагерц',
            'MHz': 'мегагерц',
            'kHz': 'килогерц',
            'Hz': 'герц',
            'GB': 'гигабайт',
            'MB': 'мегабайт',
            'KB': 'килобайт',
            'TB': 'терабайт',
            'min': 'мүнөт',
            'sec': 'секунд',
            'h': 'саат'
        }

        # Валюталар
        self.currencies = {
            'сом': 'сом',
            '$': 'доллар',
            '€': 'евро',
            '₽': 'рубль',
            '¥': 'юань',
            '£': 'фунт',
            '₸': 'тенге',
            '₴': 'гривна'
        }

        # Чоң сандар
        self.large_numbers = {
            'млн': 'миллион',
            'млрд': 'миллиард',
            'трлн': 'триллион',
            'тыс': 'миң'
        }

        # Кэш для частых чисел (0-100) - ускоряет обработку
        self._number_cache = {}
        self._ordinal_cache = {}
        for i in range(101):
            self._number_cache[i] = self._compute_number_to_words(i)
            self._ordinal_cache[i] = self._compute_number_to_ordinal(i)

        # Отсортированные словари (один раз)
        self.short_abbr_sorted = sorted(self.short_abbr.items(), key=lambda x: -len(x[0]))

        # Прекомпилированные regex паттерны для ускорения
        self._regex_patterns = {
            'email': re.compile(r'\b([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+)\.([a-zA-Z]{2,})\b'),
            'phone_996': re.compile(r'\+996[\s-]?(\d{3})[\s-]?(\d{3})[\s-]?(\d{3})'),
            'phone_mobile': re.compile(r'\b(0\d{3})[\s-]?(\d{3})[\s-]?(\d{3})\b'),
            'phone_context': re.compile(r'(номер|номери|тел|телефон|звоните|позвоните|code|код|борбор|индекс|почтовый|WhatsApp|Telegram)[\s::-]*(\d{3,6})\b', re.IGNORECASE),
            'date_dot': re.compile(r'\b(\d{1,2})\.(\d{1,2})\.(\d{2,4})\b'),
            'date_slash': re.compile(r'\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b'),
            'time_colon_suffix': re.compile(r'(\d{1,2}):(\d{2})(га|ге|го|гө|ка|ке|ко|кө|да|де|до|дө|та|те|то|тө)'),
            'time_colon': re.compile(r'(саат|убакыт)\s+(\d{1,2}):(\d{2})'),
            'time_dot_suffix': re.compile(r'\b(\d{1,2})\.(\d{2})(га|ге|го|гө|ка|ке|ко|кө|да|де|до|дө|та|те|то|тө)'),
            'number_k': re.compile(r'\b(\d+)k\b'),
            'roman_century': re.compile(r'\b([IVXLCDM]{1,15})\s*к\.'),
            'roman_general': re.compile(r'(?<![a-zA-Z])\b([IVXLCDM]{1,15})\b(?!\.|\s*[a-zA-Z])'),
            'letter_digit': re.compile(r'([а-яөүңА-ЯӨҮҢa-zA-Z])(\d+)'),
            'multiple_spaces': re.compile(r'\s+'),
            'year_range': re.compile(r'(\d{4})\s*[-–—]\s*(\d{4})\s*[-.]?\s*(жылдары|жылдар|жж|гг)\.?'),
            'year_single': re.compile(r'(\d{4})\s*[-.]?\s*(жылы|жыл|жж|гг|ж|г)\.?(?!\w)'),
            'percent_range': re.compile(r'(\d+)\s*[-–—]\s*(\d+)\s*%'),
            'percent_single': re.compile(r'(\d+)\s*%'),
            'currency_range': re.compile(r'(\d+)\s*[-–—]\s*(\d+)\s*([₸$€£¥₽])'),
            'ordinal_suffix': re.compile(r'(\d+)\s*-?\s*(чи|чу|чү|нчи|нчу|нчү|ынчы|инчи|үнчү|унчу)'),
            'decimal_comma': re.compile(r'\b(\d+),(\d+)\b'),
            'fraction': re.compile(r'\b(\d+)/(\d+)\b'),
        }

        # Атайын символдор
        self.symbols = {
            '%': 'пайыз',
            '№': 'номур',
            '@': 'эт белгиси',
            '&': 'жана',
            '§': 'параграф',
            '©': 'автордук укук',
            '®': 'катталган',
            '™': 'соода белгиси',
            '°': 'градус',
            '×': 'көбөйтүү',
            '÷': 'бөлүү',
            '±': 'кошуу кемитүү',
            '≈': 'болжол менен',
            '≠': 'барабар эмес',
            '≤': 'кичине же барабар',
            '≥': 'чоң же барабар',
            '<': 'кичине',
            '>': 'чоң',
            '=': 'барабар',
            '+': 'кошуу',
            '−': 'кемитүү',
            '—': '',
            '–': '',
            '/': 'сызыкча'
        }

        # Римские цифры
        self.roman_values = [
            ('M', 1000), ('CM', 900), ('D', 500), ('CD', 400),
            ('C', 100), ('XC', 90), ('L', 50), ('XL', 40),
            ('X', 10), ('IX', 9), ('V', 5), ('IV', 4), ('I', 1)
        ]

        # Шаарлар
        self.cities = {
            'г.': '',
            'ш.': 'шаары'
        }

        # Хардкод для времени (часто используемые значения минут с правильными суффиксами)
        self.time_suffixes = {
            # га/ка суффикс
            ('нөл', 'га'): 'нөлгө',
            ('беш', 'га'): 'бешке',
            ('он', 'га'): 'онго',
            ('он беш', 'га'): 'он бешке',
            ('жыйырма', 'га'): 'жыйырмага',
            ('жыйырма беш', 'га'): 'жыйырма бешке',
            ('отуз', 'га'): 'отузга',
            ('отуз беш', 'га'): 'отуз бешке',
            ('кырк', 'га'): 'кыркка',
            ('кырк беш', 'га'): 'кырк бешке',
            ('элүү', 'га'): 'элүүгө',
            ('элүү беш', 'га'): 'элүү бешке',

            # да/та суффикс
            ('нөл', 'да'): 'нөлдө',
            ('беш', 'да'): 'беште',
            ('он', 'да'): 'ондо',
            ('он беш', 'да'): 'он беште',
            ('жыйырма', 'да'): 'жыйырмада',
            ('жыйырма беш', 'да'): 'жыйырма беште',
            ('отуз', 'да'): 'отузда',
            ('отуз беш', 'да'): 'отуз беште',
            ('кырк', 'да'): 'кыркта',
            ('кырк беш', 'да'): 'кырк беште',
            ('элүү', 'да'): 'элүүдө',
            ('элүү беш', 'да'): 'элүү беште',
        }

    def digit_to_word(self, digit):
        """Жеке цифраны сөзгө айландыруу (телефон номерлери үчүн)"""
        digit_map = {
            '0': 'нөл', '1': 'бир', '2': 'эки', '3': 'үч', '4': 'төрт',
            '5': 'беш', '6': 'алты', '7': 'жети', '8': 'сегиз', '9': 'тогуз'
        }
        return digit_map.get(digit, digit)

    def digits_to_words(self, number_string):
        """Цифраларды жеке-жеке окуу (телефон номерлери үчүн)"""
        return ' '.join(self.digit_to_word(d) for d in number_string if d.isdigit())

    def _compute_number_to_words(self, num):
        """Внутренняя функция: санды сөзгө айландыруу (без кэша)"""
        if num == 0:
            return 'нөл'
        if num < 0:
            return 'минус ' + self._compute_number_to_words(abs(num))

        result = ''

        # Триллион
        if num >= 1000000000000:
            trillions = num // 1000000000000
            result += self._compute_number_to_words(trillions) + ' триллион '
            num %= 1000000000000

        # Миллиард
        if num >= 1000000000:
            billions = num // 1000000000
            result += self._compute_number_to_words(billions) + ' миллиард '
            num %= 1000000000

        # Миллион
        if num >= 1000000:
            millions = num // 1000000
            result += self._compute_number_to_words(millions) + ' миллион '
            num %= 1000000

        # Миң
        if num >= 1000:
            thousands = num // 1000
            result += self._compute_number_to_words(thousands) + ' миң '
            num %= 1000

        # Жүз
        if num >= 100:
            result += self.hundreds[num // 100] + ' '
            num %= 100

        # Он
        if num >= 10:
            result += self.tens[num // 10] + ' '
            num %= 10

        # Бирдик
        if num > 0:
            result += self.ones[num] + ' '

        return result.strip()

    def number_to_words(self, num):
        """Санды сөзгө айландыруу (с кэшем для 0-100)"""
        if 0 <= num <= 100:
            return self._number_cache[num]
        return self._compute_number_to_words(num)

    def _compute_number_to_ordinal(self, num):
        """Внутренняя функция: иреттик сан (без кэша)"""
        if num >= 1000:
            thousands = num // 1000
            remainder = num % 1000
            if remainder == 0:
                return self._compute_number_to_words(thousands) + ' миңинчи'
            else:
                return self._compute_number_to_words(thousands) + ' миң ' + self._compute_number_to_ordinal(remainder)

        if num >= 100:
            hundred_part = num // 100
            remainder = num % 100
            if remainder == 0:
                return self.hundreds[hundred_part] + 'үнчү'
            return self.hundreds[hundred_part] + ' ' + self._compute_number_to_ordinal(remainder)

        if num >= 10:
            ten_part = num // 10
            remainder = num % 10
            if remainder == 0:
                return self.ordinal_tens[ten_part]
            return self.tens[ten_part] + ' ' + self.ordinal_ones[remainder]

        if num < len(self.ordinal_ones):
            return self.ordinal_ones[num]
        return self._compute_number_to_words(num) + 'инчи'

    def number_to_ordinal(self, num):
        """Иреттик сан (порядковое числительное) с кэшем для 0-100"""
        if 0 <= num <= 100:
            return self._ordinal_cache[num]
        return self._compute_number_to_ordinal(num)

    def roman_to_number(self, roman):
        """Римские цифры санга айландыруу (XIV → 14)"""
        result = 0
        i = 0
        roman = roman.upper()

        for numeral, value in self.roman_values:
            while roman[i:i+len(numeral)] == numeral:
                result += value
                i += len(numeral)

        return result

    def decimal_to_words(self, num_str):
        """Ондук санды сөзгө айландыруу (0.5 → нөл бүтүн ондон беш)"""

        parts = num_str.split(',')
        whole_part = int(parts[0]) if parts[0] else 0

        result = 'нөл' if whole_part == 0 else self.number_to_words(whole_part)

        if len(parts) > 1 and parts[1]:
            result += ' бүтүн'
            decimal = parts[1]

            # Разряд аныктоо
            if len(decimal) == 1:
                decimal_place = 'ондон'
            elif len(decimal) == 2:
                decimal_place = 'жүздөн'
            elif len(decimal) == 3:
                decimal_place = 'миңден'
            elif len(decimal) == 4:
                decimal_place = 'он миңден'
            elif len(decimal) == 5:
                decimal_place = 'жүз миңден'
            elif len(decimal) == 6:
                decimal_place = 'миллиондон'
            else:
                decimal_place = ''

            decimal_num = int(decimal)
            if decimal_place:
                result += ' ' + decimal_place + ' ' + self.number_to_words(decimal_num)
            else:
                result += ' ' + self.number_to_words(decimal_num)

        return result

    def apply_suffix_harmony(self, word, suffix):
        """
        Универсальная функция сингармонизма для кыргызского языка
        Применяет законы гармонии гласных и согласных
        """
        if not suffix:
            return word

        word_lower = word.lower().strip()
        if not word_lower:
            return word + suffix

        # Находим последний гласный
        vowels_back_rounded = 'оу'      # задние округлые
        vowels_back_unrounded = 'аы'    # задние неокруглые
        vowels_front_rounded = 'өү'     # передние округлые
        vowels_front_unrounded = 'еи'   # передние неокруглые
        all_vowels = vowels_back_rounded + vowels_back_unrounded + vowels_front_rounded + vowels_front_unrounded

        voiceless_consonants = 'кпстфхцчшщ'

        last_vowel = ''
        last_char = word_lower[-1]

        for char in reversed(word_lower):
            if char in all_vowels:
                last_vowel = char
                break

        # Определяем тип последнего гласного
        is_back = last_vowel in (vowels_back_rounded + vowels_back_unrounded)
        is_rounded = last_vowel in (vowels_back_rounded + vowels_front_rounded)
        ends_with_vowel = last_char in all_vowels
        ends_with_voiceless = last_char in voiceless_consonants

        # ПРАВИЛО: о/у НЕ сочетается с ө/ү и наоборот
        is_back_rounded = last_vowel in vowels_back_rounded  # о, у
        is_back_unrounded = last_vowel in vowels_back_unrounded  # а, ы
        is_front_rounded = last_vowel in vowels_front_rounded  # ө, ү
        is_front_unrounded = last_vowel in vowels_front_unrounded  # е, и

        # 1. Гармония согласных (первая буква суффикса)
        new_suffix = suffix
        first_consonant = suffix[0] if suffix else ''

        if first_consonant in 'дт':
            if ends_with_vowel:
                new_suffix = 'н' + suffix[1:]
            elif ends_with_voiceless:
                new_suffix = 'т' + suffix[1:]
            else:
                new_suffix = 'д' + suffix[1:]
        elif first_consonant in 'гк':
            if ends_with_vowel:
                new_suffix = 'н' + suffix[1:]
            elif ends_with_voiceless:
                new_suffix = 'к' + suffix[1:]
            else:
                new_suffix = 'г' + suffix[1:]

        # 2. Гармония гласных
        result_suffix = ''
        for char in new_suffix:
            if char == 'а':
                if is_front_rounded:
                    result_suffix += 'ө'
                elif is_front_unrounded:
                    result_suffix += 'е'
                elif is_back_rounded and not ends_with_vowel:
                    result_suffix += 'о'
                else:
                    result_suffix += 'а'
            elif char == 'ы':
                if is_front_rounded:
                    result_suffix += 'ү'
                elif is_front_unrounded:
                    result_suffix += 'и'
                elif is_back_rounded:
                    result_suffix += 'у'
                else:
                    result_suffix += 'ы'
            elif char == 'о':
                result_suffix += 'ө' if is_front_rounded else 'о'
            elif char == 'у':
                result_suffix += 'ү' if is_front_rounded else 'у'
            elif char == 'ө':
                result_suffix += 'о' if is_back_rounded else 'ө'
            elif char == 'ү':
                result_suffix += 'у' if is_back_rounded else 'ү'
            else:
                result_suffix += char

        return word + result_suffix

    def normalize(self, text):
        """Негизги нормализация функциясы"""
        result = text

        # === 0. КЫСКАРТУУЛАР (эң биринчи) ===
        for abbr, full in self.short_abbr_sorted:
            pattern = re.compile(rf'(?<![а-яөүңА-ЯӨҮҢA-Za-z0-9]){re.escape(abbr)}(?![а-яөүңА-ЯӨҮҢA-Za-z0-9])')
            result = pattern.sub(full, result)

        # Сокращенные месяцы
        for abbr, full in self.month_abbr.items():
            result = re.sub(rf'\b{abbr}\.?\b', full, result, flags=re.IGNORECASE)


        # === 1. EMAIL ЖАНА URL ===
        result = self._regex_patterns['email'].sub(
            lambda m: f"{m.group(1)} эт белгиси {m.group(2)} чекит {m.group(3)}",
            result
        )

        # === 2. ТЕЛЕФОН НОМЕРЛЕРИ ===
        result = self._regex_patterns['phone_996'].sub(
            lambda m: f"плюс тогуз тогуз алты {self.digits_to_words(m.group(1))} {self.digits_to_words(m.group(2))} {self.digits_to_words(m.group(3))}",
            result
        )

        result = self._regex_patterns['phone_mobile'].sub(
            lambda m: f"{self.digits_to_words(m.group(1))} {self.digits_to_words(m.group(2))} {self.digits_to_words(m.group(3))}",
            result
        )

        result = self._regex_patterns['phone_context'].sub(
            lambda m: f"{m.group(1)} {self.digits_to_words(m.group(2))}",
            result
        )

        # === 3. НЕКОРРЕКТНЫЕ ФОРМАТЫ ===
        def convert_invalid_format(m):
            parts = re.split(r'[./]', m.group(0))
            words = []
            for p in parts:
                if p:
                    words.append(self.number_to_words(int(p)))
            return ' '.join(words)

        result = re.sub(
            r'\b\d*\d{3,}\d*(?:[./]\d+)+\b|\b\d+(?:[./]\d*\d{3,}\d*)+\b',
            convert_invalid_format,
            result
        )

        # === 4. ДАТАЛАР ===
        result = re.sub(
            r'(\d{4})\s*-?\s*жылдын\s+(\d{1,2})\s*-?\s*(\w+)',
            lambda m: f"{self.number_to_words(int(m.group(1)))} жылдын {self.number_to_words(int(m.group(2)))} {m.group(3)}",
            result
        )

        result = re.sub(
            r'(\d{1,2})\s*-?\s*(\w+),?\s*(\d{4})\s*[-\.]\s*жыл',
            lambda m: f"{self.number_to_words(int(m.group(1)))} {m.group(2)} {self.number_to_ordinal(int(m.group(3)))} жыл",
            result
        )

        result = re.sub(
            r'(\d{1,2})\s*-?\s*(\w+)\s+(\d{4})\s*[-\.]\s*жыл',
            lambda m: f"{self.number_to_words(int(m.group(1)))} {m.group(2)} {self.number_to_ordinal(int(m.group(3)))} жыл",
            result
        )

        # 2024-08-15 12:30 (ISO формат)
        result = re.sub(
            r'(\d{4})-(\d{2})-(\d{2})\s+(\d{1,2}):(\d{2})',
            lambda m: f"{self.number_to_words(int(m.group(1)))} жылдын {self.months.get(m.group(2), m.group(2))} айынын {self.number_to_words(int(m.group(3)))} күнү саат {self.number_to_words(int(m.group(4)))} {self.number_to_words(int(m.group(5)))}",
            result
        )

        # 30 Ноябрь 2025
        def format_text_month_date(m):
            day = int(m.group(1))
            month_name = m.group(2).lower()
            year = int(m.group(3))

            day_ord = self.number_to_ordinal(day)
            year_ord = self.number_to_ordinal(year)

            return f"{day_ord} {month_name} {year_ord} жыл"

        result = re.sub(
            r'\b(\d{1,2})\s+(январь|февраль|март|апрель|май|июнь|июль|август|сентябрь|октябрь|ноябрь|декабрь)\s+(\d{4})\b',
            format_text_month_date,
            result,
            flags=re.IGNORECASE
        )

        # 01.02.2024
        def format_date(m):
            num1 = int(m.group(1))
            num2 = int(m.group(2))
            year_str = m.group(3)

            if num2 > 12 and num1 <= 12:
                month_num = str(num1).zfill(2)
                day = num2
            else:
                day = num1
                month_num = str(num2).zfill(2)

            if len(year_str) == 2:
                year_int = int(year_str)
                if year_int < self.YEAR_THRESHOLD:
                    year_full = self.CENTURY_2000 + year_int
                else:
                    year_full = self.CENTURY_1900 + year_int
            else:
                year_full = int(year_str)

            year = self.number_to_ordinal(year_full)
            day_ord = self.number_to_ordinal(day)
            month = self.months.get(month_num, month_num)

            return f"{year} жыл {day_ord} {month}"

        result = self._regex_patterns['date_dot'].sub(format_date, result)
        result = self._regex_patterns['date_slash'].sub(format_date, result)

        # === 4-5. ЖЫЛДАР ===
        result = self._regex_patterns['year_range'].sub(
            lambda m: f"{self.number_to_ordinal(int(m.group(1)))} {self.number_to_ordinal(int(m.group(2)))} жылдар",
            result
        )

        result = self._regex_patterns['year_single'].sub(
            lambda m: f"{self.number_to_ordinal(int(m.group(1)))} жыл" + ('ы' if m.group(2) == 'жылы' else ''),
            result
        )

        # === 6. УБАКЫТ ===
        def format_time_with_suffix(m):
            hours = int(m.group(1))
            minutes = m.group(2)
            suffix_base = m.group(3)

            hours_word = self.number_to_words(hours)

            base_map = {
                'га': 'га', 'ге': 'га', 'го': 'га', 'гө': 'га',
                'ка': 'ка', 'ке': 'ка', 'ко': 'ка', 'кө': 'ка',
                'да': 'да', 'де': 'да', 'до': 'да', 'дө': 'да',
                'та': 'та', 'те': 'та', 'то': 'та', 'тө': 'та'
            }
            base_suffix = base_map.get(suffix_base, suffix_base)

            if minutes == '00':
                return self.apply_suffix_harmony(hours_word, base_suffix)
            elif minutes.startswith('0') and minutes != '00':
                minutes_word = self.number_to_words(int(minutes[1]))
                time_str = f"{hours_word} нөл {minutes_word}"
                return self.apply_suffix_harmony(time_str, base_suffix)
            else:
                minutes_word = self.number_to_words(int(minutes))

                hardcoded_key = (minutes_word, base_suffix)
                if hardcoded_key in self.time_suffixes:
                    return f"{hours_word} {self.time_suffixes[hardcoded_key]}"
                else:
                    time_str = f"{hours_word} {minutes_word}"
                    return self.apply_suffix_harmony(time_str, base_suffix)

        result = re.sub(
            r'(\d{1,2}):(\d{2})(га|ге|го|гө|ка|ке|ко|кө|да|де|до|дө|та|те|то|тө)',
            format_time_with_suffix,
            result
        )

        def format_time(m):
            hours = int(m.group(1))
            minutes = m.group(2)

            hours_word = self.number_to_words(hours)

            if minutes == '00':
                return hours_word
            elif minutes.startswith('0') and minutes != '00':
                minutes_word = self.number_to_words(int(minutes[1]))
                return f"{hours_word} нөл {minutes_word}"
            else:
                minutes_word = self.number_to_words(int(minutes))
                return f"{hours_word} {minutes_word}"

        result = re.sub(r'\b(\d{1,2}):(\d{2})\b', format_time, result)

        def format_dot_time(m):
            prefix = m.group(1) if m.group(1) else ''
            hours = int(m.group(2))
            minutes = m.group(3)
            suffix_input = m.group(4) if m.group(4) else ''

            hours_word = self.number_to_words(hours)

            if minutes == '00':
                time_str = hours_word
            elif minutes.startswith('0') and minutes != '00':
                minutes_word = self.number_to_words(int(minutes[1]))
                time_str = f"{hours_word} нөл {minutes_word}"
            else:
                minutes_word = self.number_to_words(int(minutes))
                time_str = f"{hours_word} {minutes_word}"

            if suffix_input:
                base_map = {
                    'га': 'га', 'ге': 'га', 'го': 'га', 'гө': 'га',
                    'ка': 'ка', 'ке': 'ка', 'ко': 'ка', 'кө': 'ка',
                    'да': 'да', 'де': 'да', 'до': 'да', 'дө': 'да',
                    'та': 'та', 'те': 'та', 'то': 'та', 'тө': 'та'
                }
                base_suffix = base_map.get(suffix_input, suffix_input)

                if minutes != '00' and not minutes.startswith('0'):
                    minutes_word = self.number_to_words(int(minutes))
                    hardcoded_key = (minutes_word, base_suffix)
                    if hardcoded_key in self.time_suffixes:
                        time_with_suffix = f"{hours_word} {self.time_suffixes[hardcoded_key]}"
                    else:
                        time_with_suffix = self.apply_suffix_harmony(time_str, base_suffix)
                else:
                    time_with_suffix = self.apply_suffix_harmony(time_str, base_suffix)
            else:
                time_with_suffix = time_str

            return f"{prefix}{time_with_suffix}"

        result = re.sub(
            r'((?:саат|убакыт)\s+)(\d{1,2})\.(\d{2})(га|ге|го|гө|ка|ке|ко|кө|да|де|до|дө|та|те|то|тө)?',
            format_dot_time,
            result
        )

        # === 7. ЧОҢ САНДАР "k" МЕНЕН ===
        result = self._regex_patterns['number_k'].sub(
            lambda m: f"{self.number_to_words(int(m.group(1)))} миң",
            result
        )

        # === 8. АКЧА БИРДИКТЕРИ ===
        result = re.sub(
            r'(\d+(?:[,]\d+)?)\s*(млн|млрд|трлн)\s*(сом|доллар|евро|рубль)',
            lambda m: f"{self.decimal_to_words(m.group(1))} {self.large_numbers.get(m.group(2), m.group(2))} {m.group(3)}",
            result
        )

        result = re.sub(
            r'(\d{1,3}(?:\s\d{3})*)[,.](\d{2})\s*сом',
            lambda m: f"{self.number_to_words(int(m.group(1).replace(' ', '')))} сом {self.number_to_words(int(m.group(2)))} тыйын",
            result
        )

        result = re.sub(
            r'(\d{1,3}(?:\s\d{3})+)\s*сом\b',
            lambda m: f"{self.number_to_words(int(m.group(1).replace(' ', '')))} сом",
            result
        )

        result = re.sub(
            r'(\d+)\s*сом\b',
            lambda m: f"{self.number_to_words(int(m.group(1)))} сом",
            result
        )

        for symbol, name in self.currencies.items():
            if symbol in ['$', '€', '₽', '£', '¥', '₸', '₴']:
                result = re.sub(
                    re.escape(symbol) + r'(\d+(?:[,]\d+)?)',
                    lambda m, n=name: f"{self.decimal_to_words(m.group(1))} {n}",
                    result
                )
                result = re.sub(
                    r'(\d+(?:[,]\d+)?)' + re.escape(symbol),
                    lambda m, n=name: f"{self.decimal_to_words(m.group(1))} {n}",
                    result
                )

        # Формат с точкой БЕЗ контекстного слова, но С суффиксом
        def format_dot_time_no_context(m):
            hours = int(m.group(1))
            minutes = m.group(2)
            suffix_base = m.group(3)

            hours_word = self.number_to_words(hours)

            base_map = {
                'га': 'га', 'ге': 'га', 'го': 'га', 'гө': 'га',
                'ка': 'ка', 'ке': 'ка', 'ко': 'ка', 'кө': 'ка',
                'да': 'да', 'де': 'да', 'до': 'да', 'дө': 'да',
                'та': 'та', 'те': 'та', 'то': 'та', 'тө': 'та'
            }
            base_suffix = base_map.get(suffix_base, suffix_base)

            if minutes == '00':
                return self.apply_suffix_harmony(hours_word, base_suffix)
            elif minutes.startswith('0') and minutes != '00':
                minutes_word = self.number_to_words(int(minutes[1]))
                time_str = f"{hours_word} нөл {minutes_word}"
                return self.apply_suffix_harmony(time_str, base_suffix)
            else:
                minutes_word = self.number_to_words(int(minutes))
                hardcoded_key = (minutes_word, base_suffix)
                if hardcoded_key in self.time_suffixes:
                    return f"{hours_word} {self.time_suffixes[hardcoded_key]}"
                else:
                    time_str = f"{hours_word} {minutes_word}"
                    return self.apply_suffix_harmony(time_str, base_suffix)

        result = re.sub(
            r'\b(\d{1,2})\.(\d{2})(га|ге|го|гө|ка|ке|ко|кө|да|де|до|дө|та|те|то|тө)',
            format_dot_time_no_context,
            result
        )

        # === 9. ИРЕТТИК САНДАР ===
        result = re.sub(
            r'(\d+)-([а-яөүңА-ЯӨҮҢ]+)',
            lambda m: f"{self.number_to_ordinal(int(m.group(1)))} {m.group(2)}",
            result
        )

        result = re.sub(
            r'(\d+)\s*-?\s*(чи|чу|чү|нчи|нчу|нчү|ынчы|инчи|үнчү|унчу)',
            lambda m: self.number_to_ordinal(int(m.group(1))),
            result
        )

        # === 10. ЖАШ, КЛАСС ===
        result = re.sub(
            r'(\d+)жашта',
            lambda m: f"{self.number_to_words(int(m.group(1)))} жашта",
            result
        )
        result = re.sub(
            r'(\d+)(чи|чу|чү)\s*класста',
            lambda m: f"{self.number_to_ordinal(int(m.group(1)))} класста",
            result
        )

        result = re.sub(
            r'(\d+)(мин|мүн|сек|саат)\b',
            lambda m: f"{self.number_to_words(int(m.group(1)))} {self.units.get(m.group(2), m.group(2))}",
            result
        )

        # === 11. КУРСТАР ===
        result = re.sub(
            r'(\d+)\s*-?\s*курста',
            lambda m: f"{self.number_to_ordinal(int(m.group(1)))} курста",
            result
        )

        # === 12. ӨЛЧӨМ БИРДИКТЕРИ ===
        for unit, name in sorted(self.units.items(), key=lambda x: -len(x[0])):
            result = re.sub(
                r'(\d+(?:[,]\d+)?)\s*' + re.escape(unit) + r'\b',
                lambda m, n=name: f"{self.decimal_to_words(m.group(1))} {n}",
                result
            )

        # === 13. ПАЙЫЗ ДИАПАЗОНУ ===
        result = re.sub(
            r'(\d+(?:[,]\d+)?)\s*[-–—]\s*(\d+(?:[.,]\d+)?)\s*%',
            lambda m: f"{self.decimal_to_words(m.group(1))} {self.decimal_to_words(m.group(2))} пайыз",
            result
        )

        # === 14. ПАЙЫЗ ===
        result = re.sub(
            r'(\d+(?:[,]\d+)?)\s*%',
            lambda m: f"{self.decimal_to_words(m.group(1))} пайыз",
            result
        )

        # === 15. КЫЛЫМДАР ДИАПАЗОНУ ===
        def replace_roman_century_range(m):
            roman1 = m.group(1)
            roman2 = m.group(2)
            marker = m.group(3)
            try:
                num1 = self.roman_to_number(roman1)
                num2 = self.roman_to_number(roman2)
                word = 'кылымдары' if marker == 'кылымдары' else 'кылымдар'
                return f"{self.number_to_ordinal(num1)} {self.number_to_ordinal(num2)} {word}"
            except:
                return m.group(0)

        result = re.sub(
            r'\b([IVXLCDM]{1,15})\s*[-–—]\s*([IVXLCDM]{1,15})\s*[-.]?\s*(кылымдары|кылымдар|кк)\.?',
            replace_roman_century_range,
            result
        )

        result = re.sub(
            r'(\d+)\s*[-–—]\s*(\d+)\s*[-.]?\s*(кылымдары|кылымдар|кк)\.?',
            lambda m: f"{self.number_to_ordinal(int(m.group(1)))} {self.number_to_ordinal(int(m.group(2)))} {'кылымдары' if m.group(3) == 'кылымдары' else 'кылымдар'}",
            result
        )

        # === 16. МАТЕМАТИКА (кемитүү) ===
        result = re.sub(
            r'\b(\d+)\s*[-–—]\s*(\d+)\b',
            lambda m: f"{self.number_to_words(int(m.group(1)))} кемитүү {self.number_to_words(int(m.group(2)))}",
            result
        )

        # === 17. МАТЕМАТИКА ===
        result = re.sub(
            r'(\d+)\s*[×xXхХ*]\s*(\d+)\s*=\s*(\d+)',
            lambda m: f"{self.number_to_words(int(m.group(1)))} көбөйтүү {self.number_to_words(int(m.group(2)))} барабар {self.number_to_words(int(m.group(3)))}",
            result
        )
        result = re.sub(
            r'(\d+)\s*\+\s*(\d+)\s*=\s*(\d+)',
            lambda m: f"{self.number_to_words(int(m.group(1)))} кошуу {self.number_to_words(int(m.group(2)))} барабар {self.number_to_words(int(m.group(3)))}",
            result
        )
        result = re.sub(
            r'(\d+)\s*[-−]\s*(\d+)\s*=\s*(\d+)',
            lambda m: f"{self.number_to_words(int(m.group(1)))} кемитүү {self.number_to_words(int(m.group(2)))} барабар {self.number_to_words(int(m.group(3)))}",
            result
        )
        result = re.sub(
            r'(\d+)\s*/\s*(\d+)\s*=\s*(\d+)',
            lambda m: f"{self.number_to_words(int(m.group(1)))} бөлүү {self.number_to_words(int(m.group(2)))} барабар {self.number_to_words(int(m.group(3)))}",
            result
        )

        result = re.sub(
            r'(\d+)\s*\+\s*(\d+)',
            lambda m: f"{self.number_to_words(int(m.group(1)))} кошуу {self.number_to_words(int(m.group(2)))}",
            result
        )
        result = re.sub(
            r'(\d+)\s*[×xXхХ*]\s*(\d+)',
            lambda m: f"{self.number_to_words(int(m.group(1)))} көбөйтүү {self.number_to_words(int(m.group(2)))}",
            result
        )
        result = re.sub(
            r'(\d+)\s*/\s*(\d+)',
            lambda m: f"{self.number_to_words(int(m.group(1)))} бөлүү {self.number_to_words(int(m.group(2)))}",
            result
        )

        # === 18. АББРЕВИАТУРАЛАР ===
        kyrgyz_suffixes = r'(нын|нун|нүн|нин|дын|дун|дүн|дин|тын|тун|түн|тин|га|ге|ка|ке|го|гө|ко|кө|да|де|та|те|до|дө|то|тө|дан|ден|тан|тен|дон|дөн|тон|төн|н|ы|и|у|ү)?'
        for abbr, full in self.kyrgyz_abbr.items():
            result = re.sub(r'\b' + re.escape(abbr) + kyrgyz_suffixes + r'\b',
                          lambda m, f=full: self.apply_suffix_harmony(f, m.group(1)) if m.group(1) else f,
                          result)

        for abbr, full in self.english_abbr.items():
            result = re.sub(r'\b' + re.escape(abbr) + r'\b', full, result)

        # === 19. АДРЕСТЕР ===
        result = re.sub(r'\bг\.\s*', '', result)
        result = re.sub(
            r'(\d+)\s*-?\s*кичи\s*район',
            lambda m: f"{self.number_to_ordinal(int(m.group(1)))} кичи район",
            result
        )

        def fraction_to_words(m):
            numerator = int(m.group(1))
            denominator = int(m.group(2))
            denom_word = self.number_to_words(denominator)
            numer_word = self.number_to_words(numerator)

            last_vowel = ''
            for char in reversed(denom_word):
                if char in 'аоуыэеөүи':
                    last_vowel = char
                    break

            if last_vowel in 'өү':
                suffix = 'дөн'
            elif last_vowel in 'оу':
                suffix = 'дон'
            elif last_vowel in 'еи':
                suffix = 'ден'
            else:
                suffix = 'дан'

            if denom_word[-1] in 'кпстфхцчшщ':
                suffix = 'т' + suffix[1:]
            elif denom_word[-1] in 'аоуыэеөүи':
                suffix = 'н' + suffix[1:]

            return f"{denom_word}{suffix} {numer_word}"

        result = re.sub(r'\b(\d+)/(\d+)\b', fraction_to_words, result)

        # === 20. АПОСТРОФ МЕНЕН СӨЗДӨР ===
        result = re.sub(r"(\w+)'(\w+)", r'\1\2', result)

        # === 21. АТАЙЫН СИМВОЛДОР ===
        result = re.sub(r'[«»„"""]', '', result)
        result = re.sub(r"[''‚']", '', result)

        result = re.sub(
            r'№\s*(\d+)',
            lambda m: f"номур {self.number_to_words(int(m.group(1)))}",
            result
        )

        result = re.sub(r'(?<=[,\s])%(?=[,\s]|$)', 'пайыз', result)
        result = re.sub(r'(?<=[,\s])№(?=[,\s]|$)', 'номур', result)
        result = re.sub(r'(?<=[,\s])@(?=[,\s]|$)', 'эт белгиси', result)
        result = re.sub(r'(?<=[,\s])&(?=[,\s]|$)', 'жана', result)

        # === 22. РИМСКИЕ ЦИФРЫ ===
        def replace_roman_century(m):
            roman = m.group(1)
            try:
                num = self.roman_to_number(roman)
                return f"{self.number_to_ordinal(num)} кылым"
            except:
                return m.group(0)

        result = re.sub(
            r'\b([IVXLCDM]{1,15})\s*к\.',
            replace_roman_century,
            result
        )

        result = re.sub(
            r'(?<![a-zA-Z])\b([IVXLCDM]{1,15})\b(?!\.|\s*[a-zA-Z])',
            lambda m: self.number_to_ordinal(self.roman_to_number(m.group(0))),
            result
        )

        # === 23. ОНДУК САНДАР ===
        result = re.sub(
            r'\b(\d+[,]\d+)\b',
            lambda m: self.decimal_to_words(m.group(1)),
            result
        )

        # === 24. БОШТУК МЕНЕН ЖАЗЫЛГАН ЧОҢ САНДАР ===
        def replace_spaced_number(match):
            num_str = match.group(0).replace(' ', '')
            return self.number_to_words(int(num_str))
        result = re.sub(r'\b\d{1,3}(?:\s\d{3})+\b', replace_spaced_number, result)

        # === 25. ЖӨНӨКӨЙ САНДАР ===
        result = re.sub(
            r'\b(\d+)\b',
            lambda m: self.number_to_words(int(m.group(1))),
            result
        )

        # === 26. КАЛГАН БАРДЫК САНДАРДЫ КОНВЕРТАЦИЯЛОО ===
        result = self._regex_patterns['letter_digit'].sub(r'\1 \2', result)

        def convert_separated_numbers(m):
            parts = re.split(r'[./]', m.group(0))
            words = []
            for p in parts:
                if p:
                    words.append(self.number_to_words(int(p)))
            return ' '.join(words)

        result = re.sub(
            r'\d+[./]\d+(?:[./]\d+)*',
            convert_separated_numbers,
            result
        )

        result = re.sub(
            r'\d+',
            lambda m: self.number_to_words(int(m.group(0))),
            result
        )

        # === 27. ТАЗАЛОО ===
        result = self._regex_patterns['multiple_spaces'].sub(' ', result)
        result = result.strip()

        return result
