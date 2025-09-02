# -*- coding: utf-8 -*-
from mathics.core.atoms import String
from mathics.core.builtin import Builtin
from mathics.core.evaluation import Evaluation


class Hello(Builtin):
    """
    <dl>
      <dt>'Hello'[]
      <dt>'Hello'[$person$]
      <dd>An example function in a Python-importable Mathics3 module.
    </dl>

    >> Hello["everyone"]
    = "Hello, everyone!"

    See also the <url>
    :developer guide section:
    https://mathics-development-guide.readthedocs.io/en/latest/extending/developing-code/extending/tutorial/1-builtin.html</url> for an \
    explanation of everything.

    >> Hello[]
     = Hello, World!

    >> Hello["rocky"]
     = Hello, rocky!
    """

    # Set checking that the number of arguments required is zero or one.
    # eval_error = Builtin.generic_argument_error
    # expected_args = (0, 1)

    summary_text = """classic "hello" demo"""

    # The function below should start with "apply"
    def eval(self, evaluation: Evaluation):
        "Hello[]"
        return String("Hello, World!")

    # The function below should start with "eval"
    def eval_with_name(self, person, evaluation: Evaluation) -> String:
        "Hello[person_]"
        # The above pattern matches Hello with a argument.
        # See https://reference.wolfram.com/language/tutorial/Patterns.html#7301
        # and https://reference.wolfram.com/language/ref/Cases.html

        # Check that "person" is a String.
        if not isinstance(person, String):
            evaluation.message("Hello", "string")
            return

        return String(f"Hello, {person.value}!")
