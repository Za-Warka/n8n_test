"""Trustworthy regression suite: validate the numeric-only fixture before executing it."""
import ast
import pathlib
import unittest


def load_clamp():
    source = pathlib.Path(__file__).with_name('calculator.py').read_text()
    tree = ast.parse(source)
    nodes = tree.body[:]
    if nodes and isinstance(nodes[0], ast.Expr) and isinstance(nodes[0].value, ast.Constant) and isinstance(nodes[0].value.value, str):
        nodes.pop(0)
    if len(nodes) != 1 or not isinstance(nodes[0], ast.FunctionDef):
        raise AssertionError('Only the clamp function is permitted')
    fn = nodes[0]
    args = fn.args
    if (fn.name != 'clamp' or [a.arg for a in args.args] != ['value','lower','upper']
            or args.posonlyargs or args.kwonlyargs or args.vararg or args.kwarg
            or args.defaults or args.kw_defaults or fn.decorator_list or fn.returns
            or getattr(fn, 'type_params', []) or any(a.annotation for a in args.args)):
        raise AssertionError('Unexpected function signature')
    allowed = (ast.Module, ast.FunctionDef, ast.arguments, ast.arg, ast.Expr, ast.Constant,
               ast.Return, ast.If, ast.IfExp, ast.Name, ast.Load, ast.Compare,
               ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Eq, ast.NotEq,
               ast.Call, ast.BoolOp, ast.And, ast.Or, ast.UnaryOp, ast.Not, ast.USub, ast.UAdd)
    for n in ast.walk(tree):
        if not isinstance(n, allowed):
            raise AssertionError('Unexpected syntax: ' + type(n).__name__)
        if isinstance(n, ast.Name) and n.id not in {'value','lower','upper','min','max'}:
            raise AssertionError('Unexpected name: ' + n.id)
        if isinstance(n, ast.Call) and (not isinstance(n.func, ast.Name) or n.func.id not in {'min','max'} or n.keywords):
            raise AssertionError('Unexpected call')
        if isinstance(n, ast.Constant) and not isinstance(n.value, (int,float,str)):
            raise AssertionError('Unexpected constant')
    env = {'__builtins__': {'min': min, 'max': max}}
    exec(compile(tree, 'calculator.py', 'exec'), env)
    return env['clamp']


class ClampRegression(unittest.TestCase):
    def test_all_integer_ranges(self):
        clamp = load_clamp()
        for lower in range(-5, 6):
            for upper in range(lower, 6):
                for value in range(-10, 11):
                    with self.subTest(value=value, lower=lower, upper=upper):
                        self.assertEqual(clamp(value, lower, upper), min(max(value, lower), upper))

    def test_fractional_and_equal_bounds(self):
        clamp = load_clamp()
        for value, lo, hi, expected in [(1.7,0.,1.,1.),(-1.5,-1.,2.,-1.),(0.5,0.,1.,0.5),(9,3,3,3)]:
            self.assertEqual(clamp(value, lo, hi), expected)


if __name__ == '__main__':
    unittest.main()
