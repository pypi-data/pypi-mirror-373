from typing import List
from scipy.optimize import minimize
import traceback

def stupid_minimal(func, init_params: List, steps, *args, n=2, **kws):

    best_params = init_params.copy()
    for epoch in range(n):
        for index in range(len(init_params)):
            now_result = func(best_params, *args, **kws)
            while True:
                now_params_1 = best_params.copy()
                now_params_2 = best_params.copy()
                now_params_1[index] += steps[index]
                now_params_2[index] -= steps[index]

                res1 = func(now_params_1, *args, **kws)
                res2 = func(now_params_2, *args, **kws)

                if res1 < now_result:
                    best_params = now_params_1
                    now_result = res1
                    continue

                if res2 < now_result:
                    now_result = res2
                    best_params = now_params_2
                    continue

                break

        print(f"epoch: {epoch} now {now_result}")
    return best_params


def super_minimize(func, x0, arg=(), *args, **kw):
    """如果这个不行，就是scipy.optimize import minimize不行了"""

    methods = [
        "Powell",
        "Nelder-Mead",
        "CG",
        "BFGS",
        "L-BFGS-B",
        "TNC",
        "COBYLA",
        "SLSQP",
        "trust-constr",
    ]

    if "bounds" in kw:
        methods = [
            "Nelder-Mead",
            "L-BFGS-B",
            "TNC",
            "SLSQP",
            "Powell",
            "trust-constr",
            "COBYLA",
        ]

    if "method" in kw:
        return minimize(func, x0, arg, *args, **kw)

    if "methods" in kw:
        methods = kw.pop("methods")
        return minimize(func, x0, arg, *args, **kw)

    # 首轮最小值
    method_results = {}

    for m in methods:
        try:
            result = minimize(func, x0, arg, method=m, *args, **kw)
            method_results[m] = result
            print(m, result.fun)
        except Exception as e:
            print(traceback.format_exc())
            print(m, "error", e)

    min_method = min(method_results, key=lambda m: method_results[m].fun)
    new_x0 = method_results[min_method].x

    print({k: v.fun for k, v in method_results.items()})

    method_results = {}
    for m in methods:
        try:
            result = minimize(func, new_x0, arg, method=m, *args, **kw)
            method_results[m] = result
            print(m, result.fun)
        except Exception as e:
            print(m, "error")

    print({k: v.fun for k, v in method_results.items()})
    min_method = min(method_results, key=lambda m: method_results[m].fun)
    # new_x0 = method_results[min_method].x
    return method_results[min_method]

