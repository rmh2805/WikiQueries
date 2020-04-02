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


def substringFrequency(text, substring):
    text = ' ' + text.strip().lower() + ' '
    return float(text.count(substring))/float(len(text) * len(substring))


def wordLen(text):
    text = text.strip().split()
    numWords = 0
    textSum = 0
    for word in text:
        if len(word) == 0:
            continue
        numWords += 1
        textSum += len(word)

    return float(textSum)/float(numWords)

def main():
    print('====<WikiQuery>====')

    while True:
        stIn = ''
        while len(stIn) == 0 or (not stIn[0] == 'w' and not stIn[0] == 's' and not stIn[0] == 'q'):
            stIn = input('\n\tWord Count (w) or Substring (s) (quit is \'q\'): ').strip().lower()
        nTrials = ''
        if stIn[0] == 'q':
            break

        while len(nTrials) == 0 or not nTrials.isnumeric():
            nTrials = input('\tHow many trials to run: ').strip().lower()
        nTrials = int(nTrials)

        enSum = 0.0
        nlSum = 0.0
        if stIn[0] == 'w':
            for i in range(0, nTrials):
                enSum += wordLen(getText(getPage(enRand)))
                nlSum += wordLen(getText(getPage(nlRand)))

            print('\n\tAvg word lengths:')

        if stIn[0] == 's':
            sStr = input('\tEnter the substring to scan for: ').strip().lower()
            for i in range(0, nTrials):
                nlSum += substringFrequency(getText(getPage(nlRand)), sStr)
                enSum += substringFrequency(getText(getPage(enRand)), sStr)

            print('\n\tFrequencies for substring "' + sStr + '"')

        print('\t\ten: ' + str(enSum / float(nTrials)))
        print('\t\tnl: ' + str(nlSum / float(nTrials)))


if __name__ == '__main__':
    main()
