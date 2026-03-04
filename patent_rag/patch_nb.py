import json
import os

nb_path = r"d:\Projects\patent_multimodal\patent_rag\notebooks\demonstration.ipynb"

with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

new_source = [
    "import os\n",
    "import sys\n",
    "sys.path.append(os.path.abspath('..'))\n",
    "from dotenv import load_dotenv\n",
    "load_dotenv(os.path.join(os.path.abspath('..'), '.env'))\n",
    "import logging\n",
    "\n",
    "# Setup logging\n",
    "logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')\n",
    "logger = logging.getLogger()\n",
    "\n",
    "# Ensure GEMINI API key is set\n",
    "if 'GEMINI_API_KEY' not in os.environ:\n",
    "    print(\"Please set GEMINI_API_KEY environment variable.\")"
]

nb["cells"][1]["source"] = new_source

# Also update the evaluation import to be safe
for cell in nb["cells"]:
    if "from evaluation import EvaluationModule\n" in cell.get("source", []):
         cell["source"] = [s.replace("from evaluation import", "from evaluation import") for s in cell["source"]]

with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)

print("Notebook patched.")
