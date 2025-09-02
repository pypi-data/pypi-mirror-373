# Chillax 💤

**Chillax** is a lightweight Python wrapper for Gemini’s API that lets you call AI directly inside your code.  Whenever you hit a wall and can’t implement logic on the spot, just ask AI and get the answer instantly(vibe coding supremcay).


---

## 🚀 Features

- Simple API configuration
- Extendable for your own chill functions
	- sort, translate, summation, summarize, reverse etc. (You name it)
- Minimal, lightweight, and beginner-friendly

---

## 📦 Installation

```bash
pip install chillax
```

## ⚡Quick Start - Procedure

```python
from chillax import chillax

# Set your Gemini API key
chillax.setAPIKey("your_api_key_here")

# Example of a useful function (extendable)
my_list = [5, 2, 9, 1]
sorted_list = chillax.sort(my_list)
print(sorted_list)

# Example of translation function
sentence = "hello, my name is gowtham"
translated = translateEnglishToSpanish(sentence)
print(translated)
```

## 🤝 Contributing

Contributions are welcome! Feel free to fork, open issues, or submit PRs.

---

## ⭐Naming Convention

To keep things clean and intuitive, **Chillax** uses `camelCase` for function names.  
This makes it easy to read and understand at a glance.  

```python
# Example
Chillax.writeAPoem("English")                            
Chillax.translateFrenchToEnglish("Je suis Inde")                  
```

---
