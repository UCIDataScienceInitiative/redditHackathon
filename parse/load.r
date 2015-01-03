## Read the CSV into a data frame
reddit <- read.csv("redditSubmissions.csv", header=TRUE, stringsAsFactors=FALSE)

## Maybe some columns should be strings? Up to you!
# > reddit$subreddit <- as.factor(reddit$subreddit)
## parse unix epoch time into POSIXct's, in local TZ!
# > reddit <- as.POSIXct(reddit$unixtime, origin="1970-01-01"))