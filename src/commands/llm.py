import json
import requests
import threading
import itertools
import sys
import time
from core.core_types.command import BaseCommand
from core.config_loader import Config
from core.logger import get_logger


API_ROOT = "https://ai.minoa.cat"
MODEL = "groq/llama-3.3-70b-versatile"


class LLM(BaseCommand):
    """
    llm info
    llm <your prompt here>

    Examples:
        llm info
        llm Explain quantum computing in a haiku
    """

    name = "llm"
    description = "Hack Club AI quick queries"
    fun = True

    def execute(self, *args, **kwargs) -> int:
        """
        Executes the 'llm' command with the provided arguments.
        If no arguments are given, prints usage instructions and logs a warning.
        If the first argument is 'info', logs the request and displays information about the 'llm' command.
        Otherwise, treats the arguments as a prompt and processes it accordingly.
        Args:
            *args: Positional arguments passed to the command.
            **kwargs: Keyword arguments passed to the command.
        Returns:
            int: Status code indicating the result of the command execution.
        """
        if not args:
            print("Usage:\n  llm info\n  llm <your prompt>")
            get_logger("llm").warning("No arguments provided to llm command.")
            return 0

        if args[0].lower() == "info":
            get_logger("llm").info("User requested llm info.")
            return self._do_info()

        prompt = " ".join(args)
        return self._do_query(prompt)

    def _do_info(self) -> int:
        """
        Prints the current value of the MODEL variable to the console.

        Returns:
            int: Always returns 0 to indicate successful execution.
        """
        print(MODEL)
        return 0

    def _do_query(self, prompt: str) -> int:
        """
        Sends a prompt to the LLM API and displays the response in the terminal with a spinner animation.
        Args:
            prompt (str): The user input or query to send to the language model.
        Returns:
            int: Returns 0 on success, or 1 if an error occurred during the request or response parsing.
        Side Effects:
            - Prints a spinner animation to the terminal while waiting for the API response.
            - Logs the prompt and response using the "llm" logger.
            - Prints the LLM's response or error messages to stdout.
        """
        payload = {
            "model": MODEL,
            "temperature": Config.get_config().get("ai", {}).get("temperature", 0.7),
            "messages": [
                {
                    "role": "system",
                    "content": "You are a command-line assistant who lives in a terminal. You do not have message persistence and should respond in such way, do not ask any questions and you will not remember them. You should be humourous and not take yourself too seriously.",
                },
                {"role": "user", "content": prompt},
            ],
        }
        get_logger("llm").info(f"LLM query: {prompt}")

        spinner_done = threading.Event()

        def spinner():
            """
            Displays an animated spinner in the console to indicate ongoing processing.

            The spinner cycles through a set of Unicode characters to create a spinning effect.
            It runs until the `spinner_done` event is set, at which point it clears the spinner line
            and moves the cursor to a new line.

            Assumes `spinner_done` is a threading.Event() and that `itertools`, `sys`, and `time` are imported.
            """
            for ch in itertools.cycle("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"):
                if spinner_done.is_set():
                    break
                sys.stdout.write(f"\r{ch} thinking… ")
                sys.stdout.flush()
                time.sleep(0.1)
            # Clear spinner line, but ALSO move to a fresh line
            sys.stdout.write("\r\033[K\n")
            sys.stdout.flush()

        spinner_thread = threading.Thread(target=spinner, daemon=True)
        spinner_thread.start()

        try:
            resp = requests.post(
                f"{API_ROOT}/v1/chat/completions",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer Cmdly",
                },
                timeout=60,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            spinner_done.set()
            spinner_thread.join()
            get_logger("llm").error(f"Request failed: {e}")
            print(f"Error during request: {e}")
            print(resp.text)
            return 1

        spinner_done.set()
        spinner_thread.join()  # make sure spinner has finished cleaning up

        try:
            content = resp.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError, ValueError):
            print("⚠️ Unexpected response format:")
            get_logger("llm").error("Unexpected response format from LLM API.")
            print(json.dumps(resp.json(), indent=2))
            return 1

        # Always start the answer on its own line
        print(content.strip() + "\n")
        get_logger("llm").info(f"LLM response: {content.strip()}")
        return 0
