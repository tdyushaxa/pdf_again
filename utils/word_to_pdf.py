import re
import subprocess
import sys

async def convert_to(folder, source, timeout=None):
    args = [libreoffice_exec(), '--headless', '--convert-to', 'pdf', '--outdir', folder, source]

    try:
        process = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        output = process.stdout.decode()
        filename_match = re.search('-> (.*?) using filter', output)

        if filename_match:
            filename = filename_match.group(1)
            return filename
        else:
            print("Regex pattern did not match in LibreOffice output")
            return None

    except subprocess.TimeoutExpired:
        print("Conversion process timed out")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def libreoffice_exec():
    if sys.platform == 'darwin':
        return '/Applications/LibreOffice.app/Contents/MacOS/soffice'
    return 'libreoffice'
