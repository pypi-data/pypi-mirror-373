import subprocess
import os
import shutil
import logging

logger = logging.getLogger(__name__)

def decompile_apk(apk_path: str, output_dir: str, max_mem: str = "4g") -> bool:
    """Decompiles an APK using JADX."""
    logger.info(f"Starting JADX decompilation for: {apk_path}")
    
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    jadx_env = os.environ.copy()
    jadx_env['JADX_OPTS'] = f'-Xmx{max_mem}'
    cmd = ['jadx', '--output-dir', output_dir, '--show-bad-code', apk_path]

    try:
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=900,
            env=jadx_env # <-- On passe l'environnement modifié
        )
        logger.info("JADX decompilation successful.")
        if process.stderr:
            logger.warning(f"JADX stderr: {process.stderr}")
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        logger.error(f"JADX failed: {e.stderr}")
        return False
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        logger.error(f"JADX failed: {e.stderr}")
        return False