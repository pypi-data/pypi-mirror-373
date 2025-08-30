from importlib.metadata import entry_points

# Get all entry points
eps = entry_points()

# Print the entry points
for ep in eps:
    print(ep)
