# num2bangla

[![PyPI version](https://badge.fury.io/py/num2bangla.svg)](https://badge.fury.io/py/num2bangla)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful Python package for converting numbers to Bengali/Bangla text and numerals, with comprehensive support for currency formatting. Perfect for financial documents, invoices, and applications requiring Bengali number representation.

## 🚀 Features

- 📝 Convert numbers to words in Bangla or English
- 💱 Flexible currency formatting (e.g., "Taka", "টাকা")
- 🔢 Support for Bengali numerical digits
- 💯 Handle decimal numbers in traditional (পয়সা) or modern (দশমিক) style
- 📊 Process multiple numbers simultaneously
- 🔄 Support for large numbers (up to crores)
- 💻 Command-line interface (CLI)
- ⚙️ Highly customizable output format

## 📦 Installation

```bash
pip install num2bangla
```

## 🎯 Quick Start

### Basic Usage

```python
from num2bangla import taka

# Simple conversion
result = taka(200)  # "Two Hundred Taka Only"

### Advanced Usage

```python
from num2bangla import TakaConverter

# Bangla output with traditional paisa style
converter = TakaConverter(lang="bn", currency="টাকা", extension="মাত্র")
result = converter.convert_number(200.25)  
# Output: "দুই শত টাকা এবং পঁচিশ পয়সা মাত্র"

# Modern decimal style in Bangla
converter = TakaConverter(
    lang="bn",
    currency="টাকা",
    extension="মাত্র",
    decimal_style="decimal"
)
result = converter.convert_number(42.25)  
# Output: "বিয়াল্লিশ দশমিক দুই পাঁচ টাকা মাত্র"

# Using Bengali numerals
converter = TakaConverter(numerical_digits="bn")
result = converter.convert_number(1234.56, return_numerical=True)  
# Output: "১২৩৪.৫৬"

# Multiple numbers at once
converter = TakaConverter(lang="en", currency="USD", extension="Only")
results = converter.convert_multiple(200, 100, 300)  
# Output: ["Two Hundred USD Only", "One Hundred USD Only", "Three Hundred USD Only"]
```

### Comprehensive Configuration

```python
converter = TakaConverter(
    lang="bn",                # Language: "bn" for Bangla, "en" for English
    currency="টাকা",          # Currency text
    extension="মাত্র",        # Extension text
    decimal_style="decimal",  # Decimal style: "default" or "decimal"
    numerical_digits="bn"     # Numerical digits: "bn" or "en"
)

text_result = converter.convert_number(42.25)  
# Text format: "বিয়াল্লিশ দশমিক দুই পাঁচ টাকা মাত্র"

numeral_result = converter.convert_number(42.25, return_numerical=True)  
# Numeral format: "৪২.২৫"
```

## 🖥️ Command Line Interface

The package includes a convenient command-line interface:

```bash
# Basic conversion
num2bangla 42.25

# Multiple numbers
num2bangla 100 200.50 1234.56

# Full configuration example
num2bangla 42.25 \
    --lang bn \
    --currency টাকা \
    --extension মাত্র \
    --decimal-style decimal \
    --numerical-digits bn
```

### CLI Options

| Option | Description | Values |
|--------|-------------|--------|
| `--lang` | Output language | `bn`, `en` |
| `--currency` | Currency text | e.g., টাকা, Taka |
| `--extension` | Extension text | e.g., মাত্র, Only |
| `--decimal-style` | Decimal format | `default`, `decimal` |
| `--numerical-digits` | Numeral style | `bn`, `en` |
| `--numerical-only` | Show only numerals | flag |

## 📝 Configuration Options

### TakaConverter Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `lang` | `"en"` | Output language (`"bn"` or `"en"`) |
| `currency` | `"Taka"` | Currency text to use in output |
| `extension` | `"Only"` | Extension text to append |
| `decimal_style` | `"default"` | Decimal number style |
| `numerical_digits` | `"en"` | Numeral style for numerical output |

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## 💬 Support

If you have any questions or need help, please open an issue on GitHub.
