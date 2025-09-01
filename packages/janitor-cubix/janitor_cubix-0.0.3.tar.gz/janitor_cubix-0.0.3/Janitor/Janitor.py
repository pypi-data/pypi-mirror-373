def warn(msg):
        print(f"\033[93m{msg}")

def pcall(func, *args, **kwargs):
    try:
        result = func(*args, **kwargs)
        return True, result
    except Exception as e:
        return False, e

class Janitor:

    def __init__(self):
        self.Chores = []

    def GiveChore(self, _chore):
        chore = _chore
        if callable(_chore):
            self.Chores.append(chore)
            
    def Clean(self):
        for i, chore in enumerate(self.Chores):
            if callable(chore):
                success, result = pcall(chore)

                if not success:
                    warn(f"Janitor encountered error: {result}")

        self.Chores.clear()

