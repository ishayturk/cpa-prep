שגיאת מייל: 'ascii' codec can't encode character '\u202b' in position 1: ordinal not in range(128)

Traceback (most recent call last):
  File "/mount/src/cpa-prep/utils.py", line 276, in send_otp_email
    server.login(gmail_user, gmail_pass)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.13/smtplib.py", line 753, in login
    (code, resp) = self.auth(
                   ~~~~~~~~~^
        authmethod, getattr(self, method_name),
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        initial_response_ok=initial_response_ok)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.13/smtplib.py", line 650, in auth
    response = encode_base64(initial_response.encode('ascii'), eol='')
                             ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^
UnicodeEncodeError: 'ascii' codec can't encode character '\u202b' in position 1: ordinal not in range(128)
שגיאה בשליחת המייל. בדוק/י Secrets ונסה שוב.
