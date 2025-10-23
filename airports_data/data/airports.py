"""
База данных аэропортов для калькулятора FDP
"""

AIRPORTS_DATA = {
    # Беларусь
    "UMMS": {"iata": "MSQ", "city": "Минск", "name": "Минск-2", "country": "Беларусь", "timezone": "Europe/Minsk"},
    "UMII": {"iata": "VTB", "city": "Витебск", "name": "Витебск", "country": "Беларусь", "timezone": "Europe/Minsk"},
    "UMGG": {"iata": "GME", "city": "Гомель", "name": "Гомель", "country": "Беларусь", "timezone": "Europe/Minsk"},
    "UMBB": {"iata": "BQT", "city": "Брест", "name": "Брест", "country": "Беларусь", "timezone": "Europe/Minsk"},
    "UMMG": {"iata": "MVQ", "city": "Могилев", "name": "Могилев", "country": "Беларусь", "timezone": "Europe/Minsk"},
    "UMKG": {"iata": "GNA", "city": "Гродно", "name": "Гродно", "country": "Беларусь", "timezone": "Europe/Minsk"},
    
    # Россия
    "UEEE": {"iata": "YKS", "city": "Якутск", "name": "Якутск", "country": "Россия", "timezone": "Asia/Yakutsk"},
    "UWKD": {"iata": "KZN", "city": "Казань", "name": "Казань", "country": "Россия", "timezone": "Europe/Moscow"},
    "UUDD": {"iata": "DME", "city": "Москва", "name": "Домодедово", "country": "Россия", "timezone": "Europe/Moscow"},
    "URSS": {"iata": "AER", "city": "Сочи", "name": "Сочи", "country": "Россия", "timezone": "Europe/Moscow"},
    "UUBW": {"iata": "VKO", "city": "Москва", "name": "Внуково", "country": "Россия", "timezone": "Europe/Moscow"},
    "UUEE": {"iata": "SVO", "city": "Москва", "name": "Шереметьево", "country": "Россия", "timezone": "Europe/Moscow"},
    "URRR": {"iata": "ROV", "city": "Ростов-на-Дону", "name": "Ростов-на-Дону", "country": "Россия", "timezone": "Europe/Moscow"},
    "UWWW": {"iata": "KUF", "city": "Самара", "name": "Курумоч", "country": "Россия", "timezone": "Europe/Samara"},
    "UUYY": {"iata": "SCW", "city": "Сыктывкар", "name": "Сыктывкар", "country": "Россия", "timezone": "Europe/Moscow"},
    "UHMA": {"iata": "DYR", "city": "Анадырь", "name": "Анадырь", "country": "Россия", "timezone": "Asia/Anadyr"},
    "UMMM": {"iata": "MMK", "city": "Мурманск", "name": "Мурманск", "country": "Россия", "timezone": "Europe/Moscow"},
    "URKA": {"iata": "KRR", "city": "Краснодар", "name": "Краснодар", "country": "Россия", "timezone": "Europe/Moscow"},
    "UWUU": {"iata": "UFA", "city": "Уфа", "name": "Уфа", "country": "Россия", "timezone": "Asia/Yekaterinburg"},
    "USSS": {"iata": "SVX", "city": "Екатеринбург", "name": "Кольцово", "country": "Россия", "timezone": "Asia/Yekaterinburg"},
    "UUWW": {"iata": "VOZ", "city": "Воронеж", "name": "Воронеж", "country": "Россия", "timezone": "Europe/Moscow"},
    "UMMC": {"iata": "CEE", "city": "Череповец", "name": "Череповец", "country": "Россия", "timezone": "Europe/Moscow"},
    
    # Украина
    "UKBB": {"iata": "KBP", "city": "Киев", "name": "Борисполь", "country": "Украина", "timezone": "Europe/Kiev"},
    "UKLL": {"iata": "LWO", "city": "Львов", "name": "Львов", "country": "Украина", "timezone": "Europe/Kiev"},
    "UKDD": {"iata": "DNK", "city": "Днепр", "name": "Днепр", "country": "Украина", "timezone": "Europe/Kiev"},
    "UKHH": {"iata": "HRK", "city": "Харьков", "name": "Харьков", "country": "Украина", "timezone": "Europe/Kiev"},
    "UKOO": {"iata": "ODS", "city": "Одесса", "name": "Одесса", "country": "Украина", "timezone": "Europe/Kiev"},
    "UKKK": {"iata": "KGO", "city": "Кривой Рог", "name": "Кривой Рог", "country": "Украина", "timezone": "Europe/Kiev"},
    "UKDE": {"iata": "OZH", "city": "Запорожье", "name": "Запорожье", "country": "Украина", "timezone": "Europe/Kiev"},
    
    # Казахстан
    "UAKD": {"iata": "ALA", "city": "Алматы", "name": "Алматы", "country": "Казахстан", "timezone": "Asia/Almaty"},
    "UACC": {"iata": "TSE", "city": "Астана", "name": "Нур-Султан", "country": "Казахстан", "timezone": "Asia/Almaty"},
    "UASK": {"iata": "CIT", "city": "Шымкент", "name": "Шымкент", "country": "Казахстан", "timezone": "Asia/Almaty"},
    "UATT": {"iata": "GUW", "city": "Атырау", "name": "Атырау", "country": "Казахстан", "timezone": "Asia/Aqtobe"},
    "UAAH": {"iata": "SCO", "city": "Актау", "name": "Актау", "country": "Казахстан", "timezone": "Asia/Aqtobe"},
    "UAKK": {"iata": "KGF", "city": "Караганда", "name": "Караганда", "country": "Казахстан", "timezone": "Asia/Almaty"},
    "UACP": {"iata": "PPK", "city": "Петропавловск", "name": "Петропавловск", "country": "Казахстан", "timezone": "Asia/Almaty"},
    "UAOO": {"iata": "URA", "city": "Уральск", "name": "Уральск", "country": "Казахстан", "timezone": "Asia/Aqtobe"},
    "UARR": {"iata": "AKX", "city": "Актобе", "name": "Актобе", "country": "Казахстан", "timezone": "Asia/Aqtobe"},
    "UAKZ": {"iata": "KSN", "city": "Костанай", "name": "Костанай", "country": "Казахстан", "timezone": "Asia/Almaty"},
    
    # Узбекистан
    "UTTT": {"iata": "TAS", "city": "Ташкент", "name": "Ташкент", "country": "Узбекистан", "timezone": "Asia/Tashkent"},
    "UTSS": {"iata": "SKD", "city": "Самарканд", "name": "Самарканд", "country": "Узбекистан", "timezone": "Asia/Tashkent"},
    "UTSB": {"iata": "BHK", "city": "Бухара", "name": "Бухара", "country": "Узбекистан", "timezone": "Asia/Tashkent"},
    "UTKN": {"iata": "KSQ", "city": "Карши", "name": "Карши", "country": "Узбекистан", "timezone": "Asia/Tashkent"},
    "UTNN": {"iata": "NVI", "city": "Навои", "name": "Навои", "country": "Узбекистан", "timezone": "Asia/Tashkent"},
    "UTNU": {"iata": "NCU", "city": "Нукус", "name": "Нукус", "country": "Узбекистан", "timezone": "Asia/Tashkent"},
    "UTFF": {"iata": "FEG", "city": "Фергана", "name": "Фергана", "country": "Узбекистан", "timezone": "Asia/Tashkent"},
    
    # Кыргызстан
    "UAFM": {"iata": "FRU", "city": "Бишкек", "name": "Манас", "country": "Кыргызстан", "timezone": "Asia/Bishkek"},
    "UAFO": {"iata": "OSS", "city": "Ош", "name": "Ош", "country": "Кыргызстан", "timezone": "Asia/Bishkek"},
    "UAFN": {"iata": "NAR", "city": "Нарын", "name": "Нарын", "country": "Кыргызстан", "timezone": "Asia/Bishkek"},
    
    # Таджикистан
    "UTDD": {"iata": "DYU", "city": "Душанбе", "name": "Душанбе", "country": "Таджикистан", "timezone": "Asia/Dushanbe"},
    "UTDK": {"iata": "TJU", "city": "Куляб", "name": "Куляб", "country": "Таджикистан", "timezone": "Asia/Dushanbe"},
    "UTDL": {"iata": "LBD", "city": "Худжанд", "name": "Худжанд", "country": "Таджикистан", "timezone": "Asia/Dushanbe"},
    
    # Туркменистан
    "UTAA": {"iata": "ASB", "city": "Ашхабад", "name": "Ашхабад", "country": "Туркменистан", "timezone": "Asia/Ashgabat"},
    "UTAK": {"iata": "CRZ", "city": "Туркменабад", "name": "Туркменабад", "country": "Туркменистан", "timezone": "Asia/Ashgabat"},
    "UTAM": {"iata": "MYP", "city": "Мары", "name": "Мары", "country": "Туркменистан", "timezone": "Asia/Ashgabat"},
    "UTAT": {"iata": "KRW", "city": "Туркменбаши", "name": "Туркменбаши", "country": "Туркменистан", "timezone": "Asia/Ashgabat"},
    
    # Армения
    "UDYZ": {"iata": "EVN", "city": "Ереван", "name": "Звартноц", "country": "Армения", "timezone": "Asia/Yerevan"},
    "UDLS": {"iata": "LWN", "city": "Гюмри", "name": "Ширак", "country": "Армения", "timezone": "Asia/Yerevan"},
    
    # Азербайджан
    "UBBB": {"iata": "GYD", "city": "Баку", "name": "Гейдар Алиев", "country": "Азербайджан", "timezone": "Asia/Baku"},
    "UBBG": {"iata": "KVD", "city": "Гянджа", "name": "Гянджа", "country": "Азербайджан", "timezone": "Asia/Baku"},
    "UBBN": {"iata": "NAJ", "city": "Нахичевань", "name": "Нахичевань", "country": "Азербайджан", "timezone": "Asia/Baku"},
    
    # Грузия
    "UGGG": {"iata": "TBS", "city": "Тбилиси", "name": "Тбилиси", "country": "Грузия", "timezone": "Asia/Tbilisi"},
    "UGSB": {"iata": "BUS", "city": "Батуми", "name": "Батуми", "country": "Грузия", "timezone": "Asia/Tbilisi"},
    "UGKO": {"iata": "KUT", "city": "Кутаиси", "name": "Кутаиси", "country": "Грузия", "timezone": "Asia/Tbilisi"},
    "UGSS": {"iata": "SUI", "city": "Сухуми", "name": "Сухуми", "country": "Грузия", "timezone": "Asia/Tbilisi"},
    
    # Молдова
    "LUKK": {"iata": "KIV", "city": "Кишинев", "name": "Кишинев", "country": "Молдова", "timezone": "Europe/Chisinau"},
    
    # Европа (близлежащие)
    "EPWA": {"iata": "WAW", "city": "Варшава", "name": "Шопен", "country": "Польша", "timezone": "Europe/Warsaw"},
    "LOWW": {"iata": "VIE", "city": "Вена", "name": "Швехат", "country": "Австрия", "timezone": "Europe/Vienna"},
    "LZIB": {"iata": "BTS", "city": "Братислава", "name": "Братислава", "country": "Словакия", "timezone": "Europe/Bratislava"},
    "LKPR": {"iata": "PRG", "city": "Прага", "name": "Вацлав Гавел", "country": "Чехия", "timezone": "Europe/Prague"},
    "LHBP": {"iata": "BUD", "city": "Будапешт", "name": "Ферихедь", "country": "Венгрия", "timezone": "Europe/Budapest"},
}


def get_airports_data():
    """Возвращает базу данных аэропортов"""
    return AIRPORTS_DATA


def get_airport_info(icao_code):
    """Возвращает информацию об аэропорте по ICAO коду"""
    return AIRPORTS_DATA.get(icao_code.upper())


def get_airport_timezone(icao_code):
    """Возвращает часовой пояс аэропорта по ICAO коду"""
    airport_info = get_airport_info(icao_code)
    return airport_info.get('timezone') if airport_info else None
