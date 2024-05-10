def check_empty_fields(username, email, password):
    errors = []
    if len(username.replace(" ", "")) == 0:
        errors.append("Username is empty.")
    if len(email.replace(" ", "")) == 0:
        errors.append("Email is empty.")
    if len(password.replace(" ", "")) == 0:
        errors.append("Password is empty.")

    return errors
