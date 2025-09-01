# Contributing to Family AI CLI

Thank you for your interest in contributing to Family AI CLI! This document provides guidelines and information for contributors.

## 🎯 Project Vision

Family AI CLI aims to provide a safe, engaging, and educational AI chat experience for families. All contributions should align with this vision of creating child-safe, family-friendly AI interactions.

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- A text editor or IDE
- API keys for at least one LLM provider (Groq, OpenAI, Anthropic, etc.)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ai-family-cli.git
   cd ai-family-cli
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

4. **Set Up API Keys**
   ```bash
   # Create .env file or set environment variables
   export GROQ_API_KEY="your_groq_key_here"
   export OPENAI_API_KEY="your_openai_key_here"
   ```

5. **Test Installation**
   ```bash
   familycli  # Should start the application
   ```

## 📋 How to Contribute

### Reporting Bugs

1. **Check existing issues** first to avoid duplicates
2. **Use the bug report template** when creating new issues
3. **Include detailed information**:
   - Operating system and Python version
   - Steps to reproduce the bug
   - Expected vs actual behavior
   - Error messages and logs
   - Screenshots if applicable

### Suggesting Features

1. **Check existing feature requests** to avoid duplicates
2. **Use the feature request template**
3. **Explain the use case** and how it benefits families
4. **Consider child safety implications**

### Code Contributions

#### Before You Start

1. **Create an issue** to discuss major changes
2. **Check the project roadmap** for planned features
3. **Ensure your idea aligns** with the family-safe vision

#### Development Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Follow coding standards**:
   - Use meaningful variable and function names
   - Add docstrings to all functions and classes
   - Follow PEP 8 style guidelines
   - Keep functions focused and small
   - Add type hints where appropriate

3. **Write tests** for new functionality
4. **Update documentation** as needed
5. **Test thoroughly** before submitting

#### Code Style Guidelines

- **Python Style**: Follow PEP 8
- **Imports**: Group imports (standard library, third-party, local)
- **Docstrings**: Use Google-style docstrings
- **Comments**: Explain why, not what
- **Error Handling**: Use appropriate exception handling
- **Logging**: Use the logging module, not print statements

#### Example Code Structure

```python
"""
Module docstring explaining the purpose.
"""

import logging
from typing import Optional, List

from rich.console import Console
from src.database.models import User

logger = logging.getLogger(__name__)
console = Console()

def create_user(username: str, password: str) -> Optional[User]:
    """
    Create a new user with the given credentials.
    
    Args:
        username: The desired username
        password: The user's password
        
    Returns:
        User object if successful, None otherwise
        
    Raises:
        ValueError: If username or password is invalid
    """
    try:
        # Implementation here
        logger.info(f"Creating user: {username}")
        return user
    except Exception as e:
        logger.error(f"Failed to create user {username}: {e}")
        return None
```

## 🛡️ Child Safety Guidelines

**CRITICAL**: All contributions must maintain child safety standards:

1. **Content Filtering**: Ensure all AI responses are appropriate for children
2. **Privacy Protection**: Never log or store personal information
3. **Safe Defaults**: Default settings should be the safest options
4. **Clear Boundaries**: AI personas should maintain appropriate boundaries
5. **Educational Value**: Prioritize educational and positive interactions

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_specific.py
```

### Writing Tests

- Write tests for all new functionality
- Include edge cases and error conditions
- Use descriptive test names
- Mock external dependencies (API calls, file system)

## 📝 Documentation

### Code Documentation

- Add docstrings to all public functions and classes
- Update README.md for user-facing changes
- Update inline comments for complex logic

### User Documentation

- Update CLI help text for new commands
- Add examples for new features
- Update configuration documentation

## 🔄 Pull Request Process

1. **Ensure your branch is up to date**
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Create a clear PR description**:
   - What changes were made and why
   - How to test the changes
   - Any breaking changes
   - Screenshots for UI changes

3. **Ensure all checks pass**:
   - All tests pass
   - Code style checks pass
   - No merge conflicts

4. **Respond to feedback** promptly and professionally

5. **Squash commits** if requested before merging

## 🏷️ Commit Message Guidelines

Use clear, descriptive commit messages:

```
feat: add new persona creation wizard
fix: resolve database connection timeout
docs: update API key setup instructions
refactor: simplify chat message handling
test: add tests for user authentication
```

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: aistudentlearn4@gmail.com for private matters

## 📜 Code of Conduct

### Our Standards

- **Be respectful** and inclusive
- **Focus on child safety** in all decisions
- **Provide constructive feedback**
- **Help others learn and grow**
- **Maintain professionalism**

### Unacceptable Behavior

- Harassment or discrimination
- Inappropriate content or language
- Spam or off-topic discussions
- Sharing personal information without consent

## 🎉 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- Special thanks for major features

---

Thank you for helping make Family AI CLI better for families everywhere! 👨‍👩‍👧‍👦

**Created by AIMLDev726**
