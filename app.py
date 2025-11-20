import streamlit as st
import subprocess
import tempfile
from pathlib import Path
import shutil
import os


st.set_page_config(
    page_title="Arca DSA — Multi-language Runner", layout="wide")

st.title("Arca DSA — Run Python, C, and Rust snippets")

st.markdown("Use this interface to edit and run small code snippets in Python, C, or Rust. Compiles and runs inside the container.")

LANG = st.selectbox("Language", ["Python", "C", "Rust"])

default_samples = {
    "Python": "print('Hello from Python')\nfor i in range(3):\n    print('line', i)",
    "C": "#include <stdio.h>\nint main(){ printf(\"Hello from C\\n\"); return 0; }",
    "Rust": "fn main(){ println!(\"Hello from Rust\"); }",
}

code = st.text_area("Source code", value=default_samples[LANG], height=300)
args = st.text_input("Program arguments (space-separated)")
timeout = st.number_input(
    "Timeout (seconds)", min_value=1, max_value=30, value=5)

run_btn = st.button("Run")


def _safe_run(cmd, cwd, timeout_sec):
    try:
        proc = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, text=True, timeout=timeout_sec)
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as e:
        return -1, e.stdout or "", (e.stderr or "") + "\n[Timed out]"
    except Exception as e:
        return -2, "", str(e)


if run_btn:
    with st.spinner("Running..."):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            if LANG == "Python":
                src = td_path / "script.py"
                src.write_text(code)
                cmd = ["python3", str(src)] + \
                    (args.split() if args.strip() else [])
                rc, out, err = _safe_run(cmd, cwd=td, timeout_sec=timeout)

                st.subheader("Result")
                st.write(f"Exit code: {rc}")
                st.write("Stdout:")
                st.code(out if out else "<no output>")
                if err:
                    st.write("Stderr:")
                    st.code(err)

            elif LANG == "C":
                src = td_path / "main.c"
                src.write_text(code)
                exe = td_path / "main"
                # Compile
                compile_cmd = ["gcc", str(src), "-O2", "-o", str(exe)]
                crc, cout, cerr = _safe_run(
                    compile_cmd, cwd=td, timeout_sec=10)
                st.subheader("Compilation")
                st.write(f"Exit code: {crc}")
                if cout:
                    st.write("Compiler stdout:")
                    st.code(cout)
                if cerr:
                    st.write("Compiler stderr:")
                    st.code(cerr)

                if crc == 0:
                    cmd = [str(exe)] + (args.split() if args.strip() else [])
                    rc, out, err = _safe_run(cmd, cwd=td, timeout_sec=timeout)
                    st.subheader("Run")
                    st.write(f"Exit code: {rc}")
                    st.write("Stdout:")
                    st.code(out if out else "<no output>")
                    if err:
                        st.write("Stderr:")
                        st.code(err)

            elif LANG == "Rust":
                src = td_path / "main.rs"
                src.write_text(code)
                exe = td_path / "main"
                # Compile with rustc
                compile_cmd = ["rustc", str(src), "-O", "-o", str(exe)]
                crc, cout, cerr = _safe_run(
                    compile_cmd, cwd=td, timeout_sec=15)
                st.subheader("Compilation")
                st.write(f"Exit code: {crc}")
                if cout:
                    st.write("Compiler stdout:")
                    st.code(cout)
                if cerr:
                    st.write("Compiler stderr:")
                    st.code(cerr)

                if crc == 0:
                    cmd = [str(exe)] + (args.split() if args.strip() else [])
                    rc, out, err = _safe_run(cmd, cwd=td, timeout_sec=timeout)
                    st.subheader("Run")
                    st.write(f"Exit code: {rc}")
                    st.write("Stdout:")
                    st.code(out if out else "<no output>")
                    if err:
                        st.write("Stderr:")
                        st.code(err)

            else:
                st.error("Unsupported language")

    # quick cleanup note
    st.info("Temporary build files are removed after execution. This environment allows small, short-lived runs; use caution with untrusted code.")
