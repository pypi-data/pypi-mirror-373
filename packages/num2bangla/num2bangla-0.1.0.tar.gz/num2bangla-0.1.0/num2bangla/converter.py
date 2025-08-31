class TakaConverter:
    def __init__(self, lang="en", currency="BDT", extension="Only", decimal_style="default", numerical_digits="en"):
        self.lang = lang
        self.currency = currency
        self.extension = extension
        self.decimal_style = decimal_style  # Can be "default" or "decimal"
        self.numerical_digits = numerical_digits  # Can be "en" or "bn"
        
        # Bangla numerical digits mapping
        self.bn_digits = {
            '0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪',
            '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯',
            '.': '.'
        }
        
        self.bn_numbers = {
            0: "শূন্য", 1: "এক", 2: "দুই", 3: "তিন", 4: "চার", 5: "পাঁচ",
            6: "ছয়", 7: "সাত", 8: "আট", 9: "নয়", 10: "দশ",
            11: "এগারো", 12: "বারো", 13: "তেরো", 14: "চৌদ্দ", 15: "পনেরো",
            16: "ষোল", 17: "সতেরো", 18: "আঠারো", 19: "উনিশ", 20: "বিশ",
            21: "একুশ", 22: "বাইশ", 23: "তেইশ", 24: "চব্বিশ", 25: "পঁচিশ",
            26: "ছাব্বিশ", 27: "সাতাশ", 28: "আটাশ", 29: "ঊনত্রিশ", 30: "ত্রিশ",
            31: "একত্রিশ", 32: "বত্রিশ", 33: "তেত্রিশ", 34: "চৌত্রিশ", 35: "পঁয়ত্রিশ",
            36: "ছত্রিশ", 37: "সাঁইত্রিশ", 38: "আটত্রিশ", 39: "ঊনচল্লিশ", 40: "চল্লিশ",
            41: "একচল্লিশ", 42: "বিয়াল্লিশ", 43: "তেতাল্লিশ", 44: "চুয়াল্লিশ", 45: "পঁয়তাল্লিশ",
            46: "ছেচল্লিশ", 47: "সাতচল্লিশ", 48: "আটচল্লিশ", 49: "ঊনপঞ্চাশ", 50: "পঞ্চাশ",
            51: "একান্ন", 52: "বায়ান্ন", 53: "তিপ্পান্ন", 54: "চুয়ান্ন", 55: "পঞ্চান্ন",
            56: "ছাপ্পান্ন", 57: "সাতান্ন", 58: "আটান্ন", 59: "ঊনষাট", 60: "ষাট",
            61: "একষট্টি", 62: "বাষট্টি", 63: "তেষট্টি", 64: "চৌষট্টি", 65: "পঁয়ষট্টি",
            66: "ছেষট্টি", 67: "সাতষট্টি", 68: "আটষট্টি", 69: "ঊনসত্তর", 70: "সত্তর",
            71: "একাত্তর", 72: "বাহাত্তর", 73: "তিয়াত্তর", 74: "চুয়াত্তর", 75: "পঁচাত্তর",
            76: "ছিয়াত্তর", 77: "সাতাত্তর", 78: "আটাত্তর", 79: "ঊনআশি", 80: "আশি",
            81: "একাশি", 82: "বিরাশি", 83: "তিরাশি", 84: "চুরাশি", 85: "পঁচাশি",
            86: "ছিয়াশি", 87: "সাতাশি", 88: "আটাশি", 89: "ঊননব্বই", 90: "নব্বই",
            91: "একানব্বই", 92: "বিরানব্বই", 93: "তিরানব্বই", 94: "চুরানব্বই", 95: "পঁচানব্বই",
            96: "ছিয়ানব্বই", 97: "সাতানব্বই", 98: "আটানব্বই", 99: "নিরানব্বই"
        }
        
        self.en_numbers = {
            0: "Zero", 1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five",
            6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten",
            11: "Eleven", 12: "Twelve", 13: "Thirteen", 14: "Fourteen", 15: "Fifteen",
            16: "Sixteen", 17: "Seventeen", 18: "Eighteen", 19: "Nineteen", 20: "Twenty",
            30: "Thirty", 40: "Forty", 50: "Fifty", 60: "Sixty",
            70: "Seventy", 80: "Eighty", 90: "Ninety"
        }

    def _convert_bn_below_hundred(self, number):
        if number < 100:
            return self.bn_numbers.get(number, "")

    def _convert_en_below_hundred(self, number):
        if number <= 20:
            return self.en_numbers.get(number, "")
        elif number < 100:
            tens = (number // 10) * 10
            ones = number % 10
            return (self.en_numbers[tens] + ("-" + self.en_numbers[ones] if ones > 0 else ""))

    def _convert_paisa(self, decimal_part):
        if self.lang == "bn":
            if decimal_part < 10:
                decimal_part *= 10
            return self._convert_bn_below_hundred(decimal_part)
        else:
            if decimal_part < 10:
                decimal_part *= 10
            return self._convert_en_below_hundred(decimal_part)

    def _to_bangla_numeral(self, number):
        """Convert a number to Bangla numerical digits"""
        if isinstance(number, (int, float)):
            number = str(number)
        return ''.join(self.bn_digits.get(c, c) for c in str(number))

    def convert_number(self, number, return_numerical=False):
        # If numerical representation is requested
        if return_numerical:
            if self.numerical_digits == "bn":
                return self._to_bangla_numeral(number)
            return str(number)

        # Split the number into integer and decimal parts
        integer_part = int(number)
        decimal_part = int(round((number - integer_part) * 100))

        if integer_part == 0 and decimal_part == 0:
            base = self.bn_numbers[0] if self.lang == "bn" else self.en_numbers[0]
            return f"{base} {self.currency} {self.extension}"

        if self.lang == "bn":
            parts = []
            remaining = integer_part
            if remaining >= 10000000:
                crore = remaining // 10000000
                parts.append(f"{self._convert_bn_below_hundred(crore)} কোটি")
                remaining %= 10000000
            if remaining >= 100000:
                lakh = remaining // 100000
                parts.append(f"{self._convert_bn_below_hundred(lakh)} লক্ষ")
                remaining %= 100000
            if remaining >= 1000:
                thousand = remaining // 1000
                parts.append(f"{self._convert_bn_below_hundred(thousand)} হাজার")
                remaining %= 1000
            if remaining >= 100:
                hundred = remaining // 100
                parts.append(f"{self._convert_bn_below_hundred(hundred)} শত")
                remaining %= 100
            if remaining > 0:
                parts.append(self._convert_bn_below_hundred(remaining))
            
            result = " ".join(filter(None, parts))
            
            if decimal_part > 0:
                if self.decimal_style == "decimal":
                    # Convert decimal part directly as a number
                    decimal_str = str(decimal_part)
                    decimal_digits = []
                    for digit in decimal_str:
                        if digit.isdigit():
                            decimal_digits.append(self.bn_numbers[int(digit)])
                    decimal_text = " ".join(decimal_digits)
                    return f"{result} দশমিক {decimal_text} {self.currency} {self.extension}"
                else:
                    # Traditional paisa style
                    paisa = self._convert_paisa(decimal_part)
                    return f"{result} {self.currency} এবং {paisa} পয়সা {self.extension}"
            return f"{result} {self.currency} {self.extension}"
        else:
            parts = []
            remaining = integer_part
            if remaining >= 10000000:
                crore = remaining // 10000000
                parts.append(f"{self._convert_en_below_hundred(crore)} Crore")
                remaining %= 10000000
            if remaining >= 100000:
                lakh = remaining // 100000
                parts.append(f"{self._convert_en_below_hundred(lakh)} Lakh")
                remaining %= 100000
            if remaining >= 1000:
                thousand = remaining // 1000
                parts.append(f"{self._convert_en_below_hundred(thousand)} Thousand")
                remaining %= 1000
            if remaining >= 100:
                hundred = remaining // 100
                parts.append(f"{self._convert_en_below_hundred(hundred)} Hundred")
                remaining %= 100
            if remaining > 0:
                parts.append(self._convert_en_below_hundred(remaining))
            
            result = " ".join(filter(None, parts))
            
            if decimal_part > 0:
                paisa = self._convert_paisa(decimal_part)
                return f"{result} {self.currency} And {paisa} Paisa {self.extension}"
            return f"{result} {self.currency} {self.extension}"

def taka(*numbers):
    converter = TakaConverter()
    if len(numbers) == 1:
        return converter.convert_number(numbers[0])
    return [converter.convert_number(num) for num in numbers]
