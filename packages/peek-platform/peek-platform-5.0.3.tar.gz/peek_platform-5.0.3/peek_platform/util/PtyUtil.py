import logging
import shlex
import subprocess
from typing import Optional
from typing import Tuple

from twisted.internet import reactor
from twisted.internet import threads
from twisted.internet.defer import Deferred
from twisted.internet.defer import inlineCallbacks
from twisted.internet.protocol import ProcessProtocol
from vortex.DeferUtil import vortexLogFailure

logger = logging.getLogger(__name__)


class SpawnOsCommandException(subprocess.CalledProcessError):
    """Spawn OS Command Exception

    This exception is raised when an OS command fails or returns a non-zero exit code

    """

    def __init__(
        self,
        returncode: int,
        cmd: str,
        stdout: Optional[str] = None,
        stderr: Optional[str] = None,
        message: Optional[str] = None,
    ):
        """Constructor

        :param returncode: The code returned by the process.
        :param cmd: A string representing the command and args executed by bash.
        :param stdout: The output from the process.
        :param stderr: The error from the process.
        :param message: An additional message that can be used to emulate the message
        method of standard exceptions
        """

        subprocess.CalledProcessError.__init__(
            self, returncode, cmd, stdout, stderr
        )
        self.message = message

    def __str__(self):
        return "%s\nCommand '%s' returned non-zero exit status %d" % (
            self.message,
            self.cmd,
            self.returncode,
        )


def spawnSubprocessBlocking(
    cmdAndArgs: str,
    logger_: logging.Logger,
    cwd: Optional[str] = None,
    env: Optional[dict] = None,
    exceptionOnStderr: bool = True,
    exceptionOnNonZeroExitCode: bool = True,
    stderrLogLevel: int = logging.ERROR,
) -> Tuple[bytes, bytes, int]:
    return threads.blockingCallFromThread(
        reactor,
        spawnSubprocess,
        cmdAndArgs,
        logger_,
        cwd=cwd,
        env=env,
        exceptionOnStderr=exceptionOnStderr,
        exceptionOnNonZeroExitCode=exceptionOnNonZeroExitCode,
        stderrLogLevel=stderrLogLevel,
    )


@inlineCallbacks
def spawnSubprocess(
    cmdAndArgs: str,
    logger_: logging.Logger,
    cwd: Optional[str] = None,
    env: Optional[dict] = None,
    exceptionOnStderr: bool = True,
    exceptionOnNonZeroExitCode: bool = True,
    stderrLogLevel: int = logging.ERROR,
) -> Deferred:
    """Spawn Subprocess

    This method calls an OS command using the subprocess package and bash as the
    interpreter.

    :param cmdAndArgs: A string containing the command
        and arguments to pass to bash.
    :param logger_: The parser for the command output.
    :param env: os.environ to use for the command
    :param exceptionOnStderr: Should the deferred errback if there is stdout?

    :returns: None, This either succeeds or raises an exception.

    :raises: c{CalledProcessError}

    """
    assert isinstance(cmdAndArgs, str), "cmdAndArgs is not str"

    shellCmdAndArgs = """ bash -l -c "cd '%s' && %s" """ % (cwd, cmdAndArgs)
    args = shlex.split(shellCmdAndArgs)
    cmd = args[0]
    pp = ProcessOutLogger(
        shellCmdAndArgs,
        logger_,
        exceptionOnStderr,
        exceptionOnNonZeroExitCode,
        stderrLogLevel=stderrLogLevel,
    )
    # noinspection PyUnresolvedReferences
    logger_.debug("Running command '%s'", shellCmdAndArgs)
    reactor.spawnProcess(pp, cmd, args, env=env, path=cwd)

    pp.deferred.addErrback(vortexLogFailure, logger_, consumeError=False)
    return (yield pp.deferred)


class ProcessOutLogger(ProcessProtocol):
    def __init__(
        self,
        command: str,
        logger_: logging.Logger,
        exceptionOnStderr: bool,
        exceptionOnNonZeroExitCode: bool,
        stderrLogLevel: int,
    ):
        self._command = command
        self._logger = logger_
        self._exceptionOnStderr = exceptionOnStderr
        self._exceptionOnNonZeroExitCode = exceptionOnNonZeroExitCode
        self._stderrLogLevel = stderrLogLevel
        self.deferred = Deferred()
        self.stdout = b""
        self.stderr = b""

    def connectionMade(self):
        self._logger.debug("connectionMade, command=%s" % (self._command,))
        self.transport.closeStdin()

    def outReceived(self, data):
        self.stdout += data
        for line in data.splitlines():
            if not line.decode().strip():
                continue
            self._logger.debug(line.decode().strip())

    def errReceived(self, data):
        self.stderr += data
        for line in data.splitlines():
            if not line.decode().strip():
                continue
            self._logger.log(self._stderrLogLevel, line.decode().strip())

    def processEnded(self, reason):
        if self._exceptionOnStderr and self.stderr:
            self.deferred.errback(
                Exception(
                    "Command generated, exit code %s,"
                    " stderr: %s"
                    % (reason.value.exitCode, self.stderr.decode())
                )
            )

        elif self._exceptionOnNonZeroExitCode and reason.value.exitCode:
            self.deferred.errback(
                Exception(
                    "Command exited with non-zero exit code %s,"
                    " stderr: %s"
                    % (reason.value.exitCode, self.stderr.decode())
                )
            )

        else:
            self.deferred.callback(
                (self.stdout, self.stderr, reason.value.exitCode)
            )

        self._logger.debug(
            "processEnded, status %d, len(stdout) %s, len(stderr) %s, cmd: %s"
            % (
                reason.value.exitCode,
                len(self.stdout),
                len(self.stderr),
                self._command,
            )
        )
