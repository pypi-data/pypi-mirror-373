# FamilyCLI 👨‍👩‍👧‍👦

> A warm, child-safe AI family chat experience in your terminal

## 🚧 Beta Release Notice

**Welcome to Family AI CLI v1.0.0!** 🎉

This is our **initial beta release** and we're thrilled to have you as part of our testing community! Your feedback and contributions are invaluable in making this the best family-friendly AI experience possible.

**🐛 Found a bug or have suggestions?** We'd love to hear from you!
- **Report Issues**: [GitHub Issues](https://github.com/AIMLDev726/ai-family-cli/issues)
- **Request Features**: [Feature Requests](https://github.com/AIMLDev726/ai-family-cli/issues/new?template=feature_request.md)
- **General Discussion**: [GitHub Discussions](https://github.com/AIMLDev726/ai-family-cli/discussions)

Thank you for helping us improve Family AI CLI! 🙏

---

## About Family AI CLI

FamilyCLI brings AI-powered family members to life in your command line. Chat with loving personas like Grandma Rose, Uncle Joe, Dad Mike, and more - each with unique personalities, memories, and caring responses designed for children and families.

## ✨ Features

- 🏠 **6 Unique Family Members** - Each with distinct personalities and LLM providers
- 💭 **Conversation Memory** - Personas remember and reference previous messages
- 🛡️ **Child-Safe Responses** - Carefully engineered prompts for appropriate, caring interactions
- 🔐 **Secure API Storage** - Encrypted API key management in `~/.familyai`
- 🔄 **Multi-Provider Support** - Groq, OpenAI, Anthropic, Cerebras, Google
- 📱 **WhatsApp-like Interface** - Familiar chat experience with recent conversations
- 🎨 **Rich UI** - Beautiful terminal interface with markdown support
- ⚡ **Retry & Fallback** - Robust error handling and graceful degradation

## 🚀 Quick Start

### Installation

#### Option 1: Install from PyPI (Recommended)
```bash
pip install familycli
```

#### Option 2: Install from Source
```bash
# Clone the repository
git clone https://github.com/AIMLDev726/ai-family-cli.git
cd ai-family-cli

# Install in development mode
pip install -e .
```

### First Run

```bash
# Start the Family AI CLI
familycli

# Or if installed from source
python -m src.main
```

### Setup API Keys

1. Choose option `4` (Settings & Management)
2. Select `API Key Management`
3. Add keys for your preferred providers (Groq recommended for speed)

## 📋 CLI Commands

```bash
# Main command
familycli                    # Start the family chat interface

# Alternative (if installed from source)
python -m src.main          # Direct module execution
```

### Usage
1. Initialize the database:
   ```sh
   python src/main.py
   ```
2. Register a user and login via CLI prompts.
3. Create personas, start chat sessions, and interact with AI family members.


## Configuration Management
- All configuration is managed via JSON files in the `config/` directory and can be overridden by environment variables.
- Use `src/config/config_manager.py` to load, get, and reload config at runtime.
- Example:
  ```python
  from src.config.config_manager import ConfigManager
  config = ConfigManager().load('llm_providers')
  value = ConfigManager().get('llm_providers', 'default_provider')
  ConfigManager().reload('llm_providers')
  ```
- Environment variable override: set `LLM_PROVIDERS_OPENAI_API_KEY` to override OpenAI key in config.
## Performance Optimization
- Database uses connection pooling and batch commit for high throughput.
- LLM responses are cached (LRU) and API usage is tracked for cost management.
## Error Handling
- All critical operations have robust error handling and failover logic.
- LLM manager supports rate limit handling and provider failover.
- Streaming and chat modules recover from deadlocks and interruptions.
## Runtime Reload
- You can reload configuration at runtime using the `reload` method in `ConfigManager` and `UniversalLLMManager`.

## Project Structure
```
familycli/
├── src/
│   ├── auth/
│   ├── personas/
│   ├── chat/
│   ├── llm/
│   ├── database/
│   ├── ui/
│   └── main.py
├── config/
│   ├── llm_providers.json
│   ├── app_config.json
│   └── default_personas.json
├── requirements.txt
├── README.md
```

## Security
- All sensitive data is encrypted at rest.
- API keys are stored securely and never exposed in logs.

## Testing
- Run unit and integration tests with pytest:
  ```sh
  pytest
  ```

## Extending
- Add new LLM providers by implementing a subclass of `BaseLLMProvider`.
- Add new UI features in `src/ui/`.

## 👨‍💻 Creator

**Created by AIMLDev726**
- Email: aistudentlearn4@gmail.com
- GitHub: [@AIMLDev726](https://github.com/AIMLDev726)

## 🐛 Reporting Issues & Getting Help

### How to Report a Bug

1. **Check Existing Issues**: [Browse current issues](https://github.com/AIMLDev726/ai-family-cli/issues) to see if it's already reported
2. **Create New Issue**: [Report a new bug](https://github.com/AIMLDev726/ai-family-cli/issues/new)
3. **Provide Details**: Include the following information:

**Bug Description**
A clear description of what went wrong

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What you expected to happen

**Environment**
- OS: [e.g., Windows 11, macOS 13, Ubuntu 22.04]
- Python Version: [e.g., 3.11.5]
- Family CLI Version: [e.g., 1.0.0]

**Error Messages**
Any error messages or logs (check ~/.familyai/logs/familycli.log)

**Screenshots**
If applicable, add screenshots to help explain the problem


### Request a Feature

Have an idea to make Family AI CLI better? [Request a feature](https://github.com/AIMLDev726/ai-family-cli/issues/new) and include:

- **Feature Description**: What you'd like to see added
- **Use Case**: How this would help families
- **Child Safety**: How this maintains our family-friendly focus

### Beta Testing Feedback

As a beta tester, your feedback is especially valuable! Please share:

- **What works well**: Features you love and find useful
- **What's confusing**: Areas that need better documentation or UX
- **Performance issues**: Slow responses, crashes, or errors
- **Family experience**: How your family interacts with the AI personas
- **Safety concerns**: Any responses that seem inappropriate for children

### Get Help

- **GitHub Discussions**: [Ask questions and share ideas](https://github.com/AIMLDev726/ai-family-cli/discussions)
- **Documentation**: Check our [Contributing Guide](CONTRIBUTING.md)
- **Email**: aistudentlearn4@gmail.com for private matters

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on:

- How to submit bug reports and feature requests
- Development setup and coding standards
- Pull request process
- Code of conduct

### Quick Contributing Steps

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the **Mozilla Public License 2.0 (MPL-2.0)**.

See the [LICENSE](LICENSE) file for details.

### What this means:
- ✅ You can use this software for any purpose
- ✅ You can modify and distribute the software
- ✅ You can use it in proprietary software
- ⚠️ If you modify MPL-licensed files, you must share those modifications
- ⚠️ You must include the original license and copyright notices

## 🙏 Acknowledgments

- Built with ❤️ for families who want safe AI interactions
- Powered by multiple LLM providers for the best experience
- Inspired by the need for child-safe AI conversations

---

**Family AI CLI** - Bringing AI family members to life in your terminal! 👨‍👩‍👧‍👦