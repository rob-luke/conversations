# Example Analysis

## Example 1 - Three Speaker Podcast

In the following example we analyse a podcast with three speakers.
The audio file is pulled from an S3 bucket and the speaker mapping
is provided. We ask the `Conversations` package to transcribe,
diarise, summarise and generate an interactive HTML version of
the transcription. To view the html version of the transcript
click on the blue button below.

``` title="podcast_example.py"
--8<-- "examples/podcast_example.py"
```

[Interactive HTML Report](
https://project-test-data-public.s3.amazonaws.com/conversation.html
){ .md-button .md-button--primary }

```text
# Summary:
# In the meeting, Alice, Sam and Bob discuss the financial state of
# businesses, the challenges of companies going private, and the
# evolution of private equity firms' return expectations. They
# also touch on the industry's early risk-taking nature. Bob
# mentions historical deals as examples of the early risk-taking
# nature of private equity firms.
# 
# Key Points:
# 1. Challenges of companies going private
#    Alice: "Challenges of companies going private, especially in
#    terms of cutting expenses and finding new ways to pay
#    employees who were previously compensated with stocks."
# 2. Private equity firms' return expectations
#    Sam: "What are private equity firms' return expectations
#    when purchasing a company?"
# 3. Evolution of the private equity industry
#    Bob: "The industry has evolved over time, with early private
#    equity firms taking on riskier ventures,
#    similar to venture capitalists."
# ...
# 
# Action Items:
# None discussed in the meeting.
# 
# 20 Keywords (most to least relevant):
# 1. Financial state
# 2. Business
# 3. Operating cash flow
# ...
# 
# 10 Concepts/Themes (most to least relevant):
# 1. Financial challenges
# 2. Going private
# 3. Private equity
# ...
# 
# Most unexpected aspect of the conversation:
# The most unexpected aspect of the conversation was the mention of
# historical deals like RJR Nabisco and TWA Airlines as examples
# of the early risk-taking nature of private equity firms.
# 
# Concepts/Topics explained in the transcript:
# 1. Private equity firms' return expectations:
#    Bob explains that the industry has evolved over time,
#    with early private equity firms taking on riskier ventures,
#    similar to venture capitalists. No inaccuracies were identified.
# 
# Tone of the conversation:
# Overall tone: Informative and analytical
# Alice's tone: Concerned and analytical
# Bob's tone: Informative and explanatory
# Sam's tone: Inquisitive
```
