from common_agent_code.backend.utils.OutputCapture import OutputCapture
from common_agent_code.backend.utils.AgentState import AgentState
from common_agent_code.backend.utils.ExecutionResult import ExecutionResult
import traceback

def execute_code(code: str, state: AgentState) -> ExecutionResult:
    import os
    import uuid
    import json
    import numbers
    import matplotlib.pyplot as plt
    import textwrap

    # ✅ Static dir configurable via env var
    static_dir = os.getenv("FLASK_STATIC_DIR") or os.path.join(os.path.dirname(__file__), "static")
    os.makedirs(static_dir, exist_ok=True)

    # Replace plt.show() with "save to static + record in returned_objects"
    plot_save_code = textwrap.dedent(f"""
    import os
    import matplotlib.pyplot as plt
    import uuid
    static_dir = r"{static_dir}"
    os.makedirs(static_dir, exist_ok=True)
    plot_path_fs = os.path.join(static_dir, f"plot_{{uuid.uuid4()}}.png")
    web_path = f"/static/{{os.path.basename(plot_path_fs)}}"
    plt.savefig(plot_path_fs)
    returned_objects.setdefault("plot_paths", []).append(web_path)
    plt.close()
    """)
    code = code.replace("plt.show()", plot_save_code)

    if not code.strip():
        return ExecutionResult(output="No code to execute", returned_objects={})

    # ---- shared env & returned_objects reuse ----
    shared_env = state.data.copy()
    existing_ro = state.data.get("returned_objects")
    if isinstance(existing_ro, dict):
        returned_objects = existing_ro  # ✅ reuse
    else:
        returned_objects = {}
    state.data["returned_objects"] = returned_objects
    shared_env["returned_objects"] = returned_objects

    def _is_primitive(x):
        if x is None or isinstance(x, (str, bool, numbers.Number)):
            return True
        if isinstance(x, list):
            return all(_is_primitive(i) for i in x)
        if isinstance(x, dict):
            return all(isinstance(k, str) and _is_primitive(v) for k, v in x.items())
        return False

    def _is_preservable(x):
        """Check if an object can be preserved in state"""
        if _is_primitive(x):
            return True
        # Add more types that can be safely preserved
        import pandas as pd
        import numpy as np
        if isinstance(x, (pd.DataFrame, pd.Series, np.ndarray)):
            return True
        # For other objects, try to check if they're picklable
        try:
            import pickle
            pickle.dumps(x)
            return True
        except:
            return False

    SAFE_STATE_KEYS = {"returned_objects"}

    with OutputCapture() as output:
        try:
            # Run code
            if "\n" not in code and not code.strip().endswith(":"):
                # Single expression -> eval
                result = eval(code, shared_env, shared_env)
                if result is not None and _is_preservable(result):
                    returned_objects["result"] = result
            else:
                # Multi-line -> exec
                exec(code, shared_env, shared_env)

            # Catch figures not explicitly saved
            if plt.get_fignums():
                plot_path_fs = os.path.join(static_dir, f"plot_{uuid.uuid4()}.png")
                plt.savefig(plot_path_fs)
                plt.close()
                web_path = f"/static/{os.path.basename(plot_path_fs)}"
                returned_objects.setdefault("plot_paths", []).append(web_path)

            # ---- Enhanced state update (preserve more objects) ----
            for key, value in shared_env.items():
                if key in SAFE_STATE_KEYS:
                    if key == "returned_objects" and isinstance(value, dict):
                        safe_ro = {}
                        for kk, vv in value.items():
                            if _is_preservable(vv):
                                safe_ro[kk] = vv
                        state.data["returned_objects"] = safe_ro
                    else:
                        if _is_preservable(value):
                            state.data[key] = value
                elif _is_preservable(value) and not key.startswith('_'):
                    # Preserve any other preservable variables (except private ones)
                    state.data[key] = value
                    # Also add to returned_objects for easier access
                    returned_objects[key] = value

            # CRITICAL: Ensure returned_objects only contains sanitized data
            # This prevents recursion issues when saving state
            sanitized_returned_objects = {}
            for key, value in returned_objects.items():
                if _is_preservable(value):
                    sanitized_returned_objects[key] = value

            return ExecutionResult(
                output=output.stdout.getvalue(),
                error=None,
                traceback=None,
                returned_objects=sanitized_returned_objects
            )

        except Exception as e:
            return ExecutionResult(
                output=output.stdout.getvalue(),
                error=str(e),
                traceback=traceback.format_exc(),
                returned_objects=returned_objects
            )
