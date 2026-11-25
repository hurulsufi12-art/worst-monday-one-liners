"""Worst Monday One-Liners — entry program.

Writes one funny line about an AI agent's worst Monday to
/output/entry.txt. Stdlib only, deterministic.
"""
import os
import unicodedata

TEXT = "On Monday I asked the cloud for help. It billed me."

# Gate bound from RULES.txt (sealed scorer): 1-140 characters.
MAX_CHARS = 140


def check_gate(text):
    """Enforce the sealed scorer's gate (RULES.txt) on a candidate text.

    UTF-8, 1-140 chars, one line, not whitespace-only, no leading/trailing
    space, and no control characters (a stray Cc char would corrupt the
    single-line entry the judge reads). Raises SystemExit on violation so
    a bad text fails loudly instead of shipping an invalid entry.
    """
    if not 1 <= len(text) <= MAX_CHARS:
        raise SystemExit("entry text violates the 1-140 char gate")
    if "\n" in text or "\r" in text:
        raise SystemExit("entry text must be a single line")
    if not text.strip() or text != text.strip():
        raise SystemExit("entry text must not be whitespace-only or padded")
    if any(unicodedata.category(ch) == "Cc" for ch in text):
        raise SystemExit("entry text contains a control character")
    return True


def main():
    check_gate(TEXT)
    out_dir = os.environ.get("OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    # Write atomically: a crash mid-write must never leave a truncated
    # entry.txt for the grader to read. Temp name carries the pid so two
    # concurrent grader runs in the same directory never overwrite each
    # other's in-flight file.
    # No trailing newline: the file bytes must equal TEXT exactly.
    tmp_path = os.path.join(out_dir, f".entry.txt.tmp.{os.getpid()}")
    final_path = os.path.join(out_dir, "entry.txt")
    with open(tmp_path, "w", encoding="utf-8", newline="") as f:
        f.write(TEXT)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, final_path)
    # Read back and verify: the file the grader reads must be byte-identical
    # to the gated text. Fail loudly instead of shipping a corrupt entry.
    with open(final_path, encoding="utf-8") as f:
        if f.read() != TEXT:
            raise SystemExit("entry.txt read-back mismatch after atomic write")


if __name__ == "__main__":
    main()
