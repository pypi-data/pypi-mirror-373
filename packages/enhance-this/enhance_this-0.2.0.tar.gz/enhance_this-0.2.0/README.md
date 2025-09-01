# ENHANCE ✨ Your AI Prompts, Instantly.

[![PyPI - Version](https://img.shields.io/pypi/v/enhance-this?style=for-the-badge)](https://pypi.org/project/enhance-this/)
[![npm - Version](https://img.shields.io/npm/v/enhance-this?style=for-the-badge)](https://www.npmjs.com/package/enhance-this)
[![Homebrew - Version](https://img.shields.io/github/v/release/hariharen9/enhance-this?style=for-the-badge&label=homebrew)](https://github.com/hariharen9/homebrew-tap)

[![License](https://img.shields.io/github/license/hariharen9/enhance-this?style=for-the-badge)](LICENSE)

Are you tired of generic AI responses? Do you wish your AI models understood exactly what you need? **`enhance-this`** is your secret weapon. This lightning-fast command-line `(CLI)` tool transforms your simple ideas into rich, detailed prompts, ensuring you get the best possible output from any AI model. And the best part? It runs locally, keeping your data private and your workflow smooth.

Whether you're a developer, a student, a writer, or just curious about AI, `enhance-this` makes interacting with AI more powerful and intuitive.

-----

## 🚀 Why `enhance-this` Will Transform Your AI Workflow

In today's fast-paced world, getting quick, accurate, and high-quality results from AI is crucial. `enhance-this` is built for **speed**, **simplicity**, and **professional results**, allowing you to:

  * **Elevate Your AI Interactions**: Go from a basic idea like "write a blog post about AI" to a meticulously crafted prompt that guides the AI for a superior output.
  * **Boost Productivity**: No more manual prompt engineering! Get the perfect prompt copied to your clipboard in seconds, ready to paste.
  * **Maintain Privacy**: All enhancements are powered by **Ollama** models running directly on your machine. Your data never leaves your computer.
  * **Save Time & Effort**: Automate the process of creating effective prompts, freeing you up to focus on the core task.
  * **Professional-Quality Results**: Get consistently better outputs from any AI model with expertly crafted prompts.
  * **Seamless Integration**: Works with all major AI interfaces - just copy and paste your enhanced prompts.

-----

## ✨ Features That Make a Difference

`enhance-this` is packed with smart features designed to make your AI interactions effortless and powerful:

  * **Instant Enhancement, Live**: See your prompt being enhanced in real-time with animated spinners and progress indicators. It's like watching a master prompt engineer at work, right in your terminal.
  * **Interactive Mode**: Start an interactive session with `enhance --interactive` to refine your prompts iteratively with real-time feedback.
  * **Smart Model Management**: `enhance-this` intelligently finds and uses the best local Ollama model available. No model? It can even download a recommended one for you, with a clear progress bar.
  * **Tailor-Made Prompts**: Choose from built-in styles like `detailed`, `creative`, `technical`, `json`, `bullets`, `summary`, `formal`, and `casual`. Want something unique? You can easily create your **own custom prompt templates**!
  * **See the Difference**: Use the `--diff` flag to instantly compare your original prompt with the enhanced version, highlighting exactly what's been added for clarity and depth.
  * **Seamless Workflow**: Once enhanced, your refined prompt is automatically copied to your clipboard, ready for immediate use in any AI interface.
  * **History Tracking**: Keep track of your enhancements with the `enhance --history` command to revisit your best prompts.
  * **Highly Customizable**: A simple YAML configuration file lets you fine-tune everything from the AI's creativity (temperature) to default settings.
  * **Robust Error Handling**: Graceful handling of all edge cases including Ollama connectivity issues, missing models, clipboard compatibility across platforms, and network timeouts with helpful troubleshooting guidance.
  * **Cross-Platform Support**: Works flawlessly on macOS, Windows, and Linux with platform-specific error handling and clipboard support.
  * **Model Visibility**: Clearly displays which AI model is being used for each enhancement, so you always know what's powering your results.

-----

## 💼 Professional Use Cases

`enhance-this` is trusted by professionals across industries:

  * **Developers**: Generate better code review prompts, debugging requests, and technical documentation
  * **Content Creators**: Craft compelling blog posts, social media content, and marketing copy
  * **Students & Researchers**: Create detailed research prompts and academic writing guidelines
  * **Business Professionals**: Develop persuasive sales emails, reports, and presentation materials
  * **Designers**: Generate precise creative briefs for logos, UI/UX, and visual concepts
  * **Educators**: Create engaging lesson plans and educational materials

**Example Use Case - Developer Workflow:**
```bash
# Transform a vague request into a precise code review prompt
enhance "review my Python code"
# Output: "Conduct a comprehensive code review of the provided Python code. Focus on: PEP 8 compliance, code readability and maintainability, potential bugs or edge cases, performance optimizations, security vulnerabilities, and adherence to Python best practices. Provide specific examples with suggested improvements and explanations for each issue identified."
```

**Example Use Case - Regular User:**
```bash
# Transform a vague question into a precise & detailed prompt
enhance -s detailed "best places to eatout in bangalore"
# Output: 
# Objective: Provide an exhaustive list of top-rated restaurants in Bengaluru, considering various culinary preferences, regional specialties, and dining experiences.  

# Scope:  

# 1. Cuisine Analysis: Include a range of international and local cuisines, such as North Indian, South Indian (including dosa, idli, and vada), Chinese, Italian, Mexican, and Middle Eastern.  
# 2. Dining Experience: Cover various settings, including:  
#    - Fine dining restaurants with upscale ambiance  
#    - Casual eateries with outdoor seating or street food options  
#    - Specialty cafes serving coffee, pastries, or desserts  
# 3. Regional Focus: Highlight local favorites and hidden gems in specific neighborhoods or areas, such as:  
#    - HSR Layout  
#    - Koramangala  
#    - Indiranagar  
#    - Electronic City  
# 4. Food Quality and Safety: Prioritize restaurants with high food quality ratings, excellent hygiene standards, and a strong reputation for serving fresh ingredients.  

# Deliverables:  

# 1. A comprehensive list of 20–25 top-rated restaurants in Bengaluru, including:  
#    - Restaurant name  
#    - Address (with nearest landmark or metro station)  
#    - Cuisine type(s) served  
#    - Average rating (based on online reviews)  
# 2. A brief description (1–2 paragraphs) for each restaurant, highlighting its unique features, specialties, and any notable awards or recognition.  
# 3. Recommendations for the best restaurants in Bengaluru for:  
#    - Vegetarians and vegans  
#    - Non-vegetarians (including meat and seafood options)  
#    - Families with young children  
#    - Couples looking for a romantic dinner  

# Constraints:  

# 1. Filter by Rating: Only include restaurants with an average rating of 4 or higher on review platforms like Zomato, TripAdvisor, or Google Reviews.  
# 2. Exclusion Criteria: Exclude restaurants that are:  
#    - Closed permanently or temporarily  
#    - Not available for dine-in (only take-out or delivery)  
#    - Known for poor service or unhygienic conditions  

# Enhanced Clarity:  

# 1. Use precise and descriptive language to ensure accurate representation of each restaurant's offerings.  
# 2. Utilize relevant keywords and phrases to facilitate easy searchability.  

# Additional Analysis Dimensions:  

# 1. Price Range: Provide a price range (budget-friendly, moderate, upscale) for each restaurant to help users plan their dining experience accordingly.  
# 2. Accessibility: Note any accessibility features or considerations for visitors with disabilities.  
# 3. Reservations and Online Ordering: Indicate if reservations are recommended or available online, as well as options for ordering food through apps or websites.  

```

**Example Use Case - Content Creation:**
```bash
# Create a creative content brief
enhance "write about sustainable fashion" -s creative
# Output: "Create an engaging, well-researched article about sustainable fashion that captivates environmentally conscious readers. Include: compelling statistics on fashion's environmental impact, innovative sustainable materials and brands, practical tips for building a sustainable wardrobe, the economics of sustainable vs. fast fashion, and inspiring success stories. Use a conversational yet informative tone with real-world examples and actionable takeaways."
```

-----

## ⚡ Get Started in Minutes!

### Prerequisite: Get Ollama

`enhance-this` works hand-in-hand with **Ollama**, a fantastic tool that lets you run large language models locally. If you haven't already, download and install [Ollama](https://ollama.com/) for your operating system. Make sure it's running before you use `enhance-this`!

### Installation: Pick Your Favorite!

We've made `enhance-this` available through your preferred package manager:

**PyPI**: The most common way to install Python tools.

```bash
pip install enhance-this
```

**NPM**: If you're a Node.js user, this is for you!

```bash
npm install -g enhance-this
```

**Homebrew (macOS & Linux)**: Mac and Linux users can grab it with one command.

```bash
brew install hariharen9/tap/enhance-this
```

-----

## 💡 How to Use `enhance-this`

Using `enhance-this` is incredibly straightforward. Just tell it what you want to enhance!

**Basic Enhancement:**

```bash
enhance "write a blog post about AI"
# Output: "Create a comprehensive blog post about artificial intelligence that educates readers about current AI developments, applications, and implications. Structure the content with: an engaging introduction that hooks the reader, clear explanations of key AI concepts, real-world examples and case studies, discussion of both benefits and challenges, and actionable insights for the target audience. Ensure the tone is accessible to non-technical readers while maintaining accuracy and depth."
```

**Interactive Mode:**

```bash
enhance --interactive
```

**See the Magic with `--diff`:**

```bash
enhance "review my code" --diff
# Shows a side-by-side comparison of your original prompt and the new, improved version!
```

**Choose a Style:**

```bash
enhance "a logo for a coffee shop" -s creative
```

**View Your History:**

```bash
enhance --history
```

**Auto-Setup (Installs Recommended Model):**

```bash
enhance --auto-setup
```

**List Available Models:**

```bash
enhance --list-models
```

**Preload a Model for Faster Responses:**

```bash
enhance --preload-model
```

-----

## 🚀 Performance Tips

To get the fastest response times, you can preload a model into your computer's memory. This keeps the model ready to go, so you don't have to wait for it to load every time.

**Preload a Model:**

```bash
enhance --preload-model
```

This will load the best available model into memory and keep it there. For the best performance, we recommend using a fast and capable model like `llama3.1:8b` or `mistral`.

You can also configure Ollama to keep models alive for a specific duration. See the Ollama documentation for more details on the `keep_alive` parameter in your Modelfiles.

**Model Visibility**: During enhancement, you'll always see which model is being used displayed in the streaming response panel, so you know exactly what's processing your request.

**Pro Tip**: Use the `--auto-setup` command on first run to automatically download and configure the optimal model for your system.

**Performance Factors to Consider:**

Response speed and quality depend on several factors:
- Your system's CPU, RAM, and storage performance
- The size and complexity of the selected AI model
- The complexity of your prompt request
- Current system load and available resources

**Pro Tip**: Use the `--auto-setup` command on first run to automatically download and configure the optimal model for your system.

-----

## ⚙️ Advanced Configuration

`enhance-this` is highly customizable through its YAML configuration file located at `~/.enhance-this/config.yaml`:

```yaml
default_temperature: 0.7
default_style: detailed
ollama_host: http://localhost:11434
timeout: 30
max_tokens: 2000
auto_copy: true
display_colors: true
preferred_models:
  - llama3.1:8b
  - llama3
  - mistral
```

Create custom prompt templates by adding text files to `~/.enhance-this/templates/` with your desired style names.

-----

## 🛠️ Troubleshooting & Common Issues

**Ollama Not Running**: Make sure the Ollama service is active. Start it with `ollama serve` or check if it's running in your system's services.

**No Models Available**: Run `enhance --auto-setup` to automatically download and install a recommended model.

**Clipboard Issues**: On Linux, you may need to install `xclip` or `xsel`. On Windows and macOS, ensure clipboard permissions are granted.

**Slow Responses**: Try preloading your model with `enhance --preload-model` for faster subsequent requests.

**Inconsistent Quality**: Different models produce varying results. Experiment with different models using `enhance --list-models` to find the best one for your use case.

For detailed troubleshooting, see our [Troubleshooting Guide](./docs/TROUBLESHOOTING.md).


## 🤝 Join Our Community!

We're always looking to make `enhance-this` even better! If you have ideas, spot a bug, or just want to chat about prompt engineering, come join us. Check out our [CONTRIBUTING.md](./CONTRIBUTING.md) for details on how you can get involved. Your contributions help shape the future of this tool!

**Love `enhance-this`?** Star 🌟 us on [GitHub](https://github.com/hariharen9/enhance-this) and share it with your network!

-----

## 📄 License

This project is open-source and available under the MIT License - see the [LICENSE](./LICENSE) file for more details.

---

<div align="center">
  <p>Made with ❤️ by <a href="https://hariharen9.site">Hariharen</a></p>
  </div>