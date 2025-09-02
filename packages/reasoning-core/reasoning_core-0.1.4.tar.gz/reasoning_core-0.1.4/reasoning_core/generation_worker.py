from reasoning_core import DATASETS
import random
import pandas as pd
import json
from pathlib import Path
import argparse
import os
import sys
import time
from rich.console import Console
from rich.theme import Theme

# --- Argument Parsing (Original) ---
parser = argparse.ArgumentParser()
parser.add_argument('--num_examples', default=20_000, type=int)
parser.add_argument('-f', default=None)
# Default '0' makes script runnable standalone without crashing on int(None)
parser.add_argument('--id', default='0', type=str)
parser.add_argument('--version', default='rc0',type=str)
parser.add_argument('--out_path', default='generated_data', type=str)
parser.add_argument('--batch_size', default=12, type=int)
parser.add_argument("--levels", nargs="+", type=int, default=[0,2,4])

args, unknown = parser.parse_known_args()

# --- Rich Console Setup ---
WORKER_ID = args.id
COLORS = [
    "cyan", "magenta", "green", "yellow", "blue", "red", "bright_green",
    "bright_yellow", "bright_blue", "bright_magenta", "bright_cyan"
]
WORKER_COLOR = COLORS[int(WORKER_ID) % len(COLORS)]

custom_theme = Theme({
    "start": "bold green",
    "done": "bold blue",
    "skip": "dim yellow"
})
console = Console(theme=custom_theme)

def log(message, style=None):
    """Prints a message using rich, with a colored worker ID prefix."""
    prefix = f"[[{WORKER_COLOR}]Worker {WORKER_ID:>3}[/]]"
    console.print(f"{prefix} {message}", style=style, highlight=False)

# --- Generation Logic (Modified for logging and timing) ---
def generate():
    start_time = time.time()
    out_path = Path(args.out_path) / args.version
    os.makedirs(out_path, exist_ok=True)
    blocklist = ['rung1','rung2']

    tasks = [t for t in DATASETS.keys() if t.lower() not in blocklist]
    #tasks = [t for t in tasks if 'task' in t.lower()]
    if not tasks:
        sys.exit(0)

    files_per_task = args.num_examples // (args.batch_size * len(tasks))
    if files_per_task < 1:
        sys.exit(0)

    random.shuffle(tasks)
    for dataset_name in tasks:
        index = len(list(out_path.glob(f'{dataset_name}-*.jsonl')))
        if index < files_per_task:
            break
    else:
        sys.exit(0)

    log(f"START: {dataset_name}", style="start")
    d_out_path = out_path / f'{dataset_name}-{index}.jsonl'

    T = DATASETS[dataset_name]()
    T.timeout = 20
    level = random.choice(args.levels)
    examples = T.generate_balanced_batch(batch_size=args.batch_size, level=level)
    d_out_path.touch()

    duration = time.time() - start_time
    if examples:
        df = pd.DataFrame([x.to_dict() for x in examples])
        df['metadata'] = df['metadata'].map(json.dumps)
        df.to_json(d_out_path, lines=True, orient='records')
        log(f"DONE: {dataset_name} {index} (took {duration:.2f}s)", style="done")
    else:
        log(f"SKIP: No examples for {dataset_name} (took {duration:.2f}s)", style="skip")


if __name__ == '__main__':
    generate()
