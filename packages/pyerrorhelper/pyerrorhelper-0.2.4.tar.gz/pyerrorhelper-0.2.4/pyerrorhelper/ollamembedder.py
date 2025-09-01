import subprocess
import platform
import time
import requests  # type: ignore


class OllamaEmbedder:
    def __init__(self) -> None:
        self.ensure_ollama_installed()

    def ensure_ollama_installed(self) -> bool:
        try:
            subprocess.run(["ollama", "--version"], check=True, capture_output=True)  # noqa E501
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("Ollama is not installed. Installing now...")

            os_type = platform.system().lower()

            if os_type in ("darwin", "linux"):
                try:
                    subprocess.run(
                        [
                            "sh",
                            "-c",
                            "curl -fsSL https://ollama.com/install.sh | sh",
                        ],  # noqa E501
                        check=True,
                    )
                    print("✅ Ollama installed successfully.")
                    return True
                except subprocess.CalledProcessError:
                    print("❌ Failed to install Ollama automatically.")
                    print(
                        "Run this manually:\n  curl -fsSL https://ollama.com/install.sh | sh"  # noqa E501
                    )
                    return False

            elif os_type == "windows":
                print("⚠️ Automatic install on Windows is not supported.")
                print("Please download and install Ollama manually:")
                print("👉 https://ollama.com/download/windows")
                return False

            else:
                print(f"❌ Unsupported OS: {os_type}. Please install Ollama manually.")  # noqa E501
                print("👉 https://ollama.com/download")  # noqa E501
                return False  # noqa E501

    def summarize(self, code: str, model: str = "codellama") -> str:
        if not self.ensure_ollama_installed():
            raise RuntimeError(
                "Ollama is not installed. Please follow instructions above."
            )

        ollama_proc = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        print("Ollama server started (PID:", ollama_proc.pid, ")")

        # Give the server a moment to start
        time.sleep(2)

        # Ensure model is available
        subprocess.run(["ollama", "pull", model], check=False)

        url = "http://localhost:11434/api/generate"
        prompt = f"""Summarize the following error \n\n```python\n{code}\n```
        - so that we get to understand the root cause and also list possible solutions also:"""  # noqa E501

        resp = requests.post(
            url,
            json={"model": model, "prompt": prompt, "stream": False},
        )
        resp.raise_for_status()
        return str(resp.json()["response"].strip())
