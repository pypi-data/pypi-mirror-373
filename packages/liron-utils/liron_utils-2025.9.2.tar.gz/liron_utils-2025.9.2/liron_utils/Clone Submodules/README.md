### Clone Submodules

To clone a submodule (e.g, `liron-utils`) into your repository, run:\
`git submodule add https://github.com/lironst1/liron-utils.git`

You will be asked to input your username and password to GitHub.

- username: `lironst1`
- password: my personal access token (saved in iCloud Drive)

You might be needed to run:\
`git submodule update --init --recursive`

The next time you will be cloning the parent repo, instead of `git clone <project url>`, run:\
`git clone --recursive <project url>`

When pulling updates from GitHub, git does NOT automatically update the submodules.
In order to update the submodules, you will need to run:\
`git submodule update --remote`

For further information, see these links:

- [Working with submodules](https://github.blog/2016-02-01-working-with-submodules/)
- [Git Tools - Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules)