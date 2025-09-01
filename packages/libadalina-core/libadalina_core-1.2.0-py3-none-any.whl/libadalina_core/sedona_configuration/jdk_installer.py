import logging
import os
import jdk

def install_jdk_if_needed():
    """
    Install a compatible JDK if `JAVA_HOME` environment variable is not found.
    """
    if 'JAVA_HOME' not in os.environ:
        version = '17'
        jre_path = os.path.join(jdk._JRE_DIR, version)

        if os.path.exists(jre_path):
            logging.info(f'JAVA_HOME not set but JRE already downloaded')
            os.environ['JAVA_HOME'] = jre_path
        else:
            logging.info('JAVA_HOME not set, installing JRE...')
            java_home = jdk.install(version, jre=True)
            os.environ['JAVA_HOME'] = java_home
            os.symlink(java_home, jre_path)

    logging.info(f'JAVA_HOME set to {os.environ.get("JAVA_HOME")}')