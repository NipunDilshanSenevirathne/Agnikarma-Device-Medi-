# Upload to GitHub

This task prepares files; it does not publish them or create a remote repository. Review licensing and claims before making it public.

## Git workflow
From this folder, if it is not yet a local repository:
```sh
git init -b main
git add .
git commit -m "Add Agni portable prototype source and engineering records"
```
Use your own configured Git identity. Create an empty repository in your GitHub account, then follow its supplied remote/push commands. No remote URL is invented here. Alternatively upload extracted files through GitHub, preserving hidden `.github/` files and folder structure. A ZIP alone will not show the README or run CI.

## Before upload
- Run `python tools/verify.py` (63 tests plus checks/deployment/simulation) and review docs/delivery-status.md.
- Preserve the local KiCad libraries and their tables, native check records, candidate Gerber/drill folder and mechanical exports. The source hashes in the records must match the delivered files. A later CAD edit requires rerunning its native checks.
- Upload the current project files, not old release ZIPs or local backups. Release archives are kept separately from this project folder.
- Keep output in `build/` and secrets out of Git. The example provisioning file is intentionally disabled.
- Decide a software/hardware/document license; public visibility is not a license. No grant is assumed here.
- Keep concept render captions and unfinished-hardware status visible. Do not add medical approval or manufacturing-ready badges.
- Use the issue templates for actual measured faults; do not include patient data.
