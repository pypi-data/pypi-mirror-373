import dis

from wedeliver_core_plus.helpers.get_callback import get_callback


def get_embedded_function(function):
    bytecode = dis.Bytecode(function)
    instrs = list(reversed([instr for instr in bytecode]))
    function, module = None, None
    for (ix, instr) in enumerate(instrs):
        # print(instr)
        if instr.opname == "IMPORT_NAME":
            module = instr.argval
        if instr.opname == "IMPORT_FROM":
            if function is None:
                function = instr.argval

    # print(function)
    # print(module)
    function = get_callback(module=module, function=function)
    return function
