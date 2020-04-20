from requests import get
from random import randint

# ================================================<Raw Data Gathering>================================================ #
enRand = "https://en.wikipedia.org/wiki/Special:Random"
nlRand = "https://nl.wikipedia.org/wiki/Speciaal:Willekeurig"


def getPage(page):
    data = get(page)
    if data.status_code == 200:
        return data.text
    else:
        return None


def randEnPage():
    return getText(getPage(enRand))


def randNlPage():
    return getText(getPage(nlRand))


# ==================================================<Text Gathering>================================================== #
badStrs = ['[edit]', '&#91;', '&#93', '&#160;']

startBlocks = ["<p>", '<h1>', '<h2>', '<ol>', '<li>', '<td>']


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
            return i + 1  # Return next char after my block closes
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

    for st in badStrs:
        text = text.replace(st, ' ')

    return text


# ===============================================<Statistic Gathering>================================================ #
def substringCount(text, substring):
    text = ' ' + text.strip().lower() + ' '
    return float(text.count(substring))


def wordLen(text):
    text = text.strip().split()
    numWords = 0
    textSum = 0
    for word in text:
        if len(word) == 0:
            continue
        numWords += 1
        textSum += len(word)

    return float(textSum) / float(numWords)


# ===================================================<Misc Helpers>=================================================== #
def printMeanAndDev(enData, nlData):
    enMean = float(sum(enData)) / len(enData)
    nlMean = float(sum(nlData)) / len(nlData)

    enDev = 0.0
    nlDev = 0.0
    for datum in enData:
        enDev += (datum - enMean) ** 2
    enDev = (enDev / len(enData)) ** 0.5
    for datum in nlData:
        nlDev += (datum - nlMean) ** 2
    nlDev = (nlDev / len(nlData)) ** 0.5

    print('\tSample Mean:')
    print('\t\tEnglish: ' + str(enMean))
    print('\t\t  Dutch: ' + str(nlMean))
    print('\tSample Std. Deviation:')
    print('\t\tEnglish: ' + str(enDev))
    print('\t\t  Dutch: ' + str(nlDev))
    print('\tSample Variance:')
    print('\t\tEnglish: ' + str(enDev ** 2))
    print('\t\t  Dutch: ' + str(nlDev ** 2))


def grabSample(text, sampleLength=15):
    data = text.split()
    if len(data) < sampleLength:
        return None

    startIdx = randint(0, len(data) - sampleLength)
    sample = ''
    for i in range(startIdx, startIdx + sampleLength):
        sample += data[i] + ' '
    return sample


# ==============================================<Primary Function Calls>============================================== #
def getMeanLen(nTrials):
    enData = []
    nlData = []
    for i in range(0, nTrials):
        sample = None
        while sample is None or '|' in sample:
            sample = grabSample(randEnPage())
        enData.append(wordLen(sample))

        sample = None
        while sample is None or '|' in sample:
            sample = grabSample(randNlPage())
        nlData.append(wordLen(sample))

    print('\n\tWord Lengths')
    printMeanAndDev(enData, nlData)


def getSubstringFrequency(nTrials):
    enData = []
    nlData = []
    sStr = input('\tEnter the substring to scan for: ').strip().lower()
    for i in range(0, nTrials):
        nlData += substringCount(grabSample(randNlPage()), sStr)
        enData += substringCount(grabSample(randEnPage()), sStr)

    print('\n\tSubstring count for "' + sStr + '"')
    printMeanAndDev(enData, nlData)


def generateTrainingSet(nTrials):
    fName = input('\tEnter the filename to save to: ').strip()
    fp = open(fName, 'w', encoding='utf8')
    for i in range(0, nTrials):
        if i != 0:
            fp.write('\n')

        sample = None
        while sample is None or '|' in sample:
            sample = grabSample(randEnPage(), 15)
        fp.write('en|' + sample)

        fp.write('\n')
        sample = None
        while sample is None or '|' in sample:
            sample = grabSample(randNlPage(), 15)
        fp.write('nl|' + sample)

    fp.close()


legalOptions = ['m', 's', 'g']


def main():
    print('====<WikiQuery>====')

    while True:
        stIn = ''
        print('\n\n')
        while len(stIn) == 0 or (stIn[0] not in legalOptions and not stIn[0] == 'q'):
            stIn = input('\tMean Word Length (m) or Substring Count (s) or Generate Training Set (g) (quit is \'q\'): ')
            stIn = stIn.strip().lower()
        nTrials = ''
        if stIn[0] == 'q':
            break

        while len(nTrials) == 0 or not nTrials.isnumeric():
            nTrials = input('\tHow many trials to run: ').strip().lower()
        nTrials = int(nTrials)

        if stIn[0] == 'm':
            getMeanLen(nTrials)

        if stIn[0] == 's':
            getSubstringFrequency(nTrials)

        if stIn[0] == 'g':
            generateTrainingSet(nTrials)


if __name__ == '__main__':
    main()
