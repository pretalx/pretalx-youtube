# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/pretalx/pretalx-youtube/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                             |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|--------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| pretalx\_youtube/\_\_init\_\_.py |        1 |        0 |        0 |        0 |    100% |           |
| pretalx\_youtube/api.py          |       85 |       49 |       26 |        0 |     32% |20-25, 28, 37-46, 50-53, 56-63, 79-81, 84-87, 94, 97, 100, 104-137 |
| pretalx\_youtube/apps.py         |       15 |        0 |        0 |        0 |    100% |           |
| pretalx\_youtube/forms.py        |       49 |       33 |       18 |        1 |     25% |25-42, 51-69, 72-79 |
| pretalx\_youtube/models.py       |       18 |        3 |        0 |        0 |     83% |25, 29, 33 |
| pretalx\_youtube/recording.py    |        6 |        6 |        2 |        0 |      0% |       1-8 |
| pretalx\_youtube/signals.py      |       10 |        1 |        0 |        0 |     90% |        12 |
| pretalx\_youtube/views.py        |       56 |       31 |       16 |        0 |     35% |20, 37-66, 69-80 |
| **TOTAL**                        |  **240** |  **123** |   **62** |    **1** | **39%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/pretalx/pretalx-youtube/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/pretalx/pretalx-youtube/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pretalx/pretalx-youtube/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/pretalx/pretalx-youtube/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fpretalx%2Fpretalx-youtube%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/pretalx/pretalx-youtube/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.