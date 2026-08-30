# Hackathon Submission Checklist

## Security

- [ ] Revoke or rotate the credential previously committed in `.env.example`.
- [ ] Remove the exposed value from Git history with the repository owner.
- [ ] Confirm `.env.example` contains empty placeholders only.
- [ ] Run `python scripts/check_secrets.py`.
- [ ] Review the complete staged diff.

## Working prototype

- [ ] Run `streamlit run app.py` from a clean environment.
- [ ] Exercise all four demo scenarios.
- [ ] Run the complete test suite.
- [ ] Confirm evidence links, missing-data handling, and human review gates.
- [ ] Confirm the interface makes no scientific, legal, regulatory, or production claim.

## IBM Bob evidence

- [ ] Retain the real problem statement and baseline.
- [ ] Retain actual Bob plans and session exports.
- [ ] Identify which Bob capabilities were genuinely used.
- [ ] Preserve test and review evidence.
- [ ] Record real task timing, manual steps, interventions, failures, and rework.
- [ ] Remove every unmeasured productivity claim.

## Repository

- [ ] Replace the template README with the project README.
- [ ] Synchronize capability statuses with the code and tests.
- [ ] Confirm the default branch contains the submission state.
- [ ] Remove malformed placeholder files.
- [ ] Select a license or leave the repository explicitly unlicensed.
- [ ] Add final screenshots or video links without committing sensitive information.

## Final presentation

- [ ] Define the developer workflow problem in one sentence.
- [ ] Show why ARIA creates real engineering complexity.
- [ ] Demonstrate a complete ARIA workflow.
- [ ] Demonstrate Bob beyond simple code generation.
- [ ] Show observed before and after evidence.
- [ ] State current limitations clearly.
