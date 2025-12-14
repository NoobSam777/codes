# Stop pausing movies to look up words. Use Python instead. 🐍🎬

Watching movies in English is great, but pausing every 5 seconds to check the dictionary ruins the flow. That’s why I wrote a Python script to do the hard work for me before I even press play.

Meet the "English Vocab Sniper". It analyzes any subtitle file (.srt) and uses NLP (Natural Language Processing) to tell me exactly what I need to study.

# How it works:

1. It cleans the mess: Removes timecodes and HTML tags.

2. It thinks like a human: Uses the NLTK library to lemmatize words (so "running" and "ran" count as the same word: "RUN").

3. It generates two Elite Lists:

    - 🎯 The Vital List: The top 30 most frequent words. If I don't know these, I won't understand the plot.

    - 🔬 The Sniper List: Long, specific, and technical words that appear 2-4 times. Perfect for expanding advanced vocabulary.

Now, I just review the list for 5 minutes, and I’m ready to watch the movie fluently.
