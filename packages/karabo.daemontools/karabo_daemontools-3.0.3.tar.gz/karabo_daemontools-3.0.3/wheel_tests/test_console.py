import subprocess

# commands not covered, because they don't produce verifiable output: 
# - multilog
# - svscan
# - tai64n
# - tai64nlocal

def _run_cmd(cmd : str) -> str:
    # the output will end with a newline, which we remove
    return subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()[:-1]

def test_envdir():
    output =_run_cmd("envdir")
    assert output == "envdir: usage: envdir [ -p prefix ] dir child"


def test_envini():
    output =_run_cmd("envini")
    assert output == "envini: usage: envini [ -p prefix ] inifile child"


def test_envuidgid():
    output =_run_cmd("envuidgid")
    assert output == "envuidgid: usage: envuidgid account child"


def test_fghack():
    output =_run_cmd("fghack")
    assert output == "fghack: usage: fghack child"


def test_pgrphack():
    output =_run_cmd("pgrphack")
    assert output == "pgrphack: usage: pgrphack child"


def test_setlock():
    output =_run_cmd("setlock")
    assert output == "setlock: usage: setlock [ -nNxX ] file program [ arg ... ]"


def test_setuidgid():
    output =_run_cmd("setuidgid")
    assert output == "setuidgid: usage: setuidgid [-s] account child"


def test_setuser():
    output =_run_cmd("setuser")
    assert output == "setuser: usage: setuser account child"


def test_softlimit():
    output =_run_cmd("softlimit")
    assert output == "softlimit: usage: softlimit [-a allbytes] [-c corebytes] [-d databytes] [-f filebytes] [-l lockbytes] [-m membytes] [-o openfiles] [-p processes] [-r residentbytes] [-s stackbytes] [-t cpusecs] child"  # noqa


def test_supervise():
    output =_run_cmd("supervise")
    assert output == "supervise: usage: supervise dir"


def test_svstat():
    output =_run_cmd("svstat")
    assert output == "svstat: usage: svstat [-L] [-l] dir [dir ...]"


def test_svup():
    output =_run_cmd("svup")
    assert output == "svup: usage: svup [-L] [-l] dir"
