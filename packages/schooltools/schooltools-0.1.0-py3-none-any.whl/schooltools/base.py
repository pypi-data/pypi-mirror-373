def base_converter_(method):
    def converter(values):
        result = []
        for val in values:
            # If input is a string like "hello"
            if isinstance(val, str):
                for c in val:
                    if method == "bin":
                        result.append(bin(ord(c))[2:])
                    elif method == "hex":
                        result.append(hex(ord(c))[2:])
                    elif method == "ord":
                        result.append(ord(c))
                    else:
                        raise ValueError(f"Unknown method for string: {method}")
            # If input is a number
            elif isinstance(val, int):
                # Convert number to string first if method is 'ord'
                if method == "ord":
                    result.append(ord(chr(val)))  # val → char → ord
                elif method == "bin":
                    result.append(bin(val)[2:])
                elif method == "hex":
                    result.append(hex(val)[2:])
                elif method == "dec":
                    result.append(str(val))
                else:
                    raise ValueError(f"Unknown method for number: {method}")
            else:
                raise TypeError("Value must be int or str")
        return result
    return converter
