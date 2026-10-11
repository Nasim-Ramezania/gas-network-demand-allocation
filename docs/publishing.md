# Publishing this project

1. Connect the GitHub account that should own the repository.
2. Create a repository named `gas-network-demand-allocation`. Use public visibility when reviewers should access it without an invitation.
3. Add the reviewed project files at the repository root. `README.md`, `pyproject.toml`, `src/`, `tests/`, `data/example/`, `docs/`, and `.github/` should be at the top level, rather than inside a second project folder.
4. Check that only the synthetic example is included. Do not upload the private-data execution archive or local input/output folders.
5. Push the initial source commit to the default branch.
6. Check the Actions run. Local Linux tests have passed; only a completed Windows job verifies Windows in CI.
7. Open the public repository link without an authenticated session to check reviewer access.
8. Use that repository URL in the application. Describe the project as GIS demand allocation and validation; do not claim hydraulic simulation or spatial optimization.

Select a software license deliberately if you want to grant reuse rights. This package does not choose a license on the owner's behalf.
