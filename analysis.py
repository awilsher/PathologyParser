import pandas as pd

def generate_csv(file):
    data_file = open(file,"r")

    csv = open("proper.csv","w")
    for line in data_file:
        tokens = line.split(",")
        text = ''.join(str(token) for token in tokens[3:])
        csv.write('{0},{1},{2},"{3}"\n'.format(tokens[0],tokens[1],tokens[2],text))

def no_test_match(file, tests_file, results_file):
    tests = [line for line in open(tests_file).readlines()]
    results = [line for line in open(results_file).readlines()]

    both = open("both.txt","w")
    result_file = open("result_file","w")
    test_file = open("test_file","w")

    for line in open(file,"r"):
        test_no_match = True;
        result_no_match = True;
        text = ''.join(str(t) for t in line.split(",")[3:])

        for t in tests:
            if text.find(t.strip())>-1:
                test_no_match = False
                break

        if (test_no_match):
            test_file.write("<doc>\n"+text+"\n</doc>")

        for r in results:
            if text.find(r.strip())>-1:
                result_no_match = False
                break

        if (result_no_match):
            result_file.write("<doc>\n" + text + "\n</doc>")

        if (result_no_match and test_no_match):
            both.write("<doc>\n" + text + "\n</doc>")


def text(file ):

    text_file = open("data.txt","w")

    for line in open(file,"r"):
        text = ''.join(str(t) for t in line.split(",")[3:])
        text_file.write(text)

# text("syp.csv")

no_test_match("syp.csv","tests.dic","results.dic")


