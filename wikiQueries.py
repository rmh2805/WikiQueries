from requests import get
from random import randint
from math import log2

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


def maxWordLen(text):
    text = text.strip().split()
    maxWord = 0
    for word in text:
        maxWord = max(maxWord, len(word))
    return maxWord


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
    print('\t\tDutch  : ' + str(nlMean))
    print('\tSample Std. Deviation:')
    print('\t\tEnglish: ' + str(enDev))
    print('\t\tDutch  : ' + str(nlDev))
    print('\tSample Variance:')
    print('\t\tEnglish: ' + str(enDev ** 2))
    print('\t\tDutch  : ' + str(nlDev ** 2))


def grabSample(text, sampleLength=15):
    data = text.split()
    if len(data) < sampleLength:
        return None

    startIdx = randint(0, len(data) - sampleLength)
    sample = ''
    for i in range(startIdx, startIdx + sampleLength):
        sample += data[i] + ' '
    return sample


def entropy(enCount, nlCount):
    tot = 0.0

    if enCount + nlCount == 0:
        return 0.0

    if enCount != 0:
        p = enCount / (enCount + nlCount)
        tot += p * log2(p)

    if nlCount != 0:
        p = nlCount / (enCount + nlCount)
        tot += p * log2(p)

    return -tot


def printEntropy(enCount, nlCount, nTrials):
    enP = float(enCount) / nTrials
    nlP = float(nlCount) / nTrials
    totP = float(enCount + nlCount) / (2 * nTrials)

    posEntro = entropy(enCount, nlCount)
    negEntro = entropy(nTrials - enCount, nTrials - nlCount)
    totEntro = entropy(nTrials, nTrials)

    remainder = float(enCount + nlCount) / (2 * nTrials) * posEntro
    remainder += float(nTrials * 2 - enCount - nlCount) / (2 * nTrials) * negEntro

    print('\n\tCounts:')
    print('\t\tEnglish: ' + str(enCount))
    print('\t\tDutch  : ' + str(nlCount))
    print('\tProbabilities:')
    print('\t\tP(Positive | English):     ' + str(enP))
    print('\t\tP(Positive | Dutch)  :     ' + str(nlP))
    print('\t\tP(Positive)          : ' + str(totP))
    print('\tInfo Gain:')
    print('\t\tEntropy(Positives) = ' + str(posEntro))
    print('\t\tEntropy(Negatives) = ' + str(negEntro))
    print('\t\tEntropy(Total)     = ' + str(totEntro))
    print('\t\tRemainder(Split)   = ' + str(remainder))
    print('\n\t\tInfo Gain(Split) = ' + str(totEntro - remainder))


# ==============================================<Primary Function Calls>============================================== #
def getMeanLen(nTrials):
    enData = []
    nlData = []

    print('\n\tCalculating the mean word lengths of english and dutch phrases over ' + str(nTrials) + ' trials')

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


def getMaxWordLen(nTrials):
    enData = []
    nlData = []

    print('\n\tCalculating the mean max word length of english and dutch phrases over ' + str(nTrials) + ' trials')

    for i in range(0, nTrials):
        sample = None
        while sample is None or '|' in sample:
            sample = grabSample(randEnPage())
        enData.append(maxWordLen(sample))

        sample = None
        while sample is None or '|' in sample:
            sample = grabSample(randNlPage())
        nlData.append(maxWordLen(sample))

    printMeanAndDev(enData, nlData)


def getSubstringFrequency(nTrials):
    enData = []
    nlData = []
    sStr = input('\tEnter the substring to scan for: ').strip().lower()

    print('\n\tCounting the instances of substring "' + sStr + '" over ' + str(nTrials) + ' trials.')

    for i in range(0, nTrials):

        sample = None
        while sample is None or '|' in sample:
            sample = grabSample(randEnPage())
        enData.append(substringCount(sample, sStr))

        sample = None
        while sample is None or '|' in sample:
            sample = grabSample(randNlPage())
        nlData.append(substringCount(sample, sStr))

    print('\n\tSubstring count for "' + sStr + '"')
    printMeanAndDev(enData, nlData)


def generateTrainingSet(nTrials):
    fName = input('\tEnter the filename to save to: ').strip()

    print('\n\tGenerating a training set of ' + str(nTrials) + ' examples of english and dutch phrases.')
    print('\tSaving training set to ' + fName)

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

    print('\n\t Done')


#
def hasSubstring(nTrials):
    enCount = 0
    nlCount = 0

    sStr = input('\tEnter the substring to scan for: ').strip().lower()
    print('\n\tCounting the samples containing of substring "' + sStr + '" over ' + str(nTrials) + ' trials.')

    for i in range(0, nTrials):
        sample = None
        while sample is None or '|' in sample:
            sample = grabSample(randEnPage())
        if sStr in sample:
            enCount += 1

        sample = None
        while sample is None or '|' in sample:
            sample = grabSample(randNlPage())
        if sStr in sample:
            nlCount += 1

    printEntropy(enCount, nlCount, nTrials)


def hasNSubstrings(nTrials):
    enCount = 0
    nlCount = 0

    sStr = input('\tEnter the substring to scan for: ').strip().lower()
    threshold = None
    while threshold is None or not str(threshold).strip().isnumeric():
        threshold = input('\tEnter the minimum number of occurences of the substring: ')
    threshold = int(threshold)

    print('\n\tCounting the samples containing more than ' + str(threshold - 1) + ' instances of substring "', end='')
    print(sStr + '" over ' + str(nTrials) + ' trials.')

    for i in range(0, nTrials):
        sample = None
        while sample is None or '|' in sample:
            sample = grabSample(randEnPage())
        if substringCount(sample, sStr) >= threshold:
            enCount += 1

        sample = None
        while sample is None or '|' in sample:
            sample = grabSample(randNlPage())
        if substringCount(sample, sStr) >= threshold:
            nlCount += 1

    printEntropy(enCount, nlCount, nTrials)


legalOptions = ['m', 's', 'g', 'h', 'l']


def main():
    print('====<WikiQuery>====')

    while True:
        stIn = ''
        print('\n\n')
        while len(stIn) == 0 or (stIn[0] not in legalOptions and not stIn[0] == 'q'):
            print('\tMean Word Length (m), Substring Count (s), Substring Presence (h), Max Word Length (l)')
            stIn = input('\tor Generate Training Set (g) (quit is \'q\'): ')
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

        if stIn[0] == 'h':
            hasNSubstrings(nTrials)

        if stIn[0] == 'l':
            hasNSubstrings(nTrials)


if __name__ == '__main__':
    main()
