#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
from pathlib import Path


def refresh_shell_environment():
    """Refresh shell environment by sourcing profile files"""
    home = Path.home()
    shell_profiles = [home / ".bashrc", home / ".zshrc", home / ".profile"]

    for profile in shell_profiles:
        if profile.exists():
            try:
                result = subprocess.run(
                    f"source {profile} && echo $PATH",
                    shell=True,
                    capture_output=True,
                    text=True,
                    executable="/bin/bash",
                )
                if result.returncode == 0 and result.stdout.strip():
                    new_path = result.stdout.strip()
                    if new_path != os.environ.get("PATH", ""):
                        os.environ["PATH"] = new_path
                        print(f"Updated PATH from {profile}")
                        break
            except Exception as e:
                print(f"Failed to source {profile}: {e}")


def install_noirup():
    """Install noirup if not present"""
    if shutil.which("noirup"):
        print("noirup already installed")
        return True

    print("Installing noirup...")
    try:
        result = subprocess.run(
            [
                "curl",
                "-L",
                "https://raw.githubusercontent.com/noir-lang/noirup/main/install",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            print(f"Failed to download noirup installer: {result.stderr}")
            return False

        process = subprocess.Popen(
            ["bash"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate(input=result.stdout)

        if process.returncode != 0:
            print(f"Failed to install noirup: {stderr}")
            return False

        home = Path.home()
        noirup_bin = home / ".noirup" / "bin"
        if noirup_bin.exists():
            os.environ["PATH"] = f"{noirup_bin}:{os.environ['PATH']}"

        return True
    except Exception as e:
        print(f"Error installing noirup: {e}")
        return False


def install_nargo():
    """Install nargo using noirup"""
    if shutil.which("nargo"):
        print("nargo already installed")
        return True

    print("Installing nargo...")
    try:

        home = Path.home()
        noirup_cmd = str(home / ".nargo" / "bin" / "noirup")

        result = subprocess.run([noirup_cmd], capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error installing nargo: {e}")
        return False


def install_bbup():
    """Install bbup if not present"""
    if shutil.which("bbup"):
        print("bbup already installed")
        return True

    print("Installing bbup...")
    try:
        result = subprocess.run(
            [
                "curl",
                "-L",
                "https://raw.githubusercontent.com/AztecProtocol/aztec-packages/refs/heads/master/barretenberg/bbup/install",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            print(f"Failed to download bbup installer: {result.stderr}")
            return False

        process = subprocess.Popen(
            ["bash"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate(input=result.stdout)

        if process.returncode != 0:
            print(f"Failed to install bbup: {stderr}")
            return False

        home = Path.home()
        for bin_dir in [".bbup/bin", "bin", ".local/bin"]:
            bbup_bin = home / bin_dir
            if bbup_bin.exists():
                os.environ["PATH"] = f"{bbup_bin}:{os.environ['PATH']}"

        return True
    except Exception as e:
        print(f"Error installing bbup: {e}")
        return False


def install_bb():
    """Install bb using bbup"""
    if shutil.which("bb"):
        print("bb already installed")
        return True

    print("Installing bb...")
    try:

        home = Path.home()
        bbup_cmd = str(home / ".bb" / "bbup")

        if not Path(bbup_cmd).exists():
            print(f"bbup not found at {bbup_cmd}")
            return False

        result = subprocess.run(
            [bbup_cmd, "--version", "0.87.0"], capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"bbup failed: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Error installing bb: {e}")
        return False


def main():
    if os.environ.get("CI") or os.environ.get("POP_SKIP_INSTALL"):
        return

    success = True

    if not install_noirup():
        success = False
    else:
        refresh_shell_environment()
        if not install_nargo():
            success = False

    if not install_bbup():
        success = False
    else:
        refresh_shell_environment()
        if not install_bb():
            success = False

    if not success:
        print(
            "Some dependencies failed to install. You may need to install them manually."
        )
        print("See install.sh for manual installation steps.")
        sys.exit(1)


if __name__ == "__main__":
    main()
