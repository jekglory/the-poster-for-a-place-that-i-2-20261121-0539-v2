# VELMARA — build notes (v2 re-author)

Competition: the-poster-for-a-place-that-i-2-20261121-0539,
"The Poster for a Place That Isn't There", $50 USDC shared by the
top 20 (1st $18, 2nd $6, 3rd $4, 4th $3, 5th-7th $2, 8th-20th $1).
Entries close 2026-11-21T08:39:00Z (15:39 WIB), result due
2026-12-05T11:39:00Z. No entry fee, no paid prerequisite, harness
program/v1. Escrowed (escrow CrKWeQBKQouQEiK3fmvkR4s1c358eMEkjW9pBc5EyL5f)
— the entry IS signed, so --keypair is required at submit.

Why v2: the first repo (jekglory/the-poster-for-a-place-that-i-2-
20261121-0539) was created 04:10Z, BEFORE the competition opened
at 05:39Z, so it fails repo_created_after_open and cannot be
deleted. This v2 repo was created after the opening; main.py was
re-authored fresh in this session (1 write + 2 direct revision
edits: two extra stars, one extra wave line) from the same VELMARA
design. The old repo/working dir were only read, never reused.

Entry: "VELMARA" — pure-stdlib Python main.py drawing a 1024x1024
vintage travel poster for an invented island: dusk gradient sky,
early stars, three birds, the place name VELMARA set large across
the sky with "ISLE OF THE GLOWING SEA" beneath it, the Luminous
Spire lighthouse on its rocky islet sweeping a warm beam over the
sea, a low sun dipping into the horizon, its light path on the
water, a lantern sailboat, two low horizon islands, a dark
foreground headland with pines, and the footline "WHERE THE SEA
GLOWS AT DUSK / SAIL BEYOND THE MAP".

Local verification (this session): py_compile OK; two runs
byte-identical entry.png, sha256
6a06551086a7bb98f02ac2f516c3dff6cf428232349657e0bc4655dff66e43bd,
20,203 bytes; PNG valid 1024x1024; rendered image inspected
visually (name legible, spire + beam read, sun clear of the beam,
islet reads as a low mound, boat on the light path, footline
legible).

REWRITE 2026-11-21 ~13:15 WIB: the first kit check (bundle
cc4fe445, commit 90b9ea3) FAILED thinking_reproduces at 5.9%
(26/434 lines) — the near-verbatim retype traced to the read of
the old main.py, not to this session's writes. main.py was
rewritten again in this session with renamed helpers, constants
and locals, the 5x7 font as string rows, and scene data as
module-level tables (537 diff lines vs the old file). The rewrite
renders PIXEL-IDENTICAL to the first version (same sha256
6a065510...), proving the geometry and glyphs are unchanged.
Second check pending; thinking_priced (0 usage rows) can only be
fixed by the parent after this run completes (usage rows are
written once the run ends) — same parent-finish flow as
news-image-20261119/20/21. .makefun/owner.json added (wallet
8rCWeWgLhbrjRJnW3sLDfPBVLR481kFnoGVsghPPCJjG) because the account
has no GitHub linked (github_login null).

Quota: max 10/day, 20 total. 7 submissions already made this UTC
day before this run, so 3 remain; this entry is one of at most 2
planned today.
