# ENHANCE ✨ Your AI Prompts, Instantly.

[![PyPI - Version](https://img.shields.io/pypi/v/enhance-this?style=for-the-badge)](https://pypi.org/project/enhance-this/)
[![npm - Version](https://img.shields.io/npm/v/enhance-this?style=for-the-badge)](https://www.npmjs.com/package/enhance-this)
[![Homebrew - Version](https://img.shields.io/github/v/release/hariharen9/enhance-this?style=for-the-badge&label=homebrew)](https://github.com/hariharen9/homebrew-tap)
[![License](https://img.shields.io/github/license/hariharen9/enhance-this?style=for-the-badge)](LICENSE)

Tired of generic AI responses? **`enhance-this`** is your secret weapon. This lightning-fast CLI tool transforms your simple ideas into rich, detailed prompts, ensuring you get the best possible output from any AI model. It runs 100% locally using Ollama, so your data stays private.

Whether you're a developer, writer, student, or AI enthusiast, `enhance-this` makes your interactions with AI more powerful and intuitive.

---

## 🚀 Why You'll Love `enhance-this`

*   **Elevate Your Prompts**: Go from a basic idea like "write a blog post about AI" to a meticulously crafted prompt that gets superior results.
*   **Boost Productivity**: Automate prompt engineering. Get the perfect prompt copied to your clipboard in seconds.
*   **Stay Private**: Powered by your local Ollama models. Your data never leaves your computer.
*   **Save Time & Effort**: Free yourself from the tedious task of writing detailed prompts.
*   **Get Professional Results**: Consistently achieve better outputs from any AI model.

---

## ✨ Features

*   **Live Enhancement**: Watch your prompt get enhanced in real-time, right in your terminal.
*   **Interactive Mode**: Iteratively refine prompts in a session with `enhance --interactive`.
*   **Smart Model Management**: Intelligently finds and uses the best local Ollama model. No model? It can download one for you with `enhance --auto-setup`.
*   **Customizable Styles**: Choose from built-in styles (`detailed`, `creative`, `technical`) or create your own.
*   **Diff View**: Instantly see what's been improved with the `--diff` flag.
*   **Seamless Workflow**: Automatically copies the final prompt, ready to paste anywhere.
*   **History Tracking**: Revisit your best prompts with `enhance --history`.
*   **Configuration Wizard**: First-time setup made easy with an interactive configuration wizard.
*   **Visual Template Editor**: Create and edit custom prompt templates with your preferred text editor.

---

## 💼 Use Cases

`enhance-this` is perfect for...

*   **Developers**: Generating better code review prompts and technical documentation.
*   **Content Creators**: Crafting compelling blog posts and social media content.
*   **Students & Researchers**: Creating detailed research prompts and academic outlines.
*   **Business Professionals**: Developing persuasive emails, reports, and presentations.

**Example - Developer Workflow:**
```bash
# From a vague idea...
enhance "review my Python code"

# ...to a precise prompt.
# Output: "Conduct a comprehensive code review of the provided Python code. Focus on: PEP 8 compliance, code readability, potential bugs, performance optimizations, security vulnerabilities, and adherence to Python best practices..."
```

**Example - Content Creation:**
```bash
# From a simple topic...
enhance "write about sustainable fashion" -s creative

# ...to a detailed content brief.
# Output: "Create an engaging, well-researched article about sustainable fashion that captivates environmentally conscious readers. Include: compelling statistics, innovative materials, practical tips, and inspiring success stories..."
```

---

## ⚡ Get Started in Minutes

### Prerequisite: Ollama

First, make sure you have [Ollama](https://ollama.com/) installed and running.

### Installation

**PyPI**:
```bash
pip install enhance-this
```

**NPM**:
```bash
npm install -g enhance-this
```

**Homebrew (macOS & Linux)**:
```bash
brew install hariharen9/tap/enhance-this
```

---

## 🛠 Configuration Wizard

Setting up `enhance-this` has never been easier! Run the interactive configuration wizard to customize your experience:

```bash
enhance --config-wizard
```

The wizard will guide you through:
- Setting your Ollama host address
- Choosing your preferred enhancement style
- Configuring generation temperature
- Setting maximum response length
- Enabling/disabling automatic clipboard copying
- Selecting your preferred AI models

---

## 🎨 Visual Template Editor

Create custom prompt templates with our built-in visual editor that integrates with your preferred text editor:

```bash
enhance --template-editor
```

Features:
- Edit existing templates or create new ones
- Integration with your system's default text editor (nano, vim, emacs, etc.)
- Built-in templates as starting points
- Custom template management
- Real-time preview of template structure

The template editor will automatically use your system's default editor (defined by the `$EDITOR` environment variable) or fall back to `nano` if none is set.

---

## 💡 How to Use

| Command                        | Description                                           |
| ------------------------------ | ----------------------------------------------------- |
| `enhance "..."`                | Enhance a prompt.                                     |
| `enhance --interactive`        | Start an interactive session.                         |
| `enhance --diff`               | Show a diff of the changes.                           |
| `enhance -s <style>`           | Use a specific enhancement style.                     |
| `enhance --history`            | View your enhancement history.                        |
| `enhance --auto-setup`         | Download and set up a recommended model.              |
| `enhance --preload-model`      | Load a model into memory for faster responses.        |
| `enhance --config-wizard`      | Run the interactive configuration wizard.             |
| `enhance --template-editor`    | Launch the visual template editor.                    |

---

## ⚙️ Advanced Configuration

Customize `enhance-this` via `~/.enhance-this/config.yaml` and add your own prompt styles in `~/.enhance-this/templates/`.

---

## 🤝 Join Our Community!

Have ideas or found a bug? We'd love your help to make `enhance-this` even better. Check out our [CONTRIBUTING.md](./CONTRIBUTING.md) to get started.

**Love `enhance-this`?** Star 🌟 us on [GitHub](https://github.com/hariharen9/enhance-this) and share it with your network!

---

## 📄 License

This project is open-source and available under the MIT License. See the [LICENSE](./LICENSE) file for more details.

---

<div align="center">
  <p>Made with ❤️ by <a href="https://hariharen9.site">Hariharen</a></p>
</div>