# FeedForge 🎯

A powerful tool to customize your YouTube feed based on your content preferences. FeedForge uses AI to understand your interests, searches for relevant videos, and automatically interacts with them to train YouTube's recommendation algorithm.

## 🌟 Features

- **AI-Powered Content Discovery**: Uses OpenAI's GPT-4 to generate relevant search keywords from your content preferences
- **YouTube API Integration**: Searches for high-quality videos matching your interests
- **Automated Browser Interaction**: Uses browser automation to play videos and train YouTube's algorithm
- **Customizable Playback**: Control how long each video plays during the training process
- **Cross-Platform Support**: Works on Windows, macOS, and Linux

## 🔧 Prerequisites

Before running FeedForge, ensure you have:

1. **Python 3.9 or higher** (3.11+ recommended)
2. **Google Chrome or Firefox browser** installed
3. **OpenAI API Key** - Get one from [OpenAI Platform](https://platform.openai.com/api-keys)
4. **YouTube Data API Key** - Get one from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)

## 📦 Installation

### Install from PyPI (Recommended)
```bash
pip install feedforge
```

### Development Installation
If you want to contribute or install from source:

#### 1. Clone the Repository
```bash
git clone https://github.com/RishabhKodes/feedforge.git
cd feedforge
```

#### 2. Create Virtual Environment
```bash
python3.9 -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### 3. Install in Development Mode
```bash
pip install -e .
```

This will automatically install all required dependencies:
- langchain-openai (>=0.0.5)
- google-api-python-client (>=2.0.0)
- selenium (>=4.0.0)
- click (>=8.0.0)
- python-dotenv (>=1.0.0)
- geckodriver-autoinstaller (>=0.1.0)
- chromedriver-autoinstaller (>=0.6.0)
- openai (>=1.0.0)

## ⚙️ Configuration

### 1. Create Environment File
Create a `.env` file in the project root directory:
```bash
touch .env
```

### 2. Add API Keys
Add your API keys to the `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
YOUTUBE_API_KEY=your_youtube_api_key_here
```

### Getting Your API Keys

#### OpenAI API Key:
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key and add it to your `.env` file

#### YouTube Data API Key:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the "YouTube Data API v3"
4. Go to "Credentials" → "Create Credentials" → "API Key"
5. Copy the key and add it to your `.env` file

## 🧪 Testing Installation

To verify that FeedForge is installed correctly, run the test script:

```bash
python test_feedforge.py
```

This will test:
- All required imports
- Environment variable handling
- CLI command availability

## 🚀 Usage

### Basic Usage
```bash
feedforge "I want to see videos about people building successful side projects and sharing their journey"
```

### With Custom Duration
Control how long each video plays (default is 2 seconds):
```bash
feedforge "machine learning tutorials for beginners" --duration 5
```

### Example Commands
```bash
# Startup and entrepreneurship content
feedforge "startup founders sharing their journey and lessons learned"

# Programming tutorials
feedforge "python programming tutorials and coding best practices" --duration 3

# Creative content
feedforge "digital art tutorials and creative processes" --duration 4

# Productivity and self-improvement
feedforge "productivity tips and morning routines of successful people"
```

## 🔧 How It Works

1. **Input Processing**: FeedForge takes your content description and uses OpenAI's GPT-4 to generate relevant search keywords
2. **Video Discovery**: Uses YouTube's Data API to search for high-quality videos matching those keywords
3. **Smart Selection**: Implements round-robin selection to ensure diverse content from different keywords
4. **Browser Automation**: Opens Chrome and automatically plays each video for the specified duration
5. **Algorithm Training**: Your interactions help train YouTube's recommendation algorithm to show similar content

## 🛠️ Troubleshooting

### Common Issues

#### "No .env file found"
Make sure you've created a `.env` file in the project root directory with your API keys.

#### "Chrome not found"
FeedForge will automatically try to find Chrome in common locations:
- **macOS**: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
- **Windows**: `C:\Program Files\Google\Chrome\Application\chrome.exe`
- **Linux**: `/usr/bin/google-chrome`

If Chrome is installed elsewhere, you may need to update the path in `src/feedforge/core.py`.

#### "Invalid API Key"
- Verify your API keys are correct in the `.env` file
- Ensure your OpenAI account has sufficient credits
- Check that YouTube Data API is enabled in Google Cloud Console

#### "No videos found"
Try using more general or different keywords in your description.

### Debug Mode
For debugging, you can run the project with Python directly:
```bash
python -m feedforge.cli "your content description here"
```

## 📁 Project Structure

```
feedforge/
├── src/
│   └── feedforge/
│       ├── __init__.py      # Automatic Playwright setup
│       ├── cli.py           # Command-line interface
│       └── core.py          # Main functionality
├── pyproject.toml           # Project configuration
├── test_feedforge.py        # Installation test script
├── .env.example             # Environment variables template
├── .env                     # API keys (you create this)
└── README.md               # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test your changes: `python test_feedforge.py`
5. Ensure all tests pass: `feedforge --help`
6. Submit a pull request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/RishabhKodes/feedforge.git
cd feedforge

# Create virtual environment with Python 3.9+
python3.9 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Run tests
python test_feedforge.py
```

## 📄 License

This project is open source. Please check the license file for details.

## ⚠️ Disclaimer

This tool automates browser interactions with YouTube. Use responsibly and in accordance with YouTube's Terms of Service. The authors are not responsible for any violations of platform policies.

## 🆘 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Ensure all prerequisites are met
3. Verify your API keys are valid
4. Create an issue on GitHub with detailed error information

---

Happy feed customizing! 🎉
