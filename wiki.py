import wikipedia

# The topic you want to get info about
topic = "Mathematics"

# Fetch the first 2 sentences of the Wikipedia summary for that topic
summary = wikipedia.summary(topic, sentences=2)

# Print the summary to the console
print(summary)

