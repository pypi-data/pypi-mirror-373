from typing import Callable, List, Optional, Union


class CheckResult:
    """
    Class to hold the results of a check.
    """

    def __init__(self, passed: bool, message: str, check: Optional["Check"] = None) -> None:
        self.passed = passed
        self.message = message
        self.check = check

    @property
    def symbol(self) -> str:
        return "✅" if self.passed else "❌"

    @property
    def prefix_info(self) -> str:
        """Override to insert a text before message in str and repr."""
        return ""

    @property
    def check_name(self) -> str:
        return self.check.name if self.check else "unknown"

    @property
    def check_description(self) -> str:
        return self.check.description if self.check else "unknown"

    @property
    def suffix_info(self) -> str:
        """Override to insert a text after message in str and repr."""
        return ""

    def __str__(self) -> str:
        return f"{self.symbol} - {self.check_name} - {self.prefix_info} {self.message} {self.suffix_info}"

    def __repr__(self) -> str:
        return f"{self.symbol} {self.__class__.__name__}(passed={self.passed}, check={self.check_name}, message= {self.prefix_info} {self.message} {self.suffix_info})"


class Check:
    """
    Base class for checks.
    """

    def __init__(
        self,
        name: str,
        area: str,
        description: str,
        method: Optional[Union[Callable[[], List[CheckResult]], Callable[[], CheckResult]]] = None,
        results: Optional[List[CheckResult]] = None,
    ) -> None:
        """Initiate a Check by either providing a method to execute or the result of an already executed check."""
        self.id = (area + "__" + name.lower().replace(" ", "_"),)
        self.name = name
        self.area = area
        self.description = description
        self.method = method
        self.executed = method is None
        self.results: List[CheckResult] = results if results else []

        for r in self.results:
            r.check = self

    def execute(self) -> None:
        """
        Execute the check and store the results.
        If check is marked as executed, executionis skipped.
        :return: None
        """
        if self.executed:
            print(f"Check already executed, skipping: {self.name}")
            return
        try:
            print(f"Executing check: {self.name}")
            if self.method is not None:
                results = self.method()
            self.add_results(results)

        except Exception as e:
            self.add_results(ExceptionCheckResult(f"Check '{self.name}' raised an exception.", e))
        finally:
            self.executed = True

    def add_results(self, results: Union[List[CheckResult], CheckResult]) -> None:
        if isinstance(results, list):
            self.results.extend(results)
        else:
            self.results.append(results)
        for r in self.results:
            r.check = self

    @property
    def passed(self) -> bool:
        """
        Check if all results passed.
        :return: True if all results passed, False otherwise.
        """
        if not self.executed:
            raise RuntimeError("Check has not been executed yet. Call execute() first.")
        return all(result.passed for result in self.results)

    @property
    def symbol(self) -> str:
        """
        Get the symbol representing the check result.
        :return: "✔" if passed, "✘" if failed.
        """
        if len(self.results) == 1:
            return self.results[0].symbol
        return "✅" if self.passed else "❌"

    def __str__(self) -> str:
        return f"{self.name}: {self.description}"


class PluginCheckResult(CheckResult):
    """
    The result of a check on a plugin.
    """

    def __init__(self, passed: bool, message: str, plugin_name: str) -> None:
        super().__init__(passed, message)
        self.plugin_name = plugin_name

    @property
    def prefix_info(self) -> str:
        return f"Plugin: {self.plugin_name}"


class AllGoodCheckResult(CheckResult):
    """
    Placeholder result for a check where no problems were found and thus would have no results.
    """

    def __init__(self, message: str) -> None:
        super().__init__(True, "All good, " + message)


class ExceptionCheckResult(CheckResult):
    """
    Result for a check that raised an exception.
    """

    def __init__(self, message: str, exception: Exception) -> None:
        super().__init__(False, message)
        self.exception = exception

    @property
    def symbol(self) -> str:
        return "❗️"

    def __str__(self) -> str:
        return f"{self.symbol} Exception: {self.message} - {str(self.exception)}"

    def __repr__(self) -> str:
        return f"ExceptionCheckResult(passed={self.passed}, message={self.message}, exception={str(self.exception)})"


class MisconfiguredCheckResult(PluginCheckResult):
    """
    Result for a check that has a bug in config or return values.
    """

    def __init__(self, message: str, plugin_name: Optional[str] = None) -> None:
        super().__init__(True, "Config Error: " + message, plugin_name=plugin_name or "Unknown Plugin")

    @property
    def symbol(self) -> str:
        return "❗️"


class CheckList:
    """
    Class to hold a list of checks.
    """

    def __init__(self, area: str) -> None:
        self.area = area
        self.checks: List[Check] = []

    def add(
        self, name: str, description: str, method: Union[Callable[[], List[CheckResult]], Callable[[], CheckResult]]
    ) -> None:
        """
        Add a check to the list.
        """
        self.checks.append(Check(area=self.area, name=name, description=description, method=method))

    def execute(self) -> None:
        """
        Execute all checks in the list.
        :return: List[CheckResult]
        """
        for check in self.checks:
            check.execute()

    @property
    def results(self) -> List[CheckResult]:
        """
        Get the results of all checks in the list.
        :return: List[CheckResult]
        """
        return [result for check in self.checks for result in check.results]
