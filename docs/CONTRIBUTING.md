# Commits
- **Commit small, commit often**!
- It is okay to commit non-functional code to a branch.
	- The branches keep it isolated from other people's work.
- **Do not push code directly to `main`**.

## Commit Messages
- [Avoid this](https://xkcd.com/1296/).
- Commit messages have 2 major components: a title and a description.
- Titles:
	- Limited to 50 characters.
	- High-level description of changes made.
	- Use [imperative mood](https://en.wikipedia.org/wiki/Imperative_mood).
	- Complete the sentence "If applied, this commit will `<commit title>`."
		- Do not end with a period.
- Blank line after the title.
- Description:
	- Limited to 72 characters.
	- Explain *what* changes and *why* those changes are made.
	- Don't discuss *how* because that should be evident in the code.
		- Description can be omitted for simple commits.
- Avoid using `git commit -m "<commit message here>"`.
	- This hinders formatting the message.
	- Can be okay for title-only commits.

- Commit message example:
```
Summary of changes in 50 characters or less

More detailed explanation of the changes in this commit. Wrap it to the
next line every 72 characters so it displays easier on more utilities.

Separate paragraphs in the description with a blank line. Don't write a
novel, but make sure to be thorough enough that the reader can
understand the purpose of the commit.
```

# Issues
- Any changes to this repository should be addressing an [issue](
  https://guides.github.com/features/issues/).
- Some guidelines for issues:
	- Try to make the Title 10 words or less.
	- Use [Markdown](https://guides.github.com/features/mastering-markdown/) in the description.
	- Don't worry about the Milestone category.

# Branches
- Different code changes will be organized in [branches](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/about-branches).
- Each issue should have its own branch.
	- Naming of issue-based branches should be `issue-n`, where `n` is the number of the issue.
	- All code written should be done in an issue branch.
- ***DO NOT PUSH CODE DIRECTLY TO `main`.***
	- This will be done with pull requests.

# Pull Requests
- Branches should be merged into their respective source branches through [pull requests](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests).
- Each pull request should follow these guidelines:
	- Try to make the Title 10 words or less
	- Use the `closes` keyword to link issues.
	- Use [Markdown](https://guides.github.com/features/mastering-markdown/) in the description.
	- Have at least 1 reviewer.
		- Preferable to make us all reviewers since there are only 3 of us.
	- Labels/Milestone/Assignees should match any issues which are addressed by the pull request.
- Reviewers should make comments and close them when they are addressed.
- Once all reviews pass, the pull request author can merge the branch.
  - Use **squash and merge** to keep the `main` commit history clean.

# Python Style
- Follow [PEP8](https://www.python.org/dev/peps/pep-0008/) style.
	- [Pylint](https://github.com/PyCQA/pylint) for linting.
	- [YAPF](https://github.com/google/yapf) for fixing formatting.
	- If you use vim, I recommend [ALE](https://github.com/dense-analysis/ale). Otherwise, you're on your own with setup.
- Use [NumPy docstrings](https://numpydoc.readthedocs.io/en/latest/format.html).
- Explicitly state types for function parameters and return types.
	- See [this documentation](https://docs.python.org/3/library/typing.html).
