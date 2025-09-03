# Where to Store API Keys

API keys can be set in one of the following ways:

1. **Add to `~/.bashrc` or `~/.bash_profile`**  
   Insert the following lines, replacing with your actual API keys. If you do not have an optional API key (e.g., Anthropic), leave the value blank.

```bash
export GOOGLE_API_KEY=your_gemini_api_key
export GOOGLE_APPLICATION_CREDENTIALS=path/to/gemini.json
export OPENAI_API_KEY=your_openai_api_key
export PERPLEXITY_API_KEY=your_perplexity_api_key
export ANTHROPIC_API_KEY=your_anthropic_api_key
export FUTURE_HOUSE_API_KEY=your_fh_key
```

2. **Set in the Terminal**  
   Copy and paste the above lines directly into your terminal session.

3. **Create a `.env` File**  
   In the directory where Denario will be run, create a `.env` file containing:

```bash
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_APPLICATION_CREDENTIALS=path/to/gemini.json
OPENAI_API_KEY=your_openai_api_key
PERPLEXITY_API_KEY=your_perplexity_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
FUTURE_HOUSE_API_KEY=your_fh_key
```

**Note:**  
Never share your API keys. Always monitor your usage and costs on each provider's platform.

[← Back to API Keys](apikeys.md)
