TypeError: This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs (if you're on Streamlit Cloud, click on 'Manage app' in the lower right of your app).
Traceback:
File "/mount/src/cpa-prep/app.py", line 359, in <module>
    if st.button(sub, key=f"sub_{sub}", disabled=is_disabled):
       ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/metrics_util.py", line 532, in wrapped_func
    result = non_optional_func(*args, **kwargs)
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/elements/widgets/button.py", line 378, in button
    return self.dg._button(
           ~~~~~~~~~~~~~~~^
        label,
        ^^^^^^
    ...<12 lines>...
        shortcut=shortcut,
        ^^^^^^^^^^^^^^^^^^
    )
    ^
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/elements/widgets/button.py", line 1494, in _button
    button_proto.disabled = disabled
    ^^^^^^^^^^^^^^^^^^^^^
