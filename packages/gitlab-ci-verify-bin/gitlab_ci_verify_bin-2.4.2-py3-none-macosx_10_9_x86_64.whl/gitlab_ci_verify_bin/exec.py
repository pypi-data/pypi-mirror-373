from dataclasses import dataclass
import subprocess
import os
from string import Template


@dataclass(frozen=True)
class ExecWithPrefixedOutputResult:
    exit_code: int
    stderr_buffer: str | None
    stdout_buffer: str | None


def create_subprocess(args: list[str], stdout: int, stderr: int, stdin: int | None = None, cwd=None, env=None) -> subprocess.Popen:
    """
    Create subprocess for gitlab-ci-verify with the specified arguments

    :param args: Arguments to pass to gitlab-ci-verify
    :param stdout: Stdout channel
    :param stderr: Stderr channel
    :param cwd: PWD for subprocess
    :param env: Environment variables for subprocess
    """
    return subprocess.Popen([os.path.join(os.path.dirname(__file__), "gitlab-ci-verify"), *args], stdout=stdout, stderr=stderr, stdin=stdin, cwd=cwd, text=True)


def exec_silently(args: list[str], timeout: int = -1, cwd=None) -> subprocess.Popen:
    """
    Execute gitlab-ci-verify silently with given arguments

    :param args: Arguments to pass to gitlab-ci-verify
    :param timeout: Timeout in ms
    :param cwd: PWD for subprocess
    :return: Completed Popen object
    """
    process = create_subprocess(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=cwd)
    if timeout > 0:
        process.wait(timeout)
    else:
        process.wait()
    return process


def exec_with_templated_output(args: list[str],
                              capture_output: bool = False,
                              stdout_format: str = "[STDOUT] $line",
                              stderr_format: str = "[STDERR] $line",
                              cwd=None) -> ExecWithPrefixedOutputResult:
    """
    Run gitlab-ci-verify using the specified args with templated stdout and stderr.


    This utility is especially helpful when you want to use the python package as wrapper around a tool that runs
    e.g. as part of a utility, where you provide the output for debug purposes etc. and want to mark clearly what it is about.


    To customize the format of the stdout and stderr, customize the *_format parameters.

    Following variables are available:
        - *$line*: Captured output line with removed trailing linebreak or whitespace
    :param args: Arguments to pass to gitlab-ci-verify
    :param capture_output: Capture the output in the result instead of printing it to stdout
    :param stdout_format: Format string for the stdout
    :param stderr_format: Format string for the stderr.
    :param cwd: PWD for subprocess
    :return:
    """

    stderr_buffer = ""
    stdout_buffer = ""

    process = create_subprocess(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)

    stdout_template = Template(stdout_format)
    stderr_template = Template(stderr_format)

    while True:
        output_stdout = process.stdout.readline()
        output_stderr = process.stderr.readline()

        if output_stdout == '' and output_stderr == '' and process.poll() is not None:
            break

        if output_stdout:
            stdout_buffer_line = stdout_template.safe_substitute(line=output_stdout.rstrip())
            if capture_output:
                stdout_buffer += stdout_buffer_line + "\n"
            else:
                print(stdout_buffer_line)

        if output_stderr:
            stderr_buffer_line = stderr_template.safe_substitute(line=output_stderr.rstrip())
            if capture_output:
                stderr_buffer += stderr_buffer_line + "\n"
            else:
                print(stderr_buffer_line)

    process.wait()

    return ExecWithPrefixedOutputResult(
        exit_code=process.returncode,
        stdout_buffer=stdout_buffer if stdout_buffer != "" else None,
        stderr_buffer=stderr_buffer if stderr_buffer != "" else None,
    )

