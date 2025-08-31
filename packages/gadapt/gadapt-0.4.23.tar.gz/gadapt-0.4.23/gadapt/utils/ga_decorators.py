class ExecuteUntilChanges:
    def __init__(self, current_value, number_of_attempts=5):
        self.current_value = current_value
        self.number_of_attempts = number_of_attempts

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            return self._execute_function_until_value_changed(func)

        return wrapper

    def _execute_function_until_value_changed(self, f):
        i = 0
        while True:
            new_function_return_value = f()
            i += 1
            if (
                new_function_return_value != self.current_value
                or i >= self.number_of_attempts
            ):
                break
        return new_function_return_value
