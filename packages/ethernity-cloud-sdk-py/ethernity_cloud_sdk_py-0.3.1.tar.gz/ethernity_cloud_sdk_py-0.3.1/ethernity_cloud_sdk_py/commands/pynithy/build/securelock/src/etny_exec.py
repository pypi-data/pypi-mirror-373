import os.path
import ast

try:
    import serverless.backend as backend
except ImportError:
    backend = None
    pass

sdkFunctions = {}
if backend is not None:
    for func in backend.__dict__.keys():
        if func not in backend.__builtins__.keys() and func not in [
            "__file__",
            "__cached__",
            "__builtins__",
        ]:
            sdkFunctions.update({func: backend.__dict__[func]})


def ___etny_result___(data):
    quit([0, data])


class TaskStatus:
    SUCCESS = 0
    SYSTEM_ERROR = 1
    KEY_ERROR = 2
    SYNTAX_WARNING = 3
    BASE_EXCEPTION = 4
    PAYLOAD_NOT_DEFINED = 5
    PAYLOAD_CHECKSUM_ERROR = 6
    INPUT_CHECKSUM_ERROR = 7
    EXECVE = 8

def execute_task_v3(payload_data, input_data, extra_globals=None):
    base_globals = {"___etny_result___": ___etny_result___, **sdkFunctions}
    if extra_globals:
        base_globals.update(extra_globals)
    return Exec(payload_data, input_data, globals=base_globals)

def Exec(payload_data, input_data, globals=None, locals=None):
    try:
        if globals is None:
            globals = {}
        if locals is None:
            locals = globals

        print("Globals keys:", list(globals.keys()))
        print("Locals keys:", list(locals.keys()))
        print("execve in globals:", "execve" in globals)
        print("execve in locals:", "execve" in locals)

        if payload_data is not None:
            if input_data is not None:
                globals["___etny_data_set___"] = input_data
            module = ast.parse(payload_data)
            outputs = []
            for node in module.body:
                if isinstance(node, ast.Expr):
                    expr_code = compile(
                        ast.Expression(node.value), filename="<ast>", mode="eval"
                    )
                    result = eval(expr_code, globals, locals)
                    outputs.append(result)
                else:
                    # Handle statements if needed
                    exec(
                        compile(ast.Module([node], type_ignores=[]), filename="<ast>", mode="exec"),
                        globals,
                        locals,
                    )

            return ___etny_result___("\n".join(outputs))
        else:
            return (
                TaskStatus.PAYLOAD_NOT_DEFINED,
                "Could not find the source file to execute",
            )

        return TaskStatus.SUCCESS, "TASK EXECUTED SUCCESSFULLY"
    except SystemError as e:
        return TaskStatus.SYSTEM_ERROR, e.args[0]
    except KeyError as e:
        return TaskStatus.KEY_ERROR, e.args[0]
    except SyntaxWarning as e:
        return TaskStatus.SYNTAX_WARNING, e.args[0]
    except BaseException as e:
        try:
            if e.args[0][0] == 0:
                return TaskStatus.SUCCESS, e.args[0][1]
            else:
                return TaskStatus.BASE_EXCEPTION, e.args[0]
        except Exception as e:
            return TaskStatus.BASE_EXCEPTION, e.args[0]

