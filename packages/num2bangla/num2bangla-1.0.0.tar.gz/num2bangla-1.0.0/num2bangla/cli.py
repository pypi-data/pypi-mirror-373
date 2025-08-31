#!/usr/bin/env python
import argparse
from .converter import TakaConverter

def main():
    parser = argparse.ArgumentParser(description='Convert numbers to Bengali/Bangla text and numerals')
    parser.add_argument('numbers', type=float, nargs='+', help='Numbers to convert')
    parser.add_argument('--lang', choices=['bn', 'en'], default='bn', help='Output language (bn/en)')
    parser.add_argument('--currency', default='টাকা', help='Currency text (e.g., টাকা, Taka, BDT)')
    parser.add_argument('--extension', default='মাত্র', help='Extension text (e.g., মাত্র, Only)')
    parser.add_argument('--decimal-style', choices=['default', 'decimal'], default='default',
                      help='Decimal style (default: paisa style, decimal: দশমিক style)')
    parser.add_argument('--numerical-digits', choices=['bn', 'en'], default='en',
                      help='Output numerical digits in Bengali or English')
    parser.add_argument('--numerical-only', action='store_true',
                      help='Output only numerical representation')

    args = parser.parse_args()

    converter = TakaConverter(
        lang=args.lang,
        currency=args.currency,
        extension=args.extension,
        decimal_style=args.decimal_style,
        numerical_digits=args.numerical_digits
    )

    for number in args.numbers:
        if args.numerical_only:
            result = converter.convert_number(number, return_numerical=True)
        else:
            result = converter.convert_number(number)
        print(result)

if __name__ == '__main__':
    main()
