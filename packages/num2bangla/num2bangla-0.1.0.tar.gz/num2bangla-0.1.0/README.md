# num2bangla

A Python package to convert numbers to Bengali/Bangla text and numerals, with support for currency formatting.

## Installation

```bash
pip install num2bangla
```

## Usage

```python
from num2bangla import taka, TakaConverter

# Basic usage with default settings (English)
result = taka(200)  # "Two Hundred BDT Only"

# Using Bangla (Traditional paisa style)
converter = TakaConverter(lang="bn", currency="টাকা", extension="মাত্র")
result = converter.convert_number(200.25)  # "দুই শত টাকা এবং পঁচিশ পয়সা মাত্র"

# Using Bangla (Decimal style)
converter = TakaConverter(lang="bn", currency="টাকা", extension="মাত্র", decimal_style="decimal")
result = converter.convert_number(42.25)  # "বিয়াল্লিশ দশমিক দুই পাঁচ টাকা মাত্র"

# Using Bangla numerical digits
converter = TakaConverter(numerical_digits="bn")
result = converter.convert_number(1234.56, return_numerical=True)  # "১২৩৪.৫৬"

# Combining Bangla text and numerals
converter = TakaConverter(
    lang="bn", 
    currency="টাকা", 
    extension="মাত্র", 
    decimal_style="decimal",
    numerical_digits="bn"
)
text_result = converter.convert_number(42.25)  # Text format: "বিয়াল্লিশ দশমিক দুই পাঁচ টাকা মাত্র"
numeral_result = converter.convert_number(42.25, return_numerical=True)  # Numeral format: "৪২.২৫"

# Multiple numbers at once
results = taka(200, 100, 300)  # Returns a list of converted numbers

# Customizing currency and extension
converter = TakaConverter(lang="en", currency="USD", extension="Only")
result = converter.convert_number(200)  # "Two Hundred USD Only"
```

## Command Line Usage

The package includes a command-line interface. After installation, you can use it directly from the terminal:

```bash
# Basic usage - converts to Bangla text
num2bangla 42.25

# Multiple numbers
num2bangla 100 200.50 1234.56

# English output
num2bangla 42.25 --lang en

# Custom currency and extension
num2bangla 42.25 --currency BDT --extension Only

# Decimal style (দশমিক)
num2bangla 42.25 --decimal-style decimal

# Bangla numerals only
num2bangla 1234.56 --numerical-digits bn --numerical-only

# Full example with all options
num2bangla 42.25 --lang bn --currency টাকা --extension মাত্র --decimal-style decimal --numerical-digits bn
```

Available options:
- `--lang`: Output language (`bn` or `en`)
- `--currency`: Currency text (e.g., টাকা, Taka, BDT)
- `--extension`: Extension text (e.g., মাত্র, Only)
- `--decimal-style`: Decimal style (`default` or `decimal`)
- `--numerical-digits`: Numerical digit style (`bn` or `en`)
- `--numerical-only`: Output only numerical representation

## Features

- Convert numbers to words in Bangla or English
- Customize currency text (e.g., "Taka", "BDT", "টাকা")
- Customize extension text (e.g., "Only", "মাত্র")
- Support for multiple numbers at once
- Support for large numbers (up to crores)
- Command-line interface (CLI)
- Bengali numerical digits support

## License

This project is licensed under the MIT License - see the LICENSE file for details.
