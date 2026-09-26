# Contributing to Event Management System (EMS)

Thank you for your interest in contributing to the EMS project! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Report issues responsibly
- Respect the project's licensing

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported
2. Use a clear, descriptive title
3. Provide specific examples to demonstrate the issue
4. Describe the exact steps to reproduce the problem
5. Provide specific examples to clarify the issue
6. Explain the behavior you expected and what actually happened
7. Include screenshots or logs if applicable

### Suggesting Enhancements

1. Use a clear, descriptive title
2. Provide a detailed description of the suggested feature
3. List some examples showing how the feature would be used
4. Describe the current behavior and expected behavior
5. Explain why this enhancement would be useful

### Pull Requests

1. Fork the repository and create a new branch from `main`
2. Branch naming: `feature/description` or `fix/description`
3. Make your changes and test thoroughly
4. Follow the existing code style and conventions
5. Commit with clear, descriptive messages
6. Push to your fork and submit a pull request
7. Ensure all tests pass and the code is properly documented

## Development Setup

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/ems.git
   cd ems
   ```

2. Create virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables
   ```bash
   cp .env.example .env
   ```

5. Run the application
   ```bash
   python run.py
   ```

## Code Style

- Follow PEP 8 guidelines for Python
- Use meaningful variable and function names
- Write docstrings for functions and classes
- Keep functions small and focused
- Use type hints where appropriate

## Testing

Before submitting a pull request, ensure:

- Your code doesn't break existing functionality
- You test edge cases and error scenarios
- You've tested on both development and production configs if possible

## Documentation

- Update README.md if adding new features
- Add docstrings to new functions and classes
- Update SECURITY_BEST_PRACTICES.md for security-related changes
- Include examples for new features

## Need Help?

- Check the README.md for getting started information
- Review existing issues and pull requests
- Open an issue to ask questions

## License

By contributing to EMS, you agree that your contributions will be licensed under its MIT License.

Thank you for contributing!
