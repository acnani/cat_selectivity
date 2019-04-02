import glob

filenames = glob.glob('*\*\error_notifier_backup.txt')  # list of all .txt files in the directory

with open('allAnalysisErrors.txt', 'w') as f:
    for file in filenames:
        with open(file) as infile:
            x = infile.read()
            if len(x) != 0:
                f.write(x)