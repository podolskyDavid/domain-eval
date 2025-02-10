# AI Due Diligence Bot 🤖

A Slack bot that performs comprehensive analysis of pitch decks for AI-focused startups, helping with technical due diligence and market evaluation.

## Features ✨

- **Automated Pitch Deck Analysis**: Extracts and analyzes key sections from pitch decks:
  - Problem Statement
  - Market Opportunity
  - Technical Approach
  - Team Evaluation
  - Financial Analysis
  - Competitive Landscape
  - Product Roadmap

- **Multi-Model AI Analysis**: Leverages multiple AI models for comprehensive evaluation:
  - Claude 3.5 (Sonnet/Haiku) for section extraction
  - Perplexity AI for detailed analysis with citations
  - Specialized prompts for each section

- **Slack Integration**: Easy-to-use Slack interface for submitting and receiving pitch deck analyses

## Tech Stack 🛠️

- **Backend**: FastAPI + Python 3.11
- **AI Integration**: 
  - Anthropic Claude 3.5
  - Perplexity AI
- **Document Processing**: Docling for PDF parsing
- **Deployment**: Docker + Fly.io

## Setup 🚀

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/domain-eval.git
   cd domain-eval
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Set up environment variables**
   Create a `.env` file with:
   ```
   SLACK_BOT_TOKEN=your_slack_bot_token
   SLACK_APP_TOKEN=your_slack_app_token
   ANTHROPIC_API_KEY=your_anthropic_api_key
   PERPLEXITY_API_KEY=your_perplexity_api_key
   PORT=3000
   ```

4. **Run locally**
   ```bash
   poetry run uvicorn main:app --host 0.0.0.0 --port 3000
   ```

5. **Deploy with Docker**
   ```bash
   docker build -t ai-due-diligence .
   docker run -p 3000:3000 ai-due-diligence
   ```

## Usage 💡

1. Invite the bot to your Slack channel
2. Share a pitch deck PDF and mention the bot
3. The bot will analyze the deck and provide detailed insights for each section
4. Review the analysis with citations and sources

## Development 🔧

- Uses Poetry for dependency management
- Includes development tools: black, pytest, ruff
- Follows Python 3.11+ standards
