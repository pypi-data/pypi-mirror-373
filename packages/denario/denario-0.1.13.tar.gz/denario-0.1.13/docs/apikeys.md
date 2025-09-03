# LLM APIs

Denario requires access to large language models (LLMs) to function. Currently, Denario supports LLMs from Google (Gemini series), OpenAI (GPT and o series), Anthropic (Claude), Perplexity (Sonar), and agents from [Futurehouse](https://platform.futurehouse.org/) (Owl). Access to all these models is not mandatory for experimentation; however, **at least OpenAI API access is required**, so an OpenAI API key must be configured.

API access is managed via keys generated on each provider's platform and set as environment variables. Most LLM providers require a small amount of credit to be added to your account, as usage typically incurs a cost (though this is relatively minor for experimentation).

The required and optional models for Denario's subsystems are summarized below:

| Subsystem         | OpenAI | Gemini | Vertex AI | Claude | Perplexity | FutureHouse |
| ----------------- | ------ | ------ | --------- | ------ | ---------- | ----------- |
| **Generate Ideas**    | 🟠     | 🟠     | 🟠        | 🟠     | ❌          | ❌           |
| **Methods**           | 🟠     | 🟠     | 🟠        | 🟠     | ❌          | ❌           |
| **Analysis**          | ✅      | 🟠     | 🟠        | 🟠     | ❌          | ❌           |
| **Paper Writing**     | 🟠     | 🟠     | ❌         | 🟠     | ❌          | ❌           |
| Citation Search | ❌      | ❌      | ❌         | ❌      | ✅          | ❌           |
| Check Idea        | 🟠      | 🟠      | 🟠         | 🟠      | 🟠          | ✅           |

## Quick Navigation

- **[How Much Money Is Needed?](how-much-money.md)** - Cost estimates and budgeting information
- **[Risk of Overspending](risk-overspending.md)** - Important precautions and monitoring tips
- **[Rate Limits](rate-limits.md)** - Understanding and managing API rate limits
- **[Obtaining API Keys](obtaining-api-keys.md)** - Step-by-step guides for each provider
- **[Vertex AI Setup](vertex-ai-setup.md)** - Detailed setup for Google Cloud Vertex AI
- **[FutureHouse](futurehouse.md)** - Setup for FutureHouse Owl agent
- **[Where to Store API Keys](where-to-store-api-keys.md)** - Environment variable configuration