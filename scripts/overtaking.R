library("dplyr")

df = read.csv("events.csv", header = 1, sep = ",")
print(length(filter(df, classification == 1, interval_length == 1, flag == 0)))

