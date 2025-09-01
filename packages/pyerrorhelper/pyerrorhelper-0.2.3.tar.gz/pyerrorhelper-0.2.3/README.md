# pyerrorhelper

> 🧠 AI-enabled Python library for **runtime error explainability**.

---

## 📖 Description

`pyerrorhelper` is a Python library that brings **AI-powered error explainability** into your runtime environment.

### Why?
Developers typically use AI **before** running code (for generation) or **after** running code (for debugging).
This package enables AI **during execution**, so your running Python programs can leverage AI-driven insights in real time.

### Key Objectives
- **Runtime AI integration** – Make AI available inside the running program (starting with error explainability).
- **Retrofit older systems** – Allow existing Python systems to adopt AI workflows with minimal changes [this is the future i wanna build].
- **Free & local AI models** – Works with free AI solutions - using [Ollama](https://www.ollama.com).

---

## Architecture Diagram

![Architecture Digram](pyerrorhelper.jpg)

## 🛠️ Working

There are two main components (class) in the system - 

- ErrorMananger (manager.py) -
    install - this method handles overriding sys.excepthook with custom method.
    process_exception - this method calls the second component (OllamaEmbedder) and helps in summarizing the error
    uninstall - this method makes the sys.excepthook as default error handling way

- OllamEmbedder (ollamaembedder.py) - 
    ensure_ollama_installed - this method ensures that Ollama is installed, if not - it tries installing it via curl command
    summarize - this method uses the Ollama supported GPT model to summarize the errors

## 🔀 Flow of control - 

- When we use install() of ErrorManager -> sys.excepthook is overridden
- and at the same time -> OllamaEmbedder is initialised and it checks for Ollama installation on local system
- if its not present -> it tries to install the Ollama backend
- After the installation of Ollama -> the system is activated, ready to catch any error and summarize it


## ⚙️ Installation

1. **Install Python**
   Download and install from [python.org](https://www.python.org/downloads/).

2. **Install pyerrorhelper**
   ```bash
   pip install pyerrorhelper
   ```

3. **Usage**
```
from pyerrorhelper import ErrorManager

class Test:
    def __init__(self):
        self.error_manager = ErrorManager()
        self.error_manager.install()
    
    def some_function(self):
        cause_some_error()
```
## 👨‍💻 About Me

Name: Shikhar Aditya

Email: satyamshikhar@gmail.com

Github Repo Link: [pyerrorhandler](https://github.com/Satyamaadi/pyerrorhelper)

GitHub Personal Profile: [Satyamaadi](https://github.com/Satyamaadi)

## 🤝 Contributing

Contributions are welcome! Feel free to fork, open issues, or submit pull requests.
