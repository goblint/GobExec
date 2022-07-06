import re
from dataclasses import dataclass


@dataclass
class RaceSummary:
    safe: int
    vulnerable: int
    unsafe: int
    # total: int

    def template(self, env):
        return env.get_template("racesummary.jinja")

    @staticmethod
    def extract(stdout) -> 'RaceSummary':
        stdout = stdout.decode("utf-8")
        safe = int(re.search(r"safe:\s+(\d+)", stdout).group(1))
        vulnerable = int(re.search(r"vulnerable:\s+(\d+)", stdout).group(1))
        unsafe = int(re.search(r"unsafe:\s+(\d+)", stdout).group(1))
        return RaceSummary(safe, vulnerable, unsafe)


@dataclass
class AssertSummary:
    success: int
    warning: int
    error: int
    # total: int

    def template(self, env):
        return env.get_template("assertsummary.jinja")

    @staticmethod
    def extract(stdout) -> 'AssertSummary':
        stdout = stdout.decode("utf-8")
        success = len(re.findall(r"\[Success]\[Assert]", stdout))
        warning = len(re.findall(r"\[Warning]\[Assert]", stdout))
        error = len(re.findall(r"\[Error]\[Assert]", stdout))
        return AssertSummary(success, warning, error)

