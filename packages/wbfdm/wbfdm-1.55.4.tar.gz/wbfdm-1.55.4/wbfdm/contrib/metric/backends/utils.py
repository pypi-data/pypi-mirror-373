from datetime import date


def get_today():  # utility function to be able to mock today in the test suit
    return date.today()
