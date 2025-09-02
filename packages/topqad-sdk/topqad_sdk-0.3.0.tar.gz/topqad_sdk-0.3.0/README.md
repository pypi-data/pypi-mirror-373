# TopQAD SDK for Python

The code in this repository is intended to make access to the TopQAD platform as easy as writing Python!  
This guide provides everything you need to set up your local development environment, run the demo script, and understand the core features of the SDK.

---

## 1. Development Setup

Follow these steps to set up a local environment for developing and testing the SDK.

### a. Create and Activate a Virtual Environment
This creates an isolated Python environment for the project.

Open your terminal and navigate to the root directory of this project.

Create the virtual environment:  
`python3 -m venv .venv`

Activate the environment:  
**macOS / Linux:**  
`source .venv/bin/activate`  
**Windows:**  
`.\.venv\Scripts\activate`

Your terminal prompt should now begin with `(.venv)`.

Update pip:  
`python -m pip install -U pip`

---

### b. Install the Package in Editable Mode
This project uses `pyproject.toml` to manage dependencies. The following command will install the SDK in editable mode (`-e`) along with all development dependencies. This means any changes you make to the source code are immediately reflected in your environment.

`pip install -e .`

---

### c. Get Your Refresh Token (Required for Authentication)
To use the SDK, you need a `TOPQAD_REFRESH_TOKEN` from the TopQAD portal.

1. Visit: [https://portal.topqad.1qbit-dev.com/](https://portal.topqad.1qbit-dev.com/)  
2. Go through the **registration** process and log in.  
3. Click your **profile picture** in the top right.  
4. Select **"Get refresh token"**.  
5. Copy the token shown.

> ⚠️ **Security Note:** Your refresh token is as sensitive as a password. Keep it safe and never commit it to source control.

Set the environment variable in your shell or put it in ```.env``` file in ```root```:  
**macOS / Linux:**  
`export TOPQAD_REFRESH_TOKEN="<PASTE_YOUR_TOKEN_HERE>"`  
**Windows:**  
`set TOPQAD_REFRESH_TOKEN="<PASTE_YOUR_TOKEN_HERE>"`

---

### d. Verify the Installation

Run the following to check that the `topqad-sdk` package is installed, see its version, and confirm the installation path:

```
pip show topqad-sdk
```
---

## 2. Running the Interactive Demo
To see the SDK in action, we have prepared an interactive Jupyter Notebook that demonstrates the core functionality of the Noise Profiler.

To run the demo, open and run the notebook located at:
```
Noise_Profiler_Demo.ipynb
```

This notebook will guide you through setting your authentication token and running a simulation.

## License

This project is licensed under the [Apache 2.0 License](LICENSE).