# NovaLearn AI — UNLOX LangChain Mini-Project

**AI Question-Answering Chatbot** with a dark violet/cyan Streamlit interface, secure local Gemini API-key setup, and a LangChain prompt → Gemini model → output parser pipeline.

This project addresses the supplied UNLOX **LANGCHAIN MINI-PROJECT GUIDELINES** (two-page PDF). It includes a selectable **Study Assistant**, **Python Doubt Solver**, and **Interview Preparation** chatbot.

## 1. Quick start (Windows 11)

1. Extract the whole ZIP; open the `langchain_project` folder (the one containing `app.py`).
2. **Double-click `RUN_ME.bat`**. It creates a Python 3.11 virtual environment, installs the required packages and starts Streamlit. It does not need a global Streamlit installation.
3. Open the address printed in the terminal, usually `http://localhost:8501`.
4. In the left sidebar open **🔐 Add / replace Gemini API key**.
5. Paste your own **Gemini Developer API** key, select a model, and click **💾 Save key on this PC**.
6. Click **🔌 Test API connection**. A verified success state appears only after a real Gemini response.
7. Ask a question in the chat box.

To run without double-clicking the batch file:

```powershell
cd "C:\path\to\langchain_project"
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Using `.venv\Scripts\python.exe` directly avoids PowerShell execution-policy issues entirely.

If you want to use the provided PowerShell launcher from any directory:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1
```

### Which folder should I run it from?

**Use the directory where `app.py`, `chatbot.py`, `requirements.txt`, and `RUN_ME.bat` are together.** The project does not need to be moved into an older `unlox` folder, and should not be launched from the ZIP itself. The launcher selects its own directory regardless of where PowerShell starts.

## 2. Key setup and security

- The sidebar key field is **password-masked**. Saving it writes a `.env` file *on your computer* beside `app.py`, not into Python source files or GitHub.
- The `.env` file is not included in the downloadable ZIP and is listed in `.gitignore`.
- You can also manually create `.env` from `.env.example`:

```env
GOOGLE_API_KEY=YOUR_OWN_GEMINI_KEY
GEMINI_MODEL=gemini-3.5-flash-lite
```

- Alternatively, the loader accepts `GEMINI_API_KEY` or `GOOGLE_API_KEY` from the operating-system environment.
- **Never publish a key** in a repository, report, screenshot, or chat. If you have already shared a key, revoke it and generate a replacement at https://aistudio.google.com/apikey.
- The app never prints the key in status messages, and generic API failures are displayed without raw provider exception payloads.

### If a key begins with `AQ.`

Some Google AI Studio keys now start with `AQ.`. The app does **not** reject this prefix. However, Google AI Developer Forum users report occasional `401 ACCESS_TOKEN_TYPE_UNSUPPORTED` failures from some `AQ.` credentials; a valid-looking prefix cannot guarantee that the key works. Use **Test API connection** to distinguish a local setup problem from actual API rejection.

### Which model?

Default is **`gemini-3.5-flash-lite`**. Google has restricted Gemini 2.5 Flash access for new projects. You can change the selected model to `gemini-3.8-flash` or `gemini-3.5-flash` from the sidebar if your account has access. No model is guaranteed to be available to every account; model and quota failures are described in the UI.

## 3. Features

- Responsive, dark SaaS-style Streamlit interface, with violet/cyan gradients and branded sidebar
- Selectable topic and three example question prompts
- LangChain `ChatPromptTemplate`, `MessagesPlaceholder`, `ChatGoogleGenerativeAI`, and `StrOutputParser`
- In-session conversational context (10 recent messages)
- Input validation and basic error handling for 401/403, 404, 429, 503 and timeouts
- Password-masked sidebar key input with local `.env` saving
- Real **Test API connection** action (makes one Gemini API request)
- Windows double-click launcher and PowerShell launcher
- Offline unit tests plus a five-question optional real-API smoke test

## 4. Architecture

