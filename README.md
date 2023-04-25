# diff-GPT

diff-GPT is a simple command-line application that generates a human-readable summary of the changes made in a GitHub pull request. It uses OpenAI's GPT-4 language model to help non-technical users understand the purpose and impact of the changes.

## Features

- Easy-to-use command-line interface
- Simply provide the URL to your github PR as input
- Generates a detailed summary of a pull request
- Uses OpenAI's GPT-3.5 language model for natural language processing
- Summary is presented in a non-technical language for a wider audience

## Requirements

1. Python 3.9 (recommended) or 3.6+
2. A github personal access token for accessing your PR in a private repo.
3. An openai API key

## Installation

1. [Make sure you have Python installed on your system.](https://www.python.org/downloads/)
2. [Generate a github personal access token (PAT)](https://github.com/settings/tokens)
3. Clone this repository:

```bash
git clone https://github.com/yourusername/gpt-pr-summarizer.git
cd gpt-pr-summarizer
```

3. Install the required packages:

```
pip install -r requirements.txt
```

4. Create a .env file with your OpenAI API key and GitHub Personal Access Token (PAT) by renaming the provided .env.template:

```
cp .env.template .env
```

Replace `your_openai_api_key_here` and `your_github_personal_access_token` with your actual API key and PAT. No quotes or spaces.

## Usage

Run the script with a GitHub Pull Request URL as the argument:

```
python main.py <GitHub Pull Request URL>
```

After a few moments, depending on the size of the PR, your PR summary will be printed to the console.

![diff-GPT example](https://cdn.discordapp.com/attachments/949084429601632316/1100442891769348166/image.png)
