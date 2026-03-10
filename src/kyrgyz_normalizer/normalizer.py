#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Кыргызча текст нормализатор TTS системасы үчүн
Сандарды, даталарды, убакытты, акча бирдиктерин жана башка форматтарды сөзгө айландырат
"""

import re
import sys


class KyrgyzTextNormalizer:
    YEAR_THRESHOLD = 50
    CENTURY_2000 = 2000
    CENTURY_1900 = 1900

    def __init__(self):
        self._init_data()
        self._init_caches()
        self._compile_patterns()

    # ================================================================
    # Маалыматтар
    # ================================================================

    def _init_data(self):
        self.ones = ['', 'бир', 'эки', 'үч', 'төрт', 'беш', 'алты', 'жети', 'сегиз', 'тогуз']
        self.tens = ['', 'он', 'жыйырма', 'отуз', 'кырк', 'элүү', 'алтымыш', 'жетимиш', 'сексен', 'токсон']
        self.hundreds = ['', 'жүз', 'эки жүз', 'үч жүз', 'төрт жүз', 'беш жүз',
                         'алты жүз', 'жети жүз', 'сегиз жүз', 'тогуз жүз']

        self.ordinal_ones = ['', 'биринчи', 'экинчи', 'үчүнчү', 'төртүнчү', 'бешинчи',
                             'алтынчы', 'жетинчи', 'сегизинчи', 'тогузунчу']
        self.ordinal_tens = ['', 'онунчу', 'жыйырманчы', 'отузунчу', 'кыркынчы', 'элүүнчү',
                             'алтымышынчы', 'жетимишинчи', 'сексенинчи', 'токсонунчу']

        self.months = {
            '01': 'январь', '02': 'февраль', '03': 'март', '04': 'апрель',
            '05': 'май', '06': 'июнь', '07': 'июль', '08': 'август',
            '09': 'сентябрь', '10': 'октябрь', '11': 'ноябрь', '12': 'декабрь',
            '1': 'январь', '2': 'февраль', '3': 'март', '4': 'апрель',
            '5': 'май', '6': 'июнь', '7': 'июль', '8': 'август',
            '9': 'сентябрь',
        }

        self.month_abbr = {
            'янв': 'январь', 'фев': 'февраль', 'мар': 'март', 'апр': 'апрель',
            'июн': 'июнь', 'июл': 'июль', 'авг': 'август',
            'сен': 'сентябрь', 'окт': 'октябрь', 'ноя': 'ноябрь', 'дек': 'декабрь',
        }

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
            'ш.': 'шаары',
            'обл.': 'облусу',
            'р-н': 'району',
            'р.': 'району',
            'үй': 'үй',
            'кв.': 'квартира',
            'мкр.': 'микрорайон',
            'мкр': 'микрорайон',
        }

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
            'ЖМК': 'жалпыга маалымдоо каражаттары',
            'ЖАМК': 'жаза аткаруу мамлекеттик кызматы',
            'УКМК': 'улуттук коопсуздук мамлекеттик комитети',
            'ТИМ': 'тышкы иштер министрлиги',
            'ӨКМ': 'өзгөчө кырдаалдар министрлиги',
            'ИИМ': 'ички иштер министрлиги',
            'ОИИБ': 'облустук ички иштер башкармалыгы',
            'ШИИББ': 'шаардык ички иштер башкы башкармалыгы',
            'РИИБ': 'райондук ички иштер башкармалыгы',
            'ЧЧК': 'чоң чүй каналы',
        }

        self.english_abbr = {
            'IT': 'ай ти', 'AI': 'эй ай', 'GPU': 'жи пи ю', 'CPU': 'си пи ю',
            'ML': 'эм эл', 'API': 'эй пи ай', 'URL': 'ю ар эл',
            'HTTP': 'эйч ти ти пи', 'HTTPS': 'эйч ти ти пи эс',
            'HTML': 'эйч ти эм эл', 'CSS': 'си эс эс', 'PDF': 'пи ди эф',
            'USB': 'ю эс би', 'WiFi': 'вай фай', 'GPS': 'жи пи эс',
            'SMS': 'эс эм эс', 'SIM': 'сим', 'PIN': 'пин', 'ATM': 'эй ти эм',
            'VPN': 'ви пи эн', 'iOS': 'ай о эс', 'RAM': 'рам', 'ROM': 'ром',
            'SSD': 'эс эс ди', 'HDD': 'эйч ди ди', 'LED': 'лед', 'LCD': 'эл си ди',
            'TV': 'ти ви', 'DVD': 'ди ви ди', 'CD': 'си ди', 'PR': 'пи ар',
            'HR': 'эйч ар', 'CEO': 'си и о', 'ID': 'ай ди', 'OK': 'окей', 'QR': 'кю ар',
        }

        self.units = {
            'км': 'километр', 'м': 'метр', 'см': 'сантиметр', 'мм': 'миллиметр',
            'кг': 'килограмм', 'г': 'грамм', 'мг': 'миллиграмм', 'т': 'тонна',
            'л': 'литр', 'мл': 'миллилитр', 'га': 'гектар',
            'м2': 'квадрат метр', 'м3': 'куб метр', 'км2': 'квадрат километр',
            'см2': 'квадрат сантиметр', 'км/ч': 'километр саатына', 'м/с': 'метр секундасына',
            'кВт': 'киловатт', 'Вт': 'ватт', 'МВт': 'мегаватт',
            'ГГц': 'гигагерц', 'МГц': 'мегагерц', 'кГц': 'килогерц', 'Гц': 'герц',
            'ГБ': 'гигабайт', 'МБ': 'мегабайт', 'КБ': 'килобайт', 'ТБ': 'терабайт',
            'мин': 'мүнөт', 'сек': 'секунд', 'саат': 'саат',
            'km': 'километр', 'km²': 'квадрат километр', 'm': 'метр',
            'm²': 'квадрат метр', 'm³': 'куб метр', 'cm': 'сантиметр', 'mm': 'миллиметр',
            'kg': 'килограмм', 'g': 'грамм', 'mg': 'миллиграмм',
            'l': 'литр', 'ml': 'миллилитр', 'ha': 'гектар',
            'km/h': 'километр саатына', 'm/s': 'метр секундасына',
            'kW': 'киловатт', 'W': 'ватт', 'MW': 'мегаватт',
            'GHz': 'гигагерц', 'MHz': 'мегагерц', 'kHz': 'килогерц', 'Hz': 'герц',
            'GB': 'гигабайт', 'MB': 'мегабайт', 'KB': 'килобайт', 'TB': 'терабайт',
            'min': 'мүнөт', 'sec': 'секунд', 'h': 'саат',
        }

        self.currencies = {
            'сом': 'сом', '$': 'доллар', '€': 'евро', '₽': 'рубль',
            '¥': 'юань', '£': 'фунт', '₸': 'тенге', '₴': 'гривна',
        }

        self.large_numbers = {'млн': 'миллион', 'млрд': 'миллиард', 'трлн': 'триллион', 'тыс': 'миң'}

        self.symbols = {
            '%': 'пайыз', '№': 'номур', '@': 'эт белгиси', '&': 'жана',
            '§': 'параграф', '©': 'автордук укук', '®': 'катталган', '™': 'соода белгиси',
            '°': 'градус', '×': 'көбөйтүү', '÷': 'бөлүү', '±': 'кошуу кемитүү',
            '≈': 'болжол менен', '≠': 'барабар эмес', '≤': 'кичине же барабар',
            '≥': 'чоң же барабар', '<': 'кичине', '>': 'чоң', '=': 'барабар',
            '+': 'кошуу', '−': 'кемитүү', '—': '', '–': '', '/': 'сызыкча',
        }

        self.roman_values = [
            ('M', 1000), ('CM', 900), ('D', 500), ('CD', 400),
            ('C', 100), ('XC', 90), ('L', 50), ('XL', 40),
            ('X', 10), ('IX', 9), ('V', 5), ('IV', 4), ('I', 1),
        ]

        self.cardinal_suffixes = (
            'дык', 'дик', 'дүк', 'дук',
            'тык', 'тик', 'түк', 'тук',
            'лык', 'лик', 'лүк', 'лук',
            'луу', 'лүү', 'дуу', 'дүү', 'туу', 'түү',
        )

        self._suffix_base_map = {
            'га': 'га', 'ге': 'га', 'го': 'га', 'гө': 'га',
            'ка': 'ка', 'ке': 'ка', 'ко': 'ка', 'кө': 'ка',
            'да': 'да', 'де': 'да', 'до': 'да', 'дө': 'да',
            'та': 'та', 'те': 'та', 'то': 'та', 'тө': 'та',
        }

        self.time_suffixes = {
            ('нөл', 'га'): 'нөлгө', ('беш', 'га'): 'бешке', ('он', 'га'): 'онго',
            ('он беш', 'га'): 'он бешке', ('жыйырма', 'га'): 'жыйырмага',
            ('жыйырма беш', 'га'): 'жыйырма бешке', ('отуз', 'га'): 'отузга',
            ('отуз беш', 'га'): 'отуз бешке', ('кырк', 'га'): 'кыркка',
            ('кырк беш', 'га'): 'кырк бешке', ('элүү', 'га'): 'элүүгө',
            ('элүү беш', 'га'): 'элүү бешке',
            ('нөл', 'да'): 'нөлдө', ('беш', 'да'): 'беште', ('он', 'да'): 'ондо',
            ('он беш', 'да'): 'он беште', ('жыйырма', 'да'): 'жыйырмада',
            ('жыйырма беш', 'да'): 'жыйырма беште', ('отуз', 'да'): 'отузда',
            ('отуз беш', 'да'): 'отуз беште', ('кырк', 'да'): 'кыркта',
            ('кырк беш', 'да'): 'кырк беште', ('элүү', 'да'): 'элүүдө',
            ('элүү беш', 'да'): 'элүү беште',
        }

    # ================================================================
    # Кэш
    # ================================================================

    def _init_caches(self):
        self._number_cache = {}
        self._ordinal_cache = {}
        for i in range(101):
            self._number_cache[i] = self._compute_number_to_words(i)
            self._ordinal_cache[i] = self._compute_number_to_ordinal(i)

    # ================================================================
    # Прекомпиляция regex паттерндери
    # ================================================================

    def _compile_patterns(self):
        _sfx = r'(га|ге|го|гө|ка|ке|ко|кө|да|де|до|дө|та|те|то|тө)'

        # --- Кыскартуулар ---
        short_sorted = sorted(self.short_abbr.items(), key=lambda x: -len(x[0]))
        self._short_abbr_compiled = [
            (re.compile(rf'(?<![а-яөүңА-ЯӨҮҢA-Za-z0-9]){re.escape(a)}(?![а-яөүңА-ЯӨҮҢA-Za-z0-9])'), f)
            for a, f in short_sorted
        ]
        self._month_abbr_compiled = [
            (re.compile(rf'\b{re.escape(a)}\.?\b', re.IGNORECASE), f)
            for a, f in self.month_abbr.items()
        ]

        # --- Email, телефон ---
        self._p_email = re.compile(r'\b([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+)\.([a-zA-Z]{2,})\b')
        self._p_phone_996 = re.compile(r'\+996[\s-]?(\d{3})[\s-]?(\d{3})[\s-]?(\d{3})')
        self._p_phone_mobile = re.compile(r'\b(0\d{3})[\s-]?(\d{3})[\s-]?(\d{3})\b')
        self._p_phone_context = re.compile(
            r'(номер|номери|тел|телефон|звоните|позвоните|code|код|борбор|индекс|почтовый|WhatsApp|Telegram)'
            r'[\s::-]*(\d{3,6})\b', re.IGNORECASE)

        # --- Даталар ---
        self._p_date_ymd = re.compile(r'\b(\d{4})[./](\d{1,2})[./](\d{1,2})\b')
        self._p_date_invalid = re.compile(
            r'\b\d*\d{3,}\d*(?:[./]\d+)+\b|(?<!\d[./])\b\d+(?:[./]\d*\d{3,}\d*)+\b')
        self._p_date_year_word = re.compile(r'(\d{4})\s*-?\s*жылдын\s+(\d{1,2})\s*-?\s*(\w+)')
        self._p_date_dmy_comma = re.compile(r'\b(\d{1,2})\s*-?\s*(\w+),?\s*(\d{4})\s*[-\.]\s*жыл\b')
        self._p_date_dmy_space = re.compile(r'\b(\d{1,2})\s*-?\s*(\w+)\s+(\d{4})\s*[-\.]\s*жыл\b')
        self._p_date_iso_time = re.compile(r'(\d{4})-(\d{2})-(\d{2})\s+(\d{1,2}):(\d{2})')
        self._p_date_iso = re.compile(r'\b(\d{4})-(\d{1,2})-(\d{1,2})\b')
        self._p_date_text_month = re.compile(
            r'\b(\d{1,2})\s+(январь|февраль|март|апрель|май|июнь|июль|август|'
            r'сентябрь|октябрь|ноябрь|декабрь)\s+(\d{4})\b', re.IGNORECASE)
        self._p_date_dot = re.compile(r'\b(\d{1,2})\.(\d{1,2})\.(\d{2,4})\b')
        self._p_date_slash = re.compile(r'\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b')
        self._p_date_dash = re.compile(r'\b(\d{1,2})-(\d{1,2})-(\d{2,4})\b')

        # --- Жылдар ---
        self._p_year_range = re.compile(
            r'(\d{4})\s*[-–—]\s*(\d{4})\s*[-.]?\s*(жылдары|жылдар|жж|гг)\.?')
        self._p_year_single = re.compile(r'(\d{4})\s*[-.]?\s*(жылы|жыл|жж|гг|ж|г)\.?(?!\w)')

        # --- Убакыт ---
        self._p_time_colon_sfx = re.compile(rf'(\d{{1,2}}):(\d{{2}}){_sfx}')
        self._p_time_colon = re.compile(r'\b(\d{1,2}):(\d{2})\b')
        self._p_time_dot_ctx = re.compile(
            rf'((?:саат|убакыт)\s+)(\d{{1,2}})\.(\d{{2}}){_sfx}?')
        self._p_time_dot_sfx = re.compile(rf'\b(\d{{1,2}})\.(\d{{2}}){_sfx}')

        # --- Сандар "k" ---
        self._p_number_k = re.compile(r'\b(\d+)k\b')

        # --- Акча ---
        self._p_som_range = re.compile(
            r'(\d+(?:[,]\d+)?)\s*[-–—]\s*(\d+(?:[,]\d+)?)\s*сом\b')
        self._p_large_range = re.compile(
            r'(\d+(?:[,]\d+)?)\s*[-–—]\s*(\d+(?:[,]\d+)?)\s*(млн|млрд|трлн)\s*(сом|доллар|евро|рубль)')
        self._p_large_single = re.compile(
            r'(\d+(?:[,]\d+)?)\s*(млн|млрд|трлн)\s*(сом|доллар|евро|рубль)')
        self._p_som_spaced_dec = re.compile(r'(\d{1,3}(?:\s\d{3})*)[,.](\d{2})\s*сом')
        self._p_som_spaced = re.compile(r'(\d{1,3}(?:\s\d{3})+)\s*сом\b')
        self._p_som_simple = re.compile(r'(\d+)\s*сом\b')
        self._p_cur_before = re.compile(r'([$€₽£¥₸₴])(\d+(?:[,]\d+)?)')
        self._p_cur_after = re.compile(r'(\d+(?:[,]\d+)?)([$€₽£¥₸₴])')

        # --- Иреттик сандар ---
        self._p_num_dash_word = re.compile(r'(\d+)-([а-яөүңА-ЯӨҮҢ]+)')
        self._p_ordinal_sfx = re.compile(r'(\d+)\s*-?\s*(чи|чу|чү|нчи|нчу|нчү|ынчы|инчи|үнчү|унчу)')
        self._p_age = re.compile(r'(\d+)жашта')
        self._p_class = re.compile(r'(\d+)(чи|чу|чү)\s*класста')
        self._p_minutes = re.compile(r'(\d+)(мин|мүн|сек|саат)\b')
        self._p_course = re.compile(r'(\d+)\s*-?\s*курста')

        # --- Өлчөм бирдиктери (бириктирилген) ---
        units_alt = '|'.join(re.escape(k) for k in sorted(self.units, key=len, reverse=True))
        self._p_units_range = re.compile(
            rf'(\d+(?:[,]\d+)?)\s*[-–—]\s*(\d+(?:[,]\d+)?)\s*({units_alt})\b')
        self._p_units_single = re.compile(rf'(\d+(?:[,]\d+)?)\s*({units_alt})\b')

        # --- Пайыз ---
        self._p_pct_range = re.compile(r'(\d+(?:[,]\d+)?)\s*[-–—]\s*(\d+(?:[.,]\d+)?)\s*%')
        self._p_pct_single = re.compile(r'(\d+(?:[,]\d+)?)\s*%')

        # --- Кылымдар ---
        self._p_century_roman_range = re.compile(
            r'\b([IVXLCDM]{1,15})\s*[-–—]\s*([IVXLCDM]{1,15})\s*[-.]?\s*(кылымдары|кылымдар|кк)\.?')
        self._p_century_arabic_range = re.compile(
            r'(\d+)\s*[-–—]\s*(\d+)\s*[-.]?\s*(кылымдары|кылымдар|кк)\.?')

        # --- Математика ---
        self._p_math_mul_eq = re.compile(r'(\d+)\s*[×xXхХ*]\s*(\d+)\s*=\s*(\d+)')
        self._p_math_add_eq = re.compile(r'(\d+)\s*\+\s*(\d+)\s*=\s*(\d+)')
        self._p_math_sub_eq = re.compile(r'(\d+)\s*[-−–—]\s*(\d+)\s*=\s*(\d+)')
        self._p_math_div_eq = re.compile(r'(\d+)\s*/\s*(\d+)\s*=\s*(\d+)')
        self._p_num_range = re.compile(r'\b(\d+(?:[,]\d+)?)\s*[-–—]\s*(\d+(?:[,]\d+)?)\b')
        self._p_math_add = re.compile(r'(\d+)\s*\+\s*(\d+)')
        self._p_math_mul = re.compile(r'(\d+)\s*[×xXхХ*]\s*(\d+)')
        self._p_math_div = re.compile(r'(\d+)\s*/\s*(\d+)')

        # --- Аббревиатуралар (бириктирилген) ---
        kg_alt = '|'.join(re.escape(k) for k in sorted(self.kyrgyz_abbr, key=len, reverse=True))
        kg_sfx = (r'(нын|нун|нүн|нин|дын|дун|дүн|дин|тын|тун|түн|тин'
                  r'|га|ге|ка|ке|го|гө|ко|кө|да|де|та|те|до|дө|то|тө'
                  r'|дан|ден|тан|тен|дон|дөн|тон|төн|н|ы|и|у|ү)?')
        self._p_kg_abbr = re.compile(rf'\b({kg_alt}){kg_sfx}\b')
        en_alt = '|'.join(re.escape(k) for k in sorted(self.english_abbr, key=len, reverse=True))
        self._p_en_abbr = re.compile(rf'\b({en_alt})\b')

        # --- Адрестер ---
        self._p_addr_city = re.compile(r'\bг\.\s*')
        self._p_addr_district = re.compile(r'(\d+)\s*-?\s*кичи\s*район')
        self._p_fraction = re.compile(r'\b(\d+)/(\d+)\b')

        # --- Символдор ---
        self._p_apostrophe = re.compile(r"(\w+)'(\w+)")
        self._p_quotes_double = re.compile(r'[«»„"""]')
        self._p_quotes_single = re.compile(r"[''‚']")
        self._p_number_sign = re.compile(r'№\s*(\d+)')
        self._p_roman_century = re.compile(r'\b([IVXLCDM]{1,15})\s*к\.')
        self._p_roman_general = re.compile(r'(?<![a-zA-Z])\b([IVXLCDM]{1,15})\b(?!\.|\s*[a-zA-Z])')

        # --- Калган сандар ---
        self._p_decimal = re.compile(r'\b(\d+[,]\d+)\b')
        self._p_spaced_num = re.compile(r'\b\d{1,3}(?:\s\d{3})+\b')
        self._p_simple_num = re.compile(r'\b(\d+)\b')
        self._p_letter_digit = re.compile(r'([а-яөүңА-ЯӨҮҢa-zA-Z])(\d+)')
        self._p_sep_nums = re.compile(r'\d+[./]\d+(?:[./]\d+)*')
        self._p_remaining = re.compile(r'\d+')
        self._p_spaces = re.compile(r'\s+')

    # ================================================================
    # Санды сөзгө айландыруу
    # ================================================================

    def digit_to_word(self, digit):
        _map = {'0': 'нөл', '1': 'бир', '2': 'эки', '3': 'үч', '4': 'төрт',
                '5': 'беш', '6': 'алты', '7': 'жети', '8': 'сегиз', '9': 'тогуз'}
        return _map.get(digit, digit)

    def digits_to_words(self, number_string):
        return ' '.join(self.digit_to_word(d) for d in number_string if d.isdigit())

    def _compute_number_to_words(self, num):
        if num == 0:
            return 'нөл'
        if num < 0:
            return 'минус ' + self._compute_number_to_words(abs(num))

        parts = []
        for threshold, label in ((1_000_000_000_000, 'триллион'),
                                 (1_000_000_000, 'миллиард'),
                                 (1_000_000, 'миллион'),
                                 (1_000, 'миң')):
            if num >= threshold:
                parts.append(self._compute_number_to_words(num // threshold))
                parts.append(label)
                num %= threshold

        if num >= 100:
            parts.append(self.hundreds[num // 100])
            num %= 100
        if num >= 10:
            parts.append(self.tens[num // 10])
            num %= 10
        if num > 0:
            parts.append(self.ones[num])

        return ' '.join(parts)

    def number_to_words(self, num):
        if 0 <= num <= 100:
            return self._number_cache[num]
        return self._compute_number_to_words(num)

    def _compute_number_to_ordinal(self, num):
        if num >= 1000:
            thousands = num // 1000
            remainder = num % 1000
            if remainder == 0:
                return self._compute_number_to_words(thousands) + ' миңинчи'
            return self._compute_number_to_words(thousands) + ' миң ' + self._compute_number_to_ordinal(remainder)

        if num >= 100:
            remainder = num % 100
            if remainder == 0:
                return self.hundreds[num // 100] + 'үнчү'
            return self.hundreds[num // 100] + ' ' + self._compute_number_to_ordinal(remainder)

        if num >= 10:
            remainder = num % 10
            if remainder == 0:
                return self.ordinal_tens[num // 10]
            return self.tens[num // 10] + ' ' + self.ordinal_ones[remainder]

        if num < len(self.ordinal_ones):
            return self.ordinal_ones[num]
        return self._compute_number_to_words(num) + 'инчи'

    def number_to_ordinal(self, num):
        if 0 <= num <= 100:
            return self._ordinal_cache[num]
        return self._compute_number_to_ordinal(num)

    def roman_to_number(self, roman):
        result = 0
        i = 0
        roman = roman.upper()
        for numeral, value in self.roman_values:
            while roman[i:i + len(numeral)] == numeral:
                result += value
                i += len(numeral)
        return result

    def decimal_to_words(self, num_str):
        parts = num_str.split(',')
        whole = int(parts[0]) if parts[0] else 0
        result = 'нөл' if whole == 0 else self.number_to_words(whole)

        if len(parts) > 1 and parts[1]:
            decimal = parts[1]
            decimal_places = {1: 'ондон', 2: 'жүздөн', 3: 'миңден',
                              4: 'он миңден', 5: 'жүз миңден', 6: 'миллиондон'}
            place = decimal_places.get(len(decimal), '')
            decimal_num = self.number_to_words(int(decimal))
            result += ' бүтүн'
            if place:
                result += f' {place} {decimal_num}'
            else:
                result += f' {decimal_num}'

        return result

    # ================================================================
    # Сингармонизм
    # ================================================================

    def apply_suffix_harmony(self, word, suffix):
        if not suffix:
            return word

        word_lower = word.lower().strip()
        if not word_lower:
            return word + suffix

        back_rounded = 'оу'
        back_unrounded = 'аы'
        front_rounded = 'өү'
        front_unrounded = 'еи'
        all_vowels = back_rounded + back_unrounded + front_rounded + front_unrounded
        voiceless = 'кпстфхцчшщ'

        last_char = word_lower[-1]
        last_vowel = ''
        for ch in reversed(word_lower):
            if ch in all_vowels:
                last_vowel = ch
                break

        is_back_rounded = last_vowel in back_rounded
        is_back_unrounded = last_vowel in back_unrounded
        is_front_rounded = last_vowel in front_rounded
        is_front_unrounded = last_vowel in front_unrounded
        ends_vowel = last_char in all_vowels
        ends_voiceless = last_char in voiceless

        new_suffix = suffix
        fc = suffix[0]
        if fc in 'дт':
            new_suffix = ('н' if ends_vowel else 'т' if ends_voiceless else 'д') + suffix[1:]
        elif fc in 'гк':
            new_suffix = ('н' if ends_vowel else 'к' if ends_voiceless else 'г') + suffix[1:]

        out = []
        for ch in new_suffix:
            if ch == 'а':
                if is_front_rounded:
                    out.append('ө')
                elif is_front_unrounded:
                    out.append('е')
                elif is_back_rounded and not ends_vowel:
                    out.append('о')
                else:
                    out.append('а')
            elif ch == 'ы':
                if is_front_rounded:
                    out.append('ү')
                elif is_front_unrounded:
                    out.append('и')
                elif is_back_rounded:
                    out.append('у')
                else:
                    out.append('ы')
            elif ch == 'о':
                out.append('ө' if is_front_rounded else 'о')
            elif ch == 'у':
                out.append('ү' if is_front_rounded else 'у')
            elif ch == 'ө':
                out.append('о' if is_back_rounded else 'ө')
            elif ch == 'ү':
                out.append('у' if is_back_rounded else 'ү')
            else:
                out.append(ch)

        return word + ''.join(out)

    # ================================================================
    # Убакыт хелпери
    # ================================================================

    def _time_to_words(self, hours, minutes_str, suffix=None):
        hours_word = self.number_to_words(hours)

        if not suffix:
            if minutes_str == '00':
                return hours_word
            if minutes_str.startswith('0'):
                return f"{hours_word} нөл {self.number_to_words(int(minutes_str[1]))}"
            return f"{hours_word} {self.number_to_words(int(minutes_str))}"

        base = self._suffix_base_map.get(suffix, suffix)

        if minutes_str == '00':
            return self.apply_suffix_harmony(hours_word, base)

        if minutes_str.startswith('0'):
            time_str = f"{hours_word} нөл {self.number_to_words(int(minutes_str[1]))}"
            return self.apply_suffix_harmony(time_str, base)

        minutes_word = self.number_to_words(int(minutes_str))
        hardcoded = self.time_suffixes.get((minutes_word, base))
        if hardcoded:
            return f"{hours_word} {hardcoded}"

        return self.apply_suffix_harmony(f"{hours_word} {minutes_word}", base)

    # ================================================================
    # Дата хелперлери
    # ================================================================

    def _format_date_ymd(self, m):
        year_full = int(m.group(1))
        num2, num3 = int(m.group(2)), int(m.group(3))

        if num2 <= 12:
            month_num, day = str(num2).zfill(2), num3
        elif num3 <= 12:
            month_num, day = str(num3).zfill(2), num2
        else:
            return m.group(0)

        month = self.months.get(month_num, month_num)
        return f"{self.number_to_ordinal(year_full)} жыл {self.number_to_ordinal(day)} {month}"

    def _format_date_dmy(self, m):
        num1, num2 = int(m.group(1)), int(m.group(2))
        year_str = m.group(3)

        if num2 > 12 and num1 <= 12:
            month_num, day = str(num1).zfill(2), num2
        else:
            day, month_num = num1, str(num2).zfill(2)

        if len(year_str) == 2:
            y = int(year_str)
            year_full = (self.CENTURY_2000 if y < self.YEAR_THRESHOLD else self.CENTURY_1900) + y
        else:
            year_full = int(year_str)

        month = self.months.get(month_num, month_num)
        return f"{self.number_to_ordinal(year_full)} жыл {self.number_to_ordinal(day)} {month}"

    # ================================================================
    # Нормализация этаптары
    # ================================================================

    def _normalize_short_abbr(self, text):
        for pat, full in self._short_abbr_compiled:
            text = pat.sub(full, text)
        for pat, full in self._month_abbr_compiled:
            text = pat.sub(full, text)
        return text

    def _normalize_contacts(self, text):
        text = self._p_email.sub(
            lambda m: f"{m.group(1)} эт белгиси {m.group(2)} чекит {m.group(3)}", text)
        text = self._p_phone_996.sub(
            lambda m: (f"плюс тогуз тогуз алты {self.digits_to_words(m.group(1))} "
                       f"{self.digits_to_words(m.group(2))} {self.digits_to_words(m.group(3))}"), text)
        text = self._p_phone_mobile.sub(
            lambda m: (f"{self.digits_to_words(m.group(1))} {self.digits_to_words(m.group(2))} "
                       f"{self.digits_to_words(m.group(3))}"), text)
        text = self._p_phone_context.sub(
            lambda m: f"{m.group(1)} {self.digits_to_words(m.group(2))}", text)
        return text

    def _normalize_dates(self, text):
        text = self._p_date_ymd.sub(self._format_date_ymd, text)

        def _convert_invalid(m):
            return ' '.join(self.number_to_words(int(p)) for p in re.split(r'[./]', m.group(0)) if p)
        text = self._p_date_invalid.sub(_convert_invalid, text)

        text = self._p_date_year_word.sub(
            lambda m: f"{self.number_to_ordinal(int(m.group(1)))} жылдын "
                       f"{self.number_to_ordinal(int(m.group(2)))} {m.group(3)}", text)

        text = self._p_date_dmy_comma.sub(
            lambda m: f"{self.number_to_words(int(m.group(1)))} {m.group(2)} "
                       f"{self.number_to_ordinal(int(m.group(3)))} жыл", text)

        text = self._p_date_dmy_space.sub(
            lambda m: f"{self.number_to_words(int(m.group(1)))} {m.group(2)} "
                       f"{self.number_to_ordinal(int(m.group(3)))} жыл", text)

        text = self._p_date_iso_time.sub(
            lambda m: (f"{self.number_to_words(int(m.group(1)))} жылдын "
                       f"{self.months.get(m.group(2), m.group(2))} айынын "
                       f"{self.number_to_words(int(m.group(3)))} күнү саат "
                       f"{self.number_to_words(int(m.group(4)))} "
                       f"{self.number_to_words(int(m.group(5)))}"), text)

        text = self._p_date_iso.sub(self._format_date_ymd, text)

        text = self._p_date_text_month.sub(
            lambda m: (f"{self.number_to_ordinal(int(m.group(1)))} {m.group(2).lower()} "
                       f"{self.number_to_ordinal(int(m.group(3)))} жыл"), text)

        text = self._p_date_dot.sub(self._format_date_dmy, text)
        text = self._p_date_slash.sub(self._format_date_dmy, text)
        text = self._p_date_dash.sub(self._format_date_dmy, text)
        return text

    def _normalize_years(self, text):
        text = self._p_year_range.sub(
            lambda m: f"{self.number_to_ordinal(int(m.group(1)))} "
                       f"{self.number_to_ordinal(int(m.group(2)))} жылдар", text)
        text = self._p_year_single.sub(
            lambda m: f"{self.number_to_ordinal(int(m.group(1)))} жыл"
                       + ('ы' if m.group(2) == 'жылы' else ''), text)
        return text

    def _normalize_time(self, text):
        text = self._p_time_colon_sfx.sub(
            lambda m: self._time_to_words(int(m.group(1)), m.group(2), m.group(3)), text)

        text = self._p_time_colon.sub(
            lambda m: self._time_to_words(int(m.group(1)), m.group(2)), text)

        def _dot_ctx(m):
            prefix = m.group(1) or ''
            return prefix + self._time_to_words(int(m.group(2)), m.group(3), m.group(4))
        text = self._p_time_dot_ctx.sub(_dot_ctx, text)
        return text

    def _normalize_currency(self, text):
        text = self._p_number_k.sub(
            lambda m: f"{self.number_to_words(int(m.group(1)))} миң", text)

        text = self._p_som_range.sub(
            lambda m: f"{self.decimal_to_words(m.group(1))} {self.decimal_to_words(m.group(2))} сом", text)

        text = self._p_large_range.sub(
            lambda m: (f"{self.decimal_to_words(m.group(1))} {self.decimal_to_words(m.group(2))} "
                       f"{self.large_numbers.get(m.group(3), m.group(3))} {m.group(4)}"), text)

        text = self._p_large_single.sub(
            lambda m: (f"{self.decimal_to_words(m.group(1))} "
                       f"{self.large_numbers.get(m.group(2), m.group(2))} {m.group(3)}"), text)

        text = self._p_som_spaced_dec.sub(
            lambda m: (f"{self.number_to_words(int(m.group(1).replace(' ', '')))} сом "
                       f"{self.number_to_words(int(m.group(2)))} тыйын"), text)

        text = self._p_som_spaced.sub(
            lambda m: f"{self.number_to_words(int(m.group(1).replace(' ', '')))} сом", text)

        text = self._p_som_simple.sub(
            lambda m: f"{self.number_to_words(int(m.group(1)))} сом", text)

        text = self._p_cur_before.sub(
            lambda m: f"{self.decimal_to_words(m.group(2))} {self.currencies[m.group(1)]}", text)
        text = self._p_cur_after.sub(
            lambda m: f"{self.decimal_to_words(m.group(1))} {self.currencies[m.group(2)]}", text)
        return text

    def _normalize_time_dot_sfx(self, text):
        text = self._p_time_dot_sfx.sub(
            lambda m: self._time_to_words(int(m.group(1)), m.group(2), m.group(3)), text)
        return text

    def _normalize_ordinals(self, text):
        def _num_dash_word(m):
            num, word = int(m.group(1)), m.group(2)
            for sfx in self.cardinal_suffixes:
                if word.lower().find(sfx) >= 2:
                    return f"{self.number_to_words(num)} {word}"
            return f"{self.number_to_ordinal(num)} {word}"

        text = self._p_num_dash_word.sub(_num_dash_word, text)

        text = self._p_ordinal_sfx.sub(
            lambda m: self.number_to_ordinal(int(m.group(1))), text)

        text = self._p_age.sub(
            lambda m: f"{self.number_to_words(int(m.group(1)))} жашта", text)

        text = self._p_class.sub(
            lambda m: f"{self.number_to_ordinal(int(m.group(1)))} класста", text)

        text = self._p_minutes.sub(
            lambda m: f"{self.number_to_words(int(m.group(1)))} {self.units.get(m.group(2), m.group(2))}", text)

        text = self._p_course.sub(
            lambda m: f"{self.number_to_ordinal(int(m.group(1)))} курста", text)
        return text

    def _normalize_units(self, text):
        text = self._p_units_range.sub(
            lambda m: (f"{self.decimal_to_words(m.group(1))} "
                       f"{self.decimal_to_words(m.group(2))} {self.units[m.group(3)]}"), text)
        text = self._p_units_single.sub(
            lambda m: f"{self.decimal_to_words(m.group(1))} {self.units[m.group(2)]}", text)
        return text

    def _normalize_percentages(self, text):
        text = self._p_pct_range.sub(
            lambda m: f"{self.decimal_to_words(m.group(1))} {self.decimal_to_words(m.group(2))} пайыз", text)
        text = self._p_pct_single.sub(
            lambda m: f"{self.decimal_to_words(m.group(1))} пайыз", text)
        return text

    def _normalize_centuries(self, text):
        def _roman_range(m):
            try:
                n1 = self.roman_to_number(m.group(1))
                n2 = self.roman_to_number(m.group(2))
            except (ValueError, IndexError):
                return m.group(0)
            word = 'кылымдары' if m.group(3) == 'кылымдары' else 'кылымдар'
            return f"{self.number_to_ordinal(n1)} {self.number_to_ordinal(n2)} {word}"

        text = self._p_century_roman_range.sub(_roman_range, text)

        text = self._p_century_arabic_range.sub(
            lambda m: (f"{self.number_to_ordinal(int(m.group(1)))} "
                       f"{self.number_to_ordinal(int(m.group(2)))} "
                       f"{'кылымдары' if m.group(3) == 'кылымдары' else 'кылымдар'}"), text)
        return text

    def _normalize_math_and_ranges(self, text):
        text = self._p_math_mul_eq.sub(
            lambda m: (f"{self.number_to_words(int(m.group(1)))} көбөйтүү "
                       f"{self.number_to_words(int(m.group(2)))} барабар "
                       f"{self.number_to_words(int(m.group(3)))}"), text)
        text = self._p_math_add_eq.sub(
            lambda m: (f"{self.number_to_words(int(m.group(1)))} кошуу "
                       f"{self.number_to_words(int(m.group(2)))} барабар "
                       f"{self.number_to_words(int(m.group(3)))}"), text)
        text = self._p_math_sub_eq.sub(
            lambda m: (f"{self.number_to_words(int(m.group(1)))} кемитүү "
                       f"{self.number_to_words(int(m.group(2)))} барабар "
                       f"{self.number_to_words(int(m.group(3)))}"), text)
        text = self._p_math_div_eq.sub(
            lambda m: (f"{self.number_to_words(int(m.group(1)))} бөлүү "
                       f"{self.number_to_words(int(m.group(2)))} барабар "
                       f"{self.number_to_words(int(m.group(3)))}"), text)

        text = self._p_num_range.sub(
            lambda m: f"{self.decimal_to_words(m.group(1))} {self.decimal_to_words(m.group(2))}", text)

        text = self._p_math_add.sub(
            lambda m: f"{self.number_to_words(int(m.group(1)))} кошуу {self.number_to_words(int(m.group(2)))}", text)
        text = self._p_math_mul.sub(
            lambda m: f"{self.number_to_words(int(m.group(1)))} көбөйтүү {self.number_to_words(int(m.group(2)))}", text)
        text = self._p_math_div.sub(
            lambda m: f"{self.number_to_words(int(m.group(1)))} бөлүү {self.number_to_words(int(m.group(2)))}", text)
        return text

    def _normalize_named_abbr(self, text):
        def _kg_replace(m):
            full = self.kyrgyz_abbr[m.group(1)]
            return self.apply_suffix_harmony(full, m.group(2)) if m.group(2) else full
        text = self._p_kg_abbr.sub(_kg_replace, text)

        text = self._p_en_abbr.sub(lambda m: self.english_abbr[m.group(1)], text)
        return text

    def _normalize_addresses(self, text):
        text = self._p_addr_city.sub('', text)

        text = self._p_addr_district.sub(
            lambda m: f"{self.number_to_ordinal(int(m.group(1)))} кичи район", text)

        def _fraction(m):
            numer = self.number_to_words(int(m.group(1)))
            denom = self.number_to_words(int(m.group(2)))
            return f"{self.apply_suffix_harmony(denom, 'дан')} {numer}"
        text = self._p_fraction.sub(_fraction, text)
        return text

    def _normalize_symbols(self, text):
        text = self._p_apostrophe.sub(r'\1\2', text)

        text = self._p_quotes_double.sub('', text)
        text = self._p_quotes_single.sub('', text)

        text = self._p_number_sign.sub(
            lambda m: f"номур {self.number_to_words(int(m.group(1)))}", text)

        text = re.sub(r'(?<=[,\s])%(?=[,\s]|$)', 'пайыз', text)
        text = re.sub(r'(?<=[,\s])№(?=[,\s]|$)', 'номур', text)
        text = re.sub(r'(?<=[,\s])@(?=[,\s]|$)', 'эт белгиси', text)
        text = re.sub(r'(?<=[,\s])&(?=[,\s]|$)', 'жана', text)

        def _roman_century(m):
            try:
                return f"{self.number_to_ordinal(self.roman_to_number(m.group(1)))} кылым"
            except (ValueError, IndexError):
                return m.group(0)
        text = self._p_roman_century.sub(_roman_century, text)

        text = self._p_roman_general.sub(
            lambda m: self.number_to_ordinal(self.roman_to_number(m.group(0))), text)
        return text

    def _normalize_remaining_numbers(self, text):
        text = self._p_decimal.sub(lambda m: self.decimal_to_words(m.group(1)), text)

        text = self._p_spaced_num.sub(
            lambda m: self.number_to_words(int(m.group(0).replace(' ', ''))), text)

        text = self._p_simple_num.sub(lambda m: self.number_to_words(int(m.group(1))), text)

        text = self._p_letter_digit.sub(r'\1 \2', text)

        def _sep(m):
            return ' '.join(self.number_to_words(int(p)) for p in re.split(r'[./]', m.group(0)) if p)
        text = self._p_sep_nums.sub(_sep, text)

        text = self._p_remaining.sub(lambda m: self.number_to_words(int(m.group(0))), text)
        return text

    # ================================================================
    # Негизги нормализация
    # ================================================================

    def normalize(self, text):
        text = self._normalize_short_abbr(text)
        text = self._normalize_contacts(text)
        text = self._normalize_dates(text)
        text = self._normalize_years(text)
        text = self._normalize_time(text)
        text = self._normalize_currency(text)
        text = self._normalize_time_dot_sfx(text)
        text = self._normalize_ordinals(text)
        text = self._normalize_units(text)
        text = self._normalize_percentages(text)
        text = self._normalize_centuries(text)
        text = self._normalize_math_and_ranges(text)
        text = self._normalize_named_abbr(text)
        text = self._normalize_addresses(text)
        text = self._normalize_symbols(text)
        text = self._normalize_remaining_numbers(text)
        return self._p_spaces.sub(' ', text).strip()


def main():
    normalizer = KyrgyzTextNormalizer()

    if len(sys.argv) > 1:
        input_text = ' '.join(sys.argv[1:])
        print(normalizer.normalize(input_text))
    else:
        print("Кыргызча текст нормализатор (TTS үчүн)")
        print("=" * 50)
        print("Текст киргизиңиз (чыгуу үчүн 'exit'):")
        print()

        while True:
            try:
                user_input = input("> ")
                if user_input.lower() in ('exit', 'quit', 'чыгуу'):
                    break
                if user_input.strip():
                    print(f"Жыйынтык: {normalizer.normalize(user_input)}")
                    print()
            except (KeyboardInterrupt, EOFError):
                print("\nЧыгуу...")
                break


if __name__ == "__main__":
    main()
