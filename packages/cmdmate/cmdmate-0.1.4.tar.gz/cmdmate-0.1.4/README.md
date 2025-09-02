# cmdmate 

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI GPT-4](https://img.shields.io/badge/AI-GPT--4-green.svg)](https://openai.com/)
[![Cross Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

cmdmate is an AI-powered command-line assistant that converts natural language queries into terminal commands. Simply describe what you want to do, and cmdmate will generate the appropriate command for your operating system.

## ✨ Features

- 🧠 **AI-Powered**: Uses OpenAI's GPT-4 to understand natural language queries
- 🖥️ **Cross-Platform**: Works on Windows, macOS, and Linux
- 🔒 **Safe Execution**: Always asks for confirmation before running commands
- 🎯 **OS-Aware**: Generates commands specific to your operating system
- ⚡ **Simple CLI**: Easy-to-use command-line interface

## 🚀 Installation

**Clone the repository:**
   ```bash
   pip install cmdmate
   ```

## 📖 Usage

### Quick Start

Run cmdmate directly from the project directory:

```bash
cmdmate "<your natural language command>"
```

**Example:**
```bash
cmdmate "list all files in current directory"
cmdmate -o win "list all files in current directory"
```

### Example Commands

#### File Operations
```bash
cmdmate "find all Python files in this directory"
cmdmate "create a new directory called my-project"
cmdmate "copy all .txt files to a backup folder"
cmdmate "delete all .log files older than 7 days"
```

#### System Information
```bash
cmdmate "show disk usage for this directory"
cmdmate "display all running processes"
cmdmate "check available memory"
cmdmate "show network connections"
```

#### Git Operations
```bash
cmdmate "stage all changes and commit with message 'fix bugs'"
cmdmate "create and switch to a new branch called feature-login"
cmdmate "show git log for the last 5 commits"
cmdmate "push current branch to origin"
```

### Example Session

```
$ cmdmate "show me all hidden files in this directory"

🤖 [cmdmate] Generated Command:
ls -la
```

### Tips for Better Results

- **Be specific**: "list Python files" vs "show files"
- **Include context**: "in current directory" or "recursively"
- **Mention your intent**: "for backup", "to delete", "to analyze"
- **Use natural language**: cmdmate understands conversational commands
```

### Supported Operating Systems

- **macOS**: Uses `/bin/zsh` as the default shell
- **Linux**: Uses `/bin/zsh` as the default shell  
- **Windows**: Uses `cmd.exe` as the default shell

## 🛡️ Safety Features

- **Confirmation Prompt**: Always asks before executing commands
- **Error Handling**: Gracefully handles execution errors
- **No Auto-Execution**: Commands are never run without user consent

## 📋 Requirements

- Python 3.8 or higher
- Internet connection for AI queries

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

cmdmate generates commands using AI, which may not always be perfect. Always review commands before execution, especially for:
- File deletion operations
- System configuration changes
- Network operations
- Administrative commands

## 🙋‍♂️ Support

If you encounter any issues or have questions:
1. Check the existing issues on GitHub
2. Create a new issue with detailed information
3. Include your OS, Python version, and error messages

---

Made with ❤️ by Chinmay Rao