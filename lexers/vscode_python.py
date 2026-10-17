"""Python lexer that tells names apart the way VS Code does.

Pygments' PythonLexer emits every identifier as a plain Name. This subclass
re-tags them from their neighbours so each kind can get its own colour:
  name(          -> Name.Function   (functions and methods being called)
  Name(          -> Name.Class      (capitalised call: a class being built)
  name=  in (..) -> Name.Tag        (keyword argument)
  .name          -> Name.Attribute  (attribute that is not called)
  CamelCase      -> Name.Class      (class referenced without a call)
  ALL_CAPS       -> Name.Constant   (module-level constant, enum member)
"""

from pygments.lexers.python import PythonLexer
from pygments.token import Name, Operator, Punctuation, Text, Whitespace

OPENERS = {"(", "[", "{"}
CLOSERS = {")", "]", "}"}


def _is_space(ttype, value):
    return ttype in Text or ttype in Whitespace or value.isspace()


class VSCodePythonLexer(PythonLexer):
    name = "VSCodePython"

    def get_tokens_unprocessed(self, text):
        tokens = list(super().get_tokens_unprocessed(text))

        def neighbour(i, step):
            j = i + step
            while 0 <= j < len(tokens) and _is_space(tokens[j][1], tokens[j][2]):
                j += step
            return tokens[j] if 0 <= j < len(tokens) else (None, None, "")

        depth = 0
        for i, (pos, ttype, value) in enumerate(tokens):
            if ttype is Punctuation and value in OPENERS:
                depth += 1
            elif ttype is Punctuation and value in CLOSERS:
                depth = max(0, depth - 1)

            if ttype is Name:
                _, next_type, next_value = neighbour(i, 1)
                _, prev_type, prev_value = neighbour(i, -1)
                is_constant = len(value) > 1 and value.isupper()
                is_class = value[:1].isupper() and not is_constant
                if next_type is Punctuation and next_value == "(":
                    ttype = Name.Class if is_class else Name.Function
                elif depth > 0 and next_type is Operator and next_value == "=":
                    ttype = Name.Tag
                elif is_constant:
                    ttype = Name.Constant
                elif prev_type is Operator and prev_value == ".":
                    ttype = Name.Attribute
                elif is_class:
                    ttype = Name.Class
            yield pos, ttype, value


CustomLexer = VSCodePythonLexer
