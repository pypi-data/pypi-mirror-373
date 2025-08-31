# Talk Gooder

![PyPI - License](https://img.shields.io/pypi/l/talkgooder?color=blue)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/brianwarner/talkgooder/pre-release.yml?label=Build%20and%20test)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/brianwarner/talkgooder/release.yml?label=Publish%20to%20PyPI)
![PyPI - Downloads](https://img.shields.io/pypi/dm/talkgooder)

`talkgooder` attempts to smooth out grammar, punctuation, and number-related corner cases when formatting text for human consumption. It is intended for applications where you know there's a noun and are trying to generate text, but you don't know much about it.

It handles:

* Plurals: "one cat" vs. "zero cats"
* Possessives: "the cat's toy" vs. "both cats' toys"
* Numbers to words: 2 == "two", 16 == 16
* "There is" vs. "There are": "There is one cat" vs. "There are two cats"
* "A" vs. "An": "A cat" vs. "An orange cat"
* "Was" vs. "Were": "There was one cat" vs. "There were two cats"

``talkgooder`` is currently specific to American English, but it is extensible to other languages.

Contributions are welcome at [github.com/brianwarner/talkgooder](https://github.com/brianwarner/talkgooder)!
