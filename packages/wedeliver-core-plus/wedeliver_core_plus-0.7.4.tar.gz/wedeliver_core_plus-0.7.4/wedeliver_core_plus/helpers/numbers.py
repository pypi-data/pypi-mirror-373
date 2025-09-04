def fix_number(number):
    try:
        return round(float(number), 2)
    except Exception:
        pass

    return 0


def format_number(number, with_commas=False):
    try:
        # Convert to float and round to 2 decimal places
        fixed_number = round(float(number), 2)
    except (ValueError, TypeError):
        # Handle invalid inputs by setting fixed_number to 0.00
        fixed_number = 0.00

    # Convert -0.00 to 0.00
    if fixed_number == -0.0:
        fixed_number = 0.0

    # Return the fixed number formatted to 2 decimal places with commas every three digits
    if with_commas:
        return "{:,.2f}".format(fixed_number)

    # Return the fixed number formatted to 2 decimal places
    return "{:.2f}".format(fixed_number)