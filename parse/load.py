import csv

with open('redditSubmissions.csv', 'rb') as csvfile:
     redditor = csv.reader(csvfile, delimiter=',')
     # special treatment for the header row
     headers = next(redditor, None)
     # now loop over the rest of the rows
     for row in redditor:
          print ', '.join(row)
