from requests import get

enRand = "https://en.wikipedia.org/wiki/Special:Random"
nlRand = "https://nl.wikipedia.org/wiki/Speciaal:Willekeurig"

startBlocks = ["<p>", '<h1>', '<h2>', '<ol>', '<li>', '<td>']

def getPage(page):
    data = get(page)
    if data.status_code == 200:
        return data.text
    else:
        return None

def stripAngles(line):
    toReturn = ""
    i = 0
    while i < len(line):
        if line[i] == '<':
            i = skipAngles(line, i + 1)
        else:
            toReturn += line[i]
            i += 1

    return toReturn

def skipAngles(line, i):
    if line is None:
        return i

    while i < len(line):
        ch = line[i]
        if ch == '>':
            return i + 1    # Return next char after my block closes
        elif ch == '<':
            i = skipAngles(line, i + 1)  # Skip next set of angles
        else:
            i += 1


def getText(data):
    if not isinstance(data, str):
        return None

    text = ""
    lines = data.split("\n")
    for line in lines:
        line = line.strip()
        good = False

        for startBlock in startBlocks:
            if line.startswith(startBlock):
                good = True
                break
        if not good:
            continue

        text += stripAngles(line) + "\n"
    return text



