# Vibesorter

Sort arrays using LLMs with structured output

[![PyPI version](https://badge.fury.io/py/vibesorter.svg)](https://badge.fury.io/py/vibesorter)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- **One Simple Interface**: Just `vibesort()` for everything
- **Auto-Detection**: Automatically handles integers vs strings
- **LLM-Powered Sorting**: Use state-of-the-art language models  
- **Structured Output**: Reliable, type-safe results using Pydantic models
- **Multiple Providers**: Support for OpenAI, Anthropic, and Google models
- **Custom Criteria**: Sort strings by length, alphabetically, or any criteria you want
- **Production Ready**: Comprehensive error handling and validation
- **Easy Setup**: Simple configuration with environment variables

## 🚀 Installation

```bash
pip install vibesorter
```

## 🔧 Setup

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Add your API key and preferred model to `.env`:
```env
VIBESORTER_MODEL_NAME=gpt-4o-mini
OPENAI_API_KEY=your_openai_api_key_here
```

Supported environment variables:
- `VIBESORTER_MODEL_NAME`: Model to use (default: `gpt-4o-mini`)
- `OPENAI_API_KEY`: For GPT models  
- `ANTHROPIC_API_KEY`: For Claude models
- `GOOGLE_API_KEY`: For Gemini models

## 📖 Usage

### Sort Integers

```python
from vibesorter import vibesort

# Sort integers in ascending order
numbers = [64, 34, 25, 12, 22, 11, 90]
sorted_numbers = vibesort(numbers)
print(sorted_numbers)  # [11, 12, 22, 25, 34, 64, 90]

# Sort in descending order
sorted_desc = vibesort(numbers, order="desc") 
print(sorted_desc)  # [90, 64, 34, 25, 22, 12, 11]
```

### Sort Strings

```python
from vibesorter import vibesort

# Sort strings alphabetically  
words = ["python", "ai", "langchain", "sort"]
sorted_words = vibesort(words)
print(sorted_words)  # ['ai', 'langchain', 'python', 'sort']

# Sort strings by length
sorted_by_length = vibesort(
    words, 
    order="asc",
    sort_criteria="by length"
)
print(sorted_by_length)  # ["ai", "sort", "python", "langchain"]

# Sort numbers as strings numerically
numbers_as_strings = ["64", "34", "25", "12", "22", "11", "90"]
sorted_numerically = vibesort(
    numbers_as_strings,
    order="asc", 
    sort_criteria="numerically"
)
print(sorted_numerically)  # ["11", "12", "22", "25", "34", "64", "90"]
```

### Error Handling

```python
from vibesorter import vibesort, APIKeyError, ModelError, VibesortError

try:
    result = vibesort([3, 1, 4, 1, 5])
    print(result)
except APIKeyError as e:
    print(f"API key error: {e}")
except ModelError as e:
    print(f"Model error: {e}") 
except VibesortError as e:
    print(f"Sorting error: {e}")
```

## 🔧 Configuration

### Supported Models

**OpenAI Models:**
- `gpt-4o-mini` (default, cleanest output)
- `gpt-4o`
- `gpt-4-turbo`
- `gpt-3.5-turbo`

**Anthropic Models:**
- `claude-3-sonnet-20240229`
- `claude-3-haiku-20240307`
- `claude-3-opus-20240229`

**Google Models:**
- `gemini-pro`
- `gemini-1.5-pro`

> **Note**: Google/Gemini models may show harmless schema warnings about `additionalProperties`. These don't affect functionality but for cleanest output, consider using OpenAI or Anthropic models.

### Environment Variables

The library automatically detects the provider based on your model name and available API keys:

```env
# For OpenAI models
VIBESORTER_MODEL_NAME=gpt-4o-mini
OPENAI_API_KEY=sk-...

# For Anthropic models  
VIBESORTER_MODEL_NAME=claude-3-sonnet-20240229
ANTHROPIC_API_KEY=sk-ant-...

# For Google models
VIBESORTER_MODEL_NAME=gemini-pro
GOOGLE_API_KEY=AI...
```

## 🧪 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/Yazan-Hamdan/vibesorter.git
cd vibesorter

# Install development dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks (optional)
pre-commit install
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black vibesorter/
isort vibesorter/
flake8 vibesorter/
```

### Type Checking

```bash
mypy vibesorter/
```

## 📋 API Reference

### `vibesort(array, order="asc", sort_criteria="")`

Sort an array of integers or strings using an LLM. Automatically detects the data type and uses the appropriate processing.

**Parameters:**
- `array` (List[int] | List[str]): List of integers or strings to sort
- `order` (Literal["asc", "desc"]): Sort order (default: "asc")
- `sort_criteria` (str): Optional criteria for string sorting (default: "", ignored for integers)

**Returns:**
- `List[int] | List[str]`: The sorted array (same type as input)

**Raises:**
- `VibesortError`: If sorting fails or array contains mixed types
- `APIKeyError`: If API key is not configured
- `ModelError`: If model initialization fails

**Examples:**
```python
# Sort integers
vibesort([3, 1, 4])  # → [1, 3, 4]

# Sort strings
vibesort(["c", "a", "b"])  # → ["a", "b", "c"]  

# Sort strings with criteria
vibesort(["python", "ai"], sort_criteria="by length")  # → ["ai", "python"]
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

If you have any questions or run into issues, please:

1. Check the [Issues](https://github.com/Yazan-Hamdan/vibesorter/issues) page
2. Create a new issue if your problem isn't already reported
3. Provide as much detail as possible, including:
   - Python version
   - Vibesorter version  
   - Error messages
   - Sample code that reproduces the issue
