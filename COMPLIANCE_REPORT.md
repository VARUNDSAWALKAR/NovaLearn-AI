# UNLOX LangChain Mini-Project — Compliance & Verification Report

## Source of requirements

The supplied two-page **LANGCHAIN MINI-PROJECT GUIDELINES** PDF specifies **AI Question-Answering Chatbot** with a user-selected topic, one LLM, one prompt template, user-question input, AI-generated answer, API key in `.env`, basic error handling, and tests using at least five questions. It suggests Python, LangChain, Gemini/another LLM, and python-dotenv, with `app.py`, `.env`, `requirements.txt`, and `README.md` files.

## Implemented project

**NovaLearn AI** is a Streamlit AI study-assistance chatbot with three modes: Study Assistant, Python Doubt Solver, and Interview Preparation. It uses a LangChain prompt chain and a Gemini model, configured with a local `.env` key.

## Requirement-by-requirement mapping

| Requirement from PDF | Status in source | Evidence |
|---|---|---|
| Choose a topic | Implemented | Study Assistant is default; sidebar also offers Python Doubt Solver and Interview Preparation |
| One LLM such as Gemini | Implemented (requires working credential) | `ChatGoogleGenerativeAI` in `chatbot.py` |
| LangChain prompt template | Implemented | `ChatPromptTemplate.from_messages` |
| User question as input | Implemented | Streamlit `st.chat_input` in `app.py`; CLI optional |
| AI-generated answer as output | Implemented (live API unverified) | `chain.invoke()` → `StrOutputParser()` → Streamlit response |
| API key stored in `.env` | Implemented locally | Password-masked sidebar key editor persists to `.env`; `.gitignore` protects it |
| Basic error handling | Implemented | Empty/long question, missing key, auth, model, quota, outages, timeouts |
| Five-question testing | Offline coverage passed; live pending | `tests/test_chatbot.py` (mock provider) and `tests/live_test_questions.py` (real provider) |
| `app.py`, `.env`, `requirements.txt`, `README.md` | Implemented | `.env` is created **locally** after secure setup; intentionally omitted from public ZIP |

## Test evidence

- Python syntax compilation: passed.
- 17 offline unit tests: passed. Includes five sample-question invocations through a mock LangChain contract, input validation, key persistence, key precedence, and provider error classification.
- Real Gemini API test: **not yet run successfully in this environment**. The bundled app includes an explicit **Test API connection** button; it must be used with a valid private key before claiming live connectivity.

## Engineering fixes since initial release

1. `.env` is always looked up relative to `chatbot.py` rather than an arbitrary terminal directory.
2. Users may configure a key through a password-masked UI and save it without manual file editing.
3. `AQ.`-prefix keys are accepted syntactically, with specific guidance for unsupported credential-type responses.
4. New default model is `gemini-3.5-flash-lite` rather than a model restricted for newer projects.
5. Connection indicators distinguish **configuration detected** from **API connection verified**.
6. A `RUN_ME.bat` launcher creates and uses the correct `.venv` automatically, avoiding accidental installation of a different project's dependencies.

## Submission instructions

On a Windows 11 machine, extract the ZIP, launch the app, configure a **new private key**, verify an API reply, then submit screenshots showing five real question/answer interactions. Do not include `.env`, screenshots of the secret, or source code containing a key in the GitHub repository or report.

## Scope note

A source implementation and offline validation are provided, but live Gemini response quality and the user's account permissions cannot be validated without a successful authenticated request. A 401, 403, 404, 429, or 503 response is not equivalent to a project code failure; the app gives diagnostics for each.
