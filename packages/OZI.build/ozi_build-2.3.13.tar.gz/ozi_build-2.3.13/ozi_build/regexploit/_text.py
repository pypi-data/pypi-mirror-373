POLYNOMIAL_DEGREES = [
    "linear",
    "quadratic",
    "cubic",
    "quartic",
    "quintic",
    "sextic",
    "septic",
    "octic",
    "nonic",
    "decic",
]


class TextOutput:
    def __init__(self, js_flavour: bool = False):
        self.first_for_regex = True
        self.regexes = 0
        self.js_flavour = js_flavour

    def next(self):
        """Next regex being processed."""
        self.first_for_regex = True
        self.regexes += 1

    def record(self, redos, pattern, *, filename=None, lineno=None, context=None):
        if self.first_for_regex:
            if filename:
                if lineno is not None:
                    print("Vulnerable regex in {} #{}".format(filename, lineno))
                else:
                    print("Vulnerable regex in {}".format(filename))
            print("Pattern: {}".format(pattern))
            if context:
                print("Context: {}".format(context))
            print("---")
            self.first_for_regex = False
        print(redos)
        stars = "\u2605" * min(10, redos.starriness)
        degree = (
            "exponential"
            if redos.starriness > 10
            else POLYNOMIAL_DEGREES[redos.starriness - 1] if redos.starriness > 0 else "?"
        )
        print("Worst-case complexity: {} {} ({})".format(redos.starriness, stars, degree))
        print("Repeated character: {}".format(redos.repeated_character))
        if redos.killer:
            print("Final character to cause backtracking: {}".format(redos.killer))
        print("Example: {}\n".format(redos.example(self.js_flavour)))
