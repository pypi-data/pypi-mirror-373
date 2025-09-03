import os
import json
import platform
import shutil
import subprocess
from typing import Optional, Tuple

try:
    import imageio_ffmpeg
except Exception:  # pragma: no cover
    imageio_ffmpeg = None


def which_ffmpeg() -> Optional[str]:
    """
    Args:
        None

    Returns:
        result: Path to ffmpeg executable if found, else None
    """
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    # try imageio-ffmpeg provided binary
    if imageio_ffmpeg is not None:
        try:
            exe = imageio_ffmpeg.get_ffmpeg_exe()
            if exe and os.path.exists(exe):
                return exe
        except Exception:
            pass
    return None


def ffmpeg_version(ffmpeg_path: str) -> str:
    """
    Args:
        ffmpeg_path: path to ffmpeg executable

    Returns:
        result: version string from `ffmpeg -version`
    """
    try:
        out = subprocess.check_output([ffmpeg_path, "-version"], stderr=subprocess.STDOUT)
        return out.decode(errors="ignore").splitlines()[0]
    except Exception as e:
        return f"unknown ({e})"


def install_ffmpeg() -> Tuple[bool, Optional[str], str]:
    """
    Try to install or fetch an ffmpeg executable.

    Strategy:
    1) Try imageio-ffmpeg bundled binary (if available)
    2) Try system package managers (macOS: brew; Debian/Ubuntu: apt; Fedora: dnf; Arch: pacman; Windows: choco/scoop if present)

    Returns:
        result: (success, ffmpeg_path, message)
    """
    # First, try to get imageio-ffmpeg provided binary
    if imageio_ffmpeg is not None:
        try:
            exe = imageio_ffmpeg.get_ffmpeg_exe()
            if exe and os.path.exists(exe):
                return True, exe, "Found ffmpeg via imageio-ffmpeg"
        except Exception as e:
            last_err = str(e)
        else:
            last_err = "Unknown error"
    else:
        last_err = "imageio-ffmpeg not installed"

    system = platform.system().lower()

    def run_install(cmd):
        try:
            subprocess.check_call(cmd, shell=True)
            return True, None
        except Exception as e:
            return False, str(e)

    # Attempt OS-specific installer
    if system == "darwin":
        if shutil.which("brew"):
            ok, err = run_install("brew install ffmpeg")
            if ok:
                exe = shutil.which("ffmpeg")
                if exe:
                    return True, exe, "Installed ffmpeg via Homebrew"
    elif system == "linux":
        # Try common managers
        managers = [
            ("apt-get", "sudo apt-get update && sudo apt-get install -y ffmpeg"),
            ("dnf", "sudo dnf install -y ffmpeg"),
            ("yum", "sudo yum install -y ffmpeg"),
            ("pacman", "sudo pacman -S --noconfirm ffmpeg"),
            ("zypper", "sudo zypper install -y ffmpeg"),
        ]
        for bin_name, cmd in managers:
            if shutil.which(bin_name):
                ok, err = run_install(cmd)
                if ok:
                    exe = shutil.which("ffmpeg")
                    if exe:
                        return True, exe, f"Installed ffmpeg via {bin_name}"
    elif system == "windows":
        # Try chocolatey or scoop if available
        if shutil.which("choco"):
            ok, err = run_install("choco install -y ffmpeg")
            if ok:
                exe = shutil.which("ffmpeg")
                if exe:
                    return True, exe, "Installed ffmpeg via Chocolatey"
        if shutil.which("scoop"):
            ok, err = run_install("scoop install ffmpeg")
            if ok:
                exe = shutil.which("ffmpeg")
                if exe:
                    return True, exe, "Installed ffmpeg via Scoop"

    # Fallback: give guidance
    return False, None, f"Failed to auto-install ffmpeg. Last error: {last_err}"


def check_ffmpeg() -> str:
    """
    Args:
        None

    Returns:
        result: JSON string with fields: installed (bool), path (str|None), message (str)
    """
    path = which_ffmpeg()
    if path:
        return json.dumps({
            "installed": True,
            "path": path,
            "message": f"ffmpeg already available: {ffmpeg_version(path)}",
        })

    ok, exe, msg = install_ffmpeg()
    if ok and exe:
        return json.dumps({
            "installed": True,
            "path": exe,
            "message": msg,
        })
    else:
        return json.dumps({
            "installed": False,
            "path": None,
            "message": msg,
        })
