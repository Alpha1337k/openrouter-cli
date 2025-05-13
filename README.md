# openrouter-cli

An Ollama-like CLI tool for OpenRouter that provides simple command-line access to various AI models.

<p align="center">
  <picture align="center">
    <source srcset="./assets/sample.png">
    <img alt="Shows a sample command for openrouter-cli.">
  </picture>
</p>

## Features

- Interactive chat interface with AI models
- Responses are styled for maximum readability
- List available OpenRouter models with context sizes and pricing
- Support for stdin input, useful for scripting
- Allows for system prompts, temperature, and more.
- Persistent local history over sessions

## Installation

Install via pip:

```bash
pip install openrouter-cli
```

## Configuration

Before using the CLI, you'll need to configure your OpenRouter API key:

```bash
openrouter-cli configure
```

Your API key will be stored at `~/.openrouter-cli/.config`.

## Usage

### List Available Models

```bash
openrouter-cli models [--raw]
```

Lists all available models in a human-readable format.

Example output:

```
...

- mistralai/mistral-medium-3                            @ 128.0K context   (07-05-2025) [ In: $0.400/1M   Out: $2.000/1M  ]
- google/gemini-2.5-pro-preview                         @ 1.0M context     (07-05-2025) [ In: $1.250/1M   Out: $10.000/1M ]
- arcee-ai/caller-large                                 @ 32.0K context    (06-05-2025) [ In: $0.550/1M   Out: $0.850/1M  ]

...
```

### Chat with a Model

```bash
openrouter-cli run [model] [--temperature TEMPERATURE] [--seed SEED] [--effort {high,medium,low}] [--system SYSTEM] [--no-thinking-stdout] [--pretty] [--raw]
```

Starts an interactive chat session with the specified model. Responses are properly styled and formatted for optimal readability in the terminal.

Example interaction:

```
>>> Write me an python hello world, and explain the code.
Python Hello World Code                                                                                                                                                                                               

print("Hello, World!")                                                                                                                                                                                               

Explanation                                                                                                                                                                                                           

This simple two-line code performs the following:                                                                                                                                                                     

1 print() function: This is a built-in Python function used to display output (text or data) to the console or standard output.                                                                                      
2 "Hello, World!": This is a string literal. Strings in Python are sequences of characters enclosed in single quotes (') or double quotes ("). In this case, the string "Hello, World!" is the data that will be     
displayed.                                                                                                                                                                                                         

When you run this Python code, the print() function takes the string "Hello, World!" as an argument and outputs it to the console, resulting in the display:                                                          

Hello, World!                                                                                                                                                                                                        

This is the basic way to write and run a "Hello, World!" program in Python. It demonstrates the fundamental concept of using the print() function to display output, which is essential for debugging, user           
interaction, and displaying results in Python programs.                                                                                                                                                               
>>>
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

