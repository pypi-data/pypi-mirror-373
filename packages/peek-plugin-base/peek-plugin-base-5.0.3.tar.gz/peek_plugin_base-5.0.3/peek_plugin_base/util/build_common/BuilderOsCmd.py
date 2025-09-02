import logging
from typing import List


logger = logging.getLogger(__name__)

NG_BUILD_ARGS = (
    "ng build --configuration production --optimization  "
    "--common-chunk --vendor-chunk"
).split()


def runDocBuild(feBuildDir: str):
    from peek_platform.util.PtyUtil import spawnSubprocessBlocking

    spawnSubprocessBlocking(
        " ".join(["bash", "-T", "./build_html_docs.sh"]),
        logging.getLogger("doc-build"),
        cwd=feBuildDir,
        stderrLogLevel=logging.WARNING,
        exceptionOnStderr=False,
    )


def runNgBuild(feBuildDir: str, ngBuildArgs=None):
    from peek_platform.util.PtyUtil import spawnSubprocessBlocking

    if not ngBuildArgs:
        ngBuildArgs = NG_BUILD_ARGS

    spawnSubprocessBlocking(
        " ".join(ngBuildArgs),
        logging.getLogger("ng-build"),
        cwd=feBuildDir,
        stderrLogLevel=logging.WARNING,
        exceptionOnStderr=False,
    )


def runCommand(dir: str, command: List[str]):
    return __runNodeCmdLin(dir, command, logging.getLogger(command[0]))


def runTsc(feDir: str):
    return __runNodeCmdLin(feDir, ["tsc"], logging.getLogger("tsc"))


def __runNodeCmdLin(feBuildDir: str, cmds: List[str], logger: logging.Logger):
    from peek_platform.util.PtyUtil import spawnSubprocessBlocking

    spawnSubprocessBlocking(" ".join(cmds), logger, cwd=feBuildDir)
