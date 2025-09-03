# rebello

`git rebase --interactive` for Trello. Opens a Trello board in `$EDITOR` for editing like a normal
Markdown document.

## Authorization

`rebello` uses the following env vars:

```bash
# Get this from Trello API keys page.
# https://developer.atlassian.com/cloud/trello/guides/power-ups/managing-power-ups/#managing-your-api-key
export TRELLO_API_KEY="..."

# To get this, visit https://trello.com/1/authorize?expiration=13days&name=MyApp&scope=read,write&response_type=token&key=$TRELLO_API_KEY
export TRELLO_API_SECRET="..."

# To get this, visist your board in a web browser, append `.json` to the url and inspect the JSON.
export TRELLO_BOARD_ID="..."
```
