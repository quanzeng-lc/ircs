import csv
path = "./hapticData/hapticFeedback.csv"
tmpData = list()
tmpData.append("1")
tmpData.append("2")
#tmpData = ["1", "2"]
with open(path, 'a+') as f:
    csv_writer = csv.writer(f)
    csv_writer.writerow(tmpData)
    #f.write(tmpData[0])

