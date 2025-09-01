import re

def format_name(name: str) -> str:
    # Replace spaces and remove special characters.
    formatted = name.replace(' ', '_')
    formatted = re.sub(r'[^\w]', '', formatted)
    return formatted

def format_extension(name: str) -> str:
    # Remove leading periods from extension.
    return name.lstrip('.')

def generate_alpha_indices(count: int) -> list[str]:
    # Returns a list with alphabetic indices.
    # E.g., A,B,C,D,...,Z,AA,AB,AC,...,AZ,BA,BB,BC,...,ZZ,AAA,AAB,AAC,...
    res: list[str] = []
    cur: list[str] = []
    for _ in range(count):
        # Find the first place where we can increment:
        i = len(cur)-1
        while i >= 0 and cur[i] == 'Z':
            i -= 1

        # Increment the value at i:
        if i >= 0:
            cur[i] = chr(ord(cur[i])+1)
        else:
            cur = ['A'] + cur

        # Set the suffix to A's:
        i += 1
        while i < len(cur):
            cur[i] = 'A'
            i += 1

        # Add the current list (as a string) to the indices array:
        res.append(''.join(cur))

    return res

def generate_numeric_indices(count: int) -> list[str]:
    # Returns a list with numeric indices.
    # E.g., 1,2,3,4,5,...
    res = [str(i) for i in range(1, count+1)]
    return res

