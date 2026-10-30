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
- Run `python tools/verify.py` (64 tests plus checks/deployment/simulation) and review docs/delivery-status.md.
- Preserve the local KiCad libraries and their tables, native check records, candidate Gerber/drill folder and mechanical exports. The source hashes in the records must match the delivered files. A later CAD edit requires rerunning its native checks.
- Upload the current project files, not old release ZIPs or local backups. Release archives are kept separately from this project folder.
- Keep output in `build/` and secrets out of Git. The example provisioning file is intentionally disabled.
- Decide a software/hardware/document license; public visibility is not a license. No grant is assumed here.
- Keep concept render captions and unfinished-hardware status visible. Do not add medical approval or manufacturing-ready badges.
- Use the issue templates for actual measured faults; do not include patient data.

## Diagnose a red Actions check

1. Open the repository's **Actions** tab, select the latest **Source checks** run, and open a failed matrix job.
2. Expand **Verify source**. The `FAILED (exit ...): python ...` line identifies the failed command; the following output contains its assertion or traceback. The verifier stops at its first failing command and returns a nonzero status.
3. Download that job's `host-checks-<OS>-python-<version>` artifact from the run summary. It contains the complete `host-checks.txt` and structured `verification.json` from that run, even if verification failed. Artifacts are retained for seven days.
4. Fix the stated error, rerun `python tools/verify.py`, then commit and push the fix. In GitHub Desktop, review **Changes**, enter a summary, choose **Commit to main**, then **Push origin**. Confirm the checks on the new commit; an older failed commit may retain its red status.

The workflow runs all matrix jobs independently and uses Node.js 24 actions. A deprecation warning is distinct from a Python command's nonzero exit code. A local pass does not establish a GitHub runner pass. Host checks do not establish physical or medical-device validation.
