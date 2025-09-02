# Chillax 💤

**Chillax** is not just another wrapper — it’s a whole new way of coding with AI.  
Instead of memorizing a fixed set of functions, **you decide what functions you want**.  
Every function you call on `Chillax` gets passed straight to AI — so you can literally invent your own function names on the fly and they’ll just work. (vibecoding supremacy)

---

## 🚀 Features

- **One-line setup** → just set your API key and you’re ready to go  
- **Make up your own functions** → `chillax.sort()`, `chillax.translate()`, `chillax.summarize()`, `chillax.reverse()`, `chillax.doMagicTrick()` … literally any name you choose will work  
- **Lightweight & beginner-friendly** → no heavy dependencies, perfect for vibecoders who want to focus on coding instead of setup  

---

## 📦 Installation

```bash
pip install chillax
```

---

## ⚡Quick Start - Procedure

```python
from chillax import chillax

# Set your Gemini API key
chillax.setAPIKey("your_api_key_here")

# Example of a useful function (extendable)
my_list = [5, 2, 9, 1]
sorted_list = chillax.sort(my_list)
print(sorted_list)

# No predefined "explainSorting" exists...
# But you can just call it anyway 👇
print(Chillax.explainSorting("quick sort"))

# Or invent your own creative function names
print(Chillax.debugMyCode("def add(a,b): return a-b", "Python"))
print(Chillax.writePoem("about vibecoding"))
print(Chillax.createPlaylist("lofi coding beats"))
```

---

## ⭐Naming Convention

To keep things clean and intuitive, **Chillax** uses `camelCase` for function names.  
This makes it easy to read and understand at a glance.  

```python
# Example                           
Chillax.translateFrenchToEnglish("Je suis Inde")                  
```

---

## 🤝 Contributing

Wanna make Chillax even chiller? 😎  
Contributions are open! Fork it, hack it, and PR it.  

Cool things you could add:

- More shortcuts for lazy coders
- Anything that makes coding more… chill.

---
