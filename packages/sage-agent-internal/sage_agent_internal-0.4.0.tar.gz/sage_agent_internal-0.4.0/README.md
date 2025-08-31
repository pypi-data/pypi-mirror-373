# **Sage Agent — The AI-Powered Assistant for Jupyter Notebooks**

![Logo](https://i.imgur.com/JdA8ilQ.png)

---

## **What is Sage Agent?**

**Sage is an AI-native notebook assistant that supercharges your existing Jupyter workflows.**

Built by leading AI and quant researchers from YC, Harvard, MIT, and Goldman Sachs, Sage brings real-time, context-aware assistance directly into JupyterLab.

Use natural language to clean data, write analysis code, debug errors, explore dataframes, and build models—faster and with fewer mistakes.

**No hallucinated code. No context switching. Just faster insights.**

---

## **Why Use Sage Agent in Jupyter?**

Whether you’re a quant, data scientist, or analyst living in notebooks, Sage helps you:

✅ Clean and transform messy data in seconds

✅ Visualize trends, rollups, and anomalies from a prompt

✅ Connect your custom databases in one click and easily explore from notebooks 

✅ Generate *runnable* Python or SQL that fits your current cell + variable context

✅ Auto-detect schema changes and debug downstream errors

✅ Stay private: run entirely *local-first* or in your own secure VPC

✅ Extend JupyterLab without changing how you work

---

## **Perfect For:**

- Data scientists cleaning huge CSVs
- Quant researchers testing ML pipelines
- Product and analytics teams tired of building dashboards and flaky notebooks
- Anyone tired of LLM tools that break their code

---

## **Installation**

### **📦 Requirements**

- JupyterLab >= 4.0.0
- NodeJS (for development)

### **🧠 Install Sage Agent:**

```
pip install jupyterlab sage_agent_internal
```

### **❌ Uninstall:**

```
pip uninstall sage_agent_internal
```

---

## **How to Get Started**

To unlock full functionality, you’ll need Sage API credentials.

👉 [**Request your API key**](https://sagebook.ai/#contact) or email us at [contact@sagebook.ai](mailto:contact@sagebook.ai)

---

## **Why Sage**

- ✅ Context-aware code gen: understands variables, dataframes, imports, and prior cells
- ✅ AI that *fixes* schema issues and silent join bugs
- ✅ Inline review + diffs before you run any code
- ✅ Visualizations via natural language (matplotlib, plotly, seaborn supported)
- ✅ BYO LLM: Anthropic, OpenAI, vLLM, Ollama, or HF endpoints
- ✅ Built to run in air-gapped / enterprise environments

---

## **Local Development Instructions**

To contribute or develop locally:

```
# Clone the repo and enter the directory
git clone https://github.com/sagebook/sage_agent_internal.git
cd sage_agent_internal

# Install in editable mode
pip install -e "."

# Link extension to JupyterLab
jupyter labextension develop . --overwrite

# Rebuild on changes
jlpm build
```

For auto-rebuild while editing:

```
# Watch source
jlpm watch

# Run JupyterLab in parallel
jupyter lab
```

---

## **Uninstall in Dev Mode**

```
pip uninstall sage_agent_internal
# Then manually remove labextension symlink from JupyterLab extensions dir.
```

---

## **Want to See Sage in Action?**

🎥 Try the demo notebook or explore at [https://sagebook.ai](https://sagebook.ai/)

---

**Built for teams working with sensitive data:**

- Zero data retention by default
- Optional BYO keys for Claude, OpenAI, or local models
- Notebook-specific controls for what the model can “see”
- Fine-grained telemetry settings

---

## **Contact**

Questions? Ideas?

Email: [fahim@sagebook.ai](mailto:fahim@sagebook.ai)

Website: [https://sagebook.ai](https://sagebook.ai/)

---

AI Jupyter Notebook, JupyterLab Extension, Jupyter Assistant, Data Science Assistant, Jupyter LLM, AI code generation, dataframe cleaning, Jupyter AI, Sagebook, Sage Agent, AI for dataframes, Jupyter SQL assistant, notebook extension