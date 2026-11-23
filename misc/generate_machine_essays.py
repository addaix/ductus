"""Machine-written essays on learner-exam prompts: the recall set for the document threshold.

The human corpus (W&I+LOCNESS) says how often the instrument accuses people; it says
nothing about what a stricter document threshold costs in findings. This script writes
that other half: essays a model wrote for the same kinds of tasks the human corpus
answers (letters, essays, reviews, stories, reports), in two registers -- the model's
own, and imitating an intermediate learner.

It calls a model through ``aix`` (``claude-cli/<model>``: the Claude Code CLI on a
subscription, no API key). The output is synthetic, so it could be shared, but like the
human corpus it lives under ``~/.local/share/ductus/corpora/`` and only the numbers are
committed (``misc/docs/non-native-calibration.md``)::

    python misc/generate_machine_essays.py                  # haiku + sonnet, 2 registers
    python misc/generate_machine_essays.py --models haiku

Each line of the output JSONL is ``{"id", "model", "register", "prompt", "text"}``.
"""

from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

OUT = (
    Path.home()
    / ".local"
    / "share"
    / "ductus"
    / "corpora"
    / "synthetic-machine"
    / "essays.jsonl"
)

#: Learner-exam style tasks, of the genres W&I+LOCNESS answers.
PROMPTS = (
    "Write a letter to a friend telling them about a holiday you had recently.",
    "Write an essay: some people think children should learn to cook at school. Do you agree?",
    "Write a review of a restaurant you have visited for a local magazine.",
    "Write a story that begins: 'When I opened the door, I could not believe my eyes.'",
    "Write a report for your manager about how to make the office more environmentally friendly.",
    "Write an email to a hotel complaining about a problem during your stay.",
    "Write an essay: is it better to live in a city or in the countryside?",
    "Write an article for a school website about your favourite hobby.",
    "Write a letter applying for a summer job at a sports centre.",
    "Write an essay: should mobile phones be banned in schools?",
    "Write a review of a film you have seen recently.",
    "Write a story about a day when everything went wrong.",
    "Write an essay: the advantages and disadvantages of working from home.",
    "Write an email to your teacher explaining why you missed an important class.",
    "Write an article about the role of technology in learning languages.",
    "Write a report on the facilities for young people in your town.",
    "Write an essay: is tourism good for local communities?",
    "Write a letter to the editor of a newspaper about public transport in your city.",
    "Write a story about meeting someone famous by chance.",
    "Write an essay: should university education be free for everyone?",
    "Write a review of a book that changed the way you think.",
    "Write an email inviting a classmate to a party and explaining how to get there.",
    "Write an essay: do social media make people more lonely?",
    "Write an article describing a festival or celebration in your country.",
    "Write a report for a college on whether students need more sports facilities.",
)

REGISTERS = {
    "plain": "{prompt} Write about 250 words. Output only the text.",
    "learner": (
        "You are an intermediate (CEFR B1-B2) learner of English, writing for an exam. "
        "{prompt} Write about 250 words, as such a learner would. Output only the text."
    ),
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--models", nargs="+", default=["haiku", "sonnet"])
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    from aix import chat

    jobs = [
        (model, register, i, prompt)
        for model in args.models
        for register in REGISTERS
        for i, prompt in enumerate(PROMPTS)
    ]

    def write(job):
        model, register, i, prompt = job
        text = chat(
            REGISTERS[register].format(prompt=prompt), model=f"claude-cli/{model}"
        )
        return {
            "id": f"{model}-{register}-{i:02d}",
            "model": model,
            "register": register,
            "prompt": prompt,
            "text": str(text).strip(),
        }

    with ThreadPoolExecutor(args.workers) as pool:
        rows = list(pool.map(write, jobs))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    print(f"wrote {len(rows)} essays to {args.out}")


if __name__ == "__main__":
    main()
