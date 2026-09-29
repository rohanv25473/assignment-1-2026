# Edmunds Luxury-Car Discussion Analysis

Vocabulary for the assignment's analysis of the supplied discussion corpus.

## Language

**Corpus**:
The `sample_data.csv` discussion records treated as the complete source for this assignment.
_Avoid_: Full Edmunds population

**Post**:
One discussion message with a username, date label, and text.
_Avoid_: Mention, sentence

**Usable post**:
A distinct post with nonblank text retained for analysis. It may contain no top-10 brand and still belong to the analysis denominator.
_Avoid_: Raw row

**Author**:
The username attached to a post. An author may contribute many posts.
_Avoid_: Customer, respondent

**Marque**:
A consumer-facing automobile brand, such as Lexus or Toyota. A parent company such as GM is a different entity.
_Avoid_: Manufacturer, corporate family

**Brand reference**:
A passage in which the post's author substantively discusses a marque, whether named directly or through an identifiable model or alias.
_Avoid_: Raw brand token

**Attribute theme**:
A broad vehicle feature or evaluative dimension, such as performance or comfort.
_Avoid_: Sentiment, purchase intent

**Subattribute**:
A more specific aspect of an attribute theme, such as acceleration or handling within performance.
_Avoid_: Synonym

**Competitive relation**:
A meaningful connection between marques in a post, such as comparison, shared evaluation, or consideration as purchase alternatives.
_Avoid_: Mere co-mention

**Lexical co-occurrence**:
Two different marques recognized in the same post, regardless of how far apart their mentions occur.
_Avoid_: Competitive relation

**GM-expanded brand label**:
A marque label assigned through the agreed GM parent-reference rule rather than a direct reference to that marque.
_Avoid_: Explicit marque mention

**Aspiration**:
The author's expressed desire to buy or own a vehicle from a marque, including a clear conditional desire. Admiration or current ownership alone does not establish aspiration.
_Avoid_: Popularity, sentiment

**Concrete purchase intent**:
An expressed plan or intention to acquire a vehicle, distinguished from ownership wishes contingent on an unmet condition.
_Avoid_: Dream ownership

**Conditional ownership desire**:
An expressed personal wish to own a vehicle despite an unmet condition such as affordability.
_Avoid_: Purchase commitment
