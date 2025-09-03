from sup.cli import run_source
from sup.parser import Parser
from sup.vm import run as vm_run


def test_vm_arith_and_print():
    code = """
sup
set x to add 2 and 3
print x
print the result
bye
""".strip()
    program = Parser().parse(code)
    out = vm_run(program)
    assert out.splitlines() == ["5.0", "5.0"]


def test_vm_control_flow():
    code = """
sup
set x to 0
repeat 3 times
set x to add x and 2
endrepeat
if x is greater than 5 then
print x
else
print "no"
end if
bye
""".strip()
    program = Parser().parse(code)
    out = vm_run(program)
    assert out.strip() == "6.0"


def test_vm_functions_and_calls():
    code = """
sup
define function called addtwo with a and b
  return add a and b
end function
print call addtwo with 4 and 5
bye
""".strip()
    program = Parser().parse(code)
    out = vm_run(program)
    assert out.strip() == "9.0"


def test_vm_builtins():
    code = """
sup
set word to "hi"
print upper of word
print power of 2 and 3
make list of 1, 2, 3
print join of "," and list
print contains of list and 2
bye
""".strip()
    program = Parser().parse(code)
    out = vm_run(program)
    lines = out.splitlines()
    assert lines[0] == "HI"
    assert lines[1] == "8.0"
    assert lines[2] == "1,2,3"
    assert lines[3] in {"True", "False"}


def test_vm_try_catch_throw():
    code = """
sup
try
  throw "boom"
catch e
  print e
end try
bye
""".strip()
    program = Parser().parse(code)
    out = vm_run(program)
    assert out.strip() == "boom"


def test_vm_ffi_files_env_json_regex_glob(tmp_path, monkeypatch):
    p = tmp_path / "f.txt"
    monkeypatch.setenv("FOO", "BAR")
    code = f"""
sup
print env get of "FOO"
print join path of "{tmp_path.as_posix()}" and "f.txt"
set _ to write file of "{(tmp_path/'f.txt').as_posix()}" and "hello"
print read file of "{(tmp_path/'f.txt').as_posix()}"
print json stringify of make list of 1, 2
print regex replace of "l" and "hello" and "L"
print glob of "{(tmp_path/'*.txt').as_posix()}"
bye
""".strip()
    program = Parser().parse(code)
    out = vm_run(program)
    lines = out.splitlines()
    assert lines[0] == "BAR"
    assert lines[1].endswith("f.txt")
    assert lines[2] == "hello"
    assert lines[3] == "[1, 2]"
    assert lines[4] == "heLLo"
    assert "f.txt" in lines[5]


