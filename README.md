# IT Knowledge-Based System

A Python-powered intelligent troubleshooting engine designed to diagnose hardware, software, networking, storage, and gaming-related issues using rule-based reasoning.

## 📌 Features

* ✔️ Rule-based reasoning engine
* ✔️ Hardware, software, networking, gaming & storage issue detection
* ✔️ Priority level classification (LOW → CRITICAL)
* ✔️ Automatic troubleshooting steps generation
* ✔️ Preventive maintenance advice
* ✔️ Supports system metrics (CPU temp, RAM usage, etc.)

## 🗂️ Project Structure

```
knowledgebasedsystem/
├── knowledge/
│   ├── rules.py
│   └── facts.json
├── reasoning/
│   └── engine.py
├── ui/
│   └── app.py
```

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
cd YOUR-REPO
```

### 2. Create and Activate Virtual Environment

#### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the App

```bash
streamlit run ui/app.py
```

## 🧠 How It Works

The system uses a rule engine defined in `knowledge/rules.py` to:

* Analyze user questions
* Detect issue category
* Generate troubleshooting advice
* Produce step-by-step solutions
* Assign priority level
* Offer preventive maintenance tips

## 🧪 Example Query

```
"My laptop is overheating when gaming"
```

The system will generate:

* Hardware overheating advice
* Priority level
* Troubleshooting steps
* Preventive maintenance tips

## 📤 Pushing to GitHub

```bash
git add .
git commit -m "Initial commit: knowledge-based system"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
git push -u origin main
```

## 📝 License

This project is open-source. You may modify and reuse.

## 👤 Author

Eugen – Knowledge-Based System Developer
