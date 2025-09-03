import base64

def base_converter_(method):
    def converter(values):
        result = []
        for val in values:
            # Handle sequences recursively
            if isinstance(val, (list, tuple)):
                result.append(converter(val))
                continue

            # If input is a string like "hello"
            if isinstance(val, str):
                for c in val:
                    code = ord(c)
                    if method == "bin":
                        result.append(bin(code)[2:])
                    elif method == "hex":
                        result.append(hex(code)[2:])
                    elif method == "oct":
                        result.append(oct(code)[2:])
                    elif method == "ord":
                        result.append(code)
                    elif method == "ascii":
                        result.append(str(code))
                    elif method == "revbin":
                        result.append(bin(code)[2:][::-1])
                    elif method == "base64":
                        result.append(base64.b64encode(c.encode()).decode())
                    else:
                        raise ValueError(f"Unknown method for string: {method}")

            # If input is a number
            elif isinstance(val, (int, float)):
                if method == "ord":
                    try:
                        result.append(ord(chr(int(val))))
                    except ValueError:
                        raise ValueError(f"Invalid number for ord(): {val}")
                elif method == "chr":
                    try:
                        result.append(chr(int(val)))
                    except ValueError:
                        raise ValueError(f"Invalid number for chr(): {val}")
                elif method == "bin":
                    result.append(bin(int(val))[2:])
                elif method == "hex":
                    result.append(hex(int(val))[2:])
                elif method == "oct":
                    result.append(oct(int(val))[2:])
                elif method == "dec":
                    result.append(str(int(val)))
                elif method == "ascii":
                    result.append(str(int(val)))
                elif method == "revbin":
                    result.append(bin(int(val))[2:][::-1])
                elif method == "base64":
                    result.append(base64.b64encode(str(val).encode()).decode())
                else:
                    raise ValueError(f"Unknown method for number: {method}")

            else:
                raise TypeError(f"Unsupported type: {type(val)}")

        return result
    return converter
