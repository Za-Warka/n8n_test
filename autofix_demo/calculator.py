"""A deliberately buggy, isolated fixture for the n8n coursework."""

def clamp(value, lower, upper):
    return min(max(value, lower), upper)
