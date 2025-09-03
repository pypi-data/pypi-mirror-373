import re
import subprocess


EXPECTED_OUTPUT= r"^.*\[info\] karabo\.core\.Device : 'PropertyTest' \(version '.*'\) with deviceId: '.*' got started on server.*$"

def _run_cmd(cmd : str) -> str:
    
    try:
        subprocess.run(cmd, check=False, shell=True, stdout=subprocess.PIPE, timeout=10, stderr=subprocess.STDOUT)
    except subprocess.TimeoutExpired as err:
        # cleanup
        subprocess.run("killall -9 karabo-cppserver", shell=True)
        return err.stdout.decode()[:-1]
    return ""


def test_cppserver():
    output =_run_cmd("karabo-cppserver init='{\"PropertyTest\": {\"deviceId\": \"test\", \"classId\": \"PropertyTest\"}}'")
    assert re.findall(EXPECTED_OUTPUT, output, re.MULTILINE)
