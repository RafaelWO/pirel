# Output path of the GIF
Output assets/images/cli_demo.gif

Require pyenv

Set FontSize 26
Set Width 1200
Set Height 1000
Set Theme "Wombat"

# Setup pyenv
Hide
Type `eval "$(pyenv init -)"`
Enter 2
Type "clear"
Enter
Show

# Activate Python 3.13
Type "pyenv shell 3.13"
Sleep 500ms
Enter
Sleep 500ms

# Show Python version
Type "python -V"
Enter
Sleep 1s

# Run Pirel check
Type "pirel check"
Sleep 500ms
Enter

# Admire the output for a bit.
Sleep 5s

# Activate Python 3.8
Type "pyenv shell 3.8"
Sleep 500ms
Enter
Sleep 500ms

# Show Python version
Type "python -V"
Enter
Sleep 1s

# Run Pirel check
Type "pirel check"
Sleep 500ms
Enter

# Admire the output for a bit.
Sleep 5s

# Clear the screen
Type "clear"
Sleep 500ms
Enter

# Run Pirel list
Type "pirel list"
Sleep 500ms
Enter

# Admire the output for a bit.
Sleep 7s
