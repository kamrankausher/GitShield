import json
import os

# -------------------------------
# PURPOSE:
# Store and track developer behavior
# -------------------------------

MEMORY_FILE = ".devflow_memory.json"


def load_memory():
    """
    Load user behavior memory
    """
    if not os.path.exists(MEMORY_FILE):
        return {}

    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def save_memory(data):
    """
    Save memory to file
    """
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)


def update_memory(warnings):
    """
    Update counts of warnings
    """
    memory = load_memory()

    for w in warnings:
        memory[w] = memory.get(w, 0) + 1

    save_memory(memory)

    return memory