```text
User question (Streamlit app.py / optional CLI)
       ↓
validate_question()
       ↓
ChatPromptTemplate(system prompt + recent messages + question)
       ↓
LangChain | ChatGoogleGenerativeAI (Gemini Developer API)
       ↓
StrOutputParser()
       ↓
answer_question() validates response or describes provider failure
       ↓
Display in chat UI

API key → password-masked sidebar field → locally stored .env
        → load_settings() → Gemini client
```

## 5. Testing

Offline tests don't call Gemini and do not need an API key:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
```

Live tests send **five real questions** (API quota and charges may apply):

```powershell
.\.venv\Scripts\python.exe tests\live_test_questions.py
```

Sample questions:
1. What is a Python list?
2. Explain recursion with a simple example.
3. What is the difference between AI and ML?
4. Explain database normalization and 3NF.
5. Give me three tips for a software engineering interview.

**Verification status at packaging:** 17 offline unit tests passed and source syntax checked. A successful live Gemini request has **not** been verified in this environment. The user must configure a working API credential and press **Test API connection** on their PC.

## 6. PDF requirement mapping

| PDF minimum requirement | Where implemented |
|---|---|
| Language model | `chatbot.py` → `ChatGoogleGenerativeAI` |
| LangChain prompt template | `chatbot.py` → `ChatPromptTemplate.from_messages` |
| User question as input | `app.py` → `st.chat_input()`; `cli.py` |
| AI-generated answer | LangChain chain invocation and rendered chat message |
| API key in `.env` | `save_local_settings`, `load_settings`; `.env.example` |
| Basic error handling | `validate_question()`, `_safe_remote_error()`, UI error feedback |
| Five questions tested | Offline tests and `tests/live_test_questions.py` |
| Suggested project files | `app.py`, `README.md`, `requirements.txt`, `.env.example`; locally generated `.env` |

## 7. Troubleshooting

| Symptom | Fix |
|---|---|
| `GOOGLE_API_KEY missing` | Use the sidebar key input and click **Save key on this PC**. |
| Key loaded but no answer | Click **Test API connection**, read its specific error classification. |
| `401 ACCESS_TOKEN_TYPE_UNSUPPORTED` | Gemini rejected the credential type; inspect/recreate your key in Google AI Studio. |
| `401` or `403` | Check Gemini Developer API key validity and account/API restrictions. |
| `404` | Model is not available to your project; change it in sidebar. |
| `429` | Rate limit/quota; see usage limits and billing. |
| `503` | Temporary model-side issue; retry or choose another model. |
| `No module named streamlit` | Launch via `RUN_ME.bat` to install into the project's virtual environment. |
| PowerShell cannot find `Activate.ps1` | The `.venv` isn't created in this directory; use `RUN_ME.bat` or run `py -3.11 -m venv .venv`. |
| Installs pandas/Jupyter instead of Streamlit | You're installing another project's `requirements.txt`. Open the new `langchain_project` folder. |

## 8. Files

```text
langchain_project/
├── app.py                   # Streamlit web UI
├── chatbot.py               # LangChain, Gemini, configuration, errors
├── cli.py                   # Optional command-line chatbot
├── .env.example             # API key template (not a real key)
├── .gitignore               # Excludes .env, .venv, caches
├── .streamlit/config.toml   # Theme settings
├── requirements.txt
├── RUN_ME.bat               # Windows double-click launcher
├── run.ps1                  # PowerShell launcher
├── README.md                # GitHub project documentation
├── COMPLIANCE_REPORT.md     # Comparison against PDF
└── tests/
    ├── test_chatbot.py
    ├── test_configuration.py
    └── live_test_questions.py
```

## References

- Gemini API: https://ai.google.dev/gemini-api/docs
- Google AI Studio API keys: https://aistudio.google.com/apikey
- LangChain Google Gemini integration: https://pypi.org/project/langchain-google-genai/
- Streamlit documentation: https://docs.streamlit.io
