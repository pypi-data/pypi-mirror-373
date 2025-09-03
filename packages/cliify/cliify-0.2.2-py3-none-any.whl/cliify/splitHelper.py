

def splitWithEscapes(string, delimiter, escape_pairs=['""', "{}", "[]", "<>", "()"], strip=True, maxsplit=-1):
    """
    Split a string by a delimiter, but ignore delimiters that are inside escape_pairs.
    
    Args:
        string: The string to split
        delimiter: The character to split on
        escape_pairs: List of pairs of characters that define escaped regions
        strip: Whether to strip whitespace from the resulting strings
        maxsplit: Maximum number of splits to perform. -1 means no limit.
    """
    split = []
    counts = {}
    splits_performed = 0

    for pair in escape_pairs:
        counts[pair] = 0

    def processEscapes(char):
        for key in escape_pairs:
            if key[0] == key[1] and char == key[0]:
                #if the escape pair is the same character, then we toggle the escape at each instance
                counts[key] = counts[key] ^ 1
            else:
                if char == key[0]:
                    counts[key] += 1
                elif char == key[1]:
                    counts[key] -= 1
    
    def isEscaped():
        for key in escape_pairs:
            if counts[key] > 0:
                return True
        return False
        
    current = ''
    for i in range(len(string)):
        # If we've hit maxsplit, just append the rest of the string
        if maxsplit != -1 and splits_performed >= maxsplit:
            current += string[i:]
            break
            
        if string[i] == delimiter and not isEscaped() and current != '':
            if strip:
                current = current.strip()
            split.append(current)
            splits_performed += 1
            current = ''
        else:
            processEscapes(string[i])
            current += string[i]
    
    if current != '' or len(split) > 0:
        if strip:
            current = current.strip()
        split.append(current)
    
    return split
