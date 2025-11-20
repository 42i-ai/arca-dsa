# Arca DSA — Multi-language Streamlit Runner

This repository provides a lightweight containerized environment to run small Python, C, and Rust code snippets through a Streamlit web interface.

Features

- Run Python scripts
- Compile & run C programs using `gcc`
- Compile & run Rust programs using `rustc` (installed via rustup)

Quick start

1. Build and run with docker-compose:

   docker-compose up --build

2. Open http://localhost:8501 in your browser.

Notes & limitations

- This environment is designed for short-lived, small test runs and demos.
- There are timeouts to reduce risk of infinite loops, but this is not a sandbox — do not run untrusted code in production.
- If you need a stronger sandbox, consider adding user namespaces, resource limits, seccomp, or running inside a dedicated build container with restricted privileges.
