## Dhyan's Code
class Player:
    def __init__(self, name, interactions):
        self.name = name
        self.interactions = interactions
        self.current_area = "spaceship"
        self.current_room = "center"
        self.inventory = []
        self.facing_direction = "north"

    def get_absolute_direction(self, facing, relative_direction):
        direction_aliases = {
            "front": {"front","forward", "f", "forwards", "frontward"},
            "back": {"back", "backward", "b", "backwards", "backward"},
            "left": {"left", "l"},
            "right": {"right", "r"},
        }
        for key, aliases in direction_aliases.items():
            if relative_direction in aliases:
                relative_direction = key
                break
        else:
            raise ValueError(f"Invalid direction: {relative_direction}")
        directions = ["north", "east", "south", "west"]
        offsets = {"front": 0, "right": 1, "back": 2, "left": -1}
        facing_index = directions.index(facing)
        abs_index = (facing_index + offsets[relative_direction]) % 4
        return directions[abs_index]

    def move(self, direction):
        room = self.interactions[self.current_area][self.current_room]
        absolute_direction = self.get_absolute_direction(self.facing_direction, direction)

        if absolute_direction in room["exits"]:
            new_room_name = room["exits"][absolute_direction]
            self.current_room = new_room_name
            self.facing_direction = absolute_direction
            print(f"{self.name} moved {direction} (facing {absolute_direction}) to {self.current_room}")
            print(self.interactions[self.current_area][self.current_room]["description"])
        else:
            print(f"Cannot move {direction} ({absolute_direction}) from {self.current_room}")
            
# interactions and rooms object
interactions = {
    "spaceship": {
        "center":{
            "description": "You are in the center of the spaceship. There are doors to the left and right, and one in front of you.",
            "items": ["crate"],
            "exits": {
                "west": "communications_room",
                "east": "storage_room",
                "north": "control_room",
                "south": "engine_room"
            }
        },
        "communications_room": {
            "description": "You are in the communications room. There are screens and buttons everywhere.",
            "items": ["main control panel", "laptop", "navigation panel", "engine control", "power control", "killswitch"],
            "exits": {
                "east": "center",
                "south": "exit_hatch",
            }
        },
        "storage_room": {
            "description": "You are in the storage room. There are crates and boxes everywhere.",
            "items": ["crate", "box", "locked box", "air tight containment capsule"],
            "exits": {
                "west": "center",
                "south": "rover_launch_bay",
            }
        },
        "control_room": {
            "description": "You are in the control room. There are screens and buttons everywhere.",
            "items": [],
            "exits": {
                "south": "center",
            }
        },
        "engine_room": {
            "description": "You are in the engine room. There are engines and machinery everywhere.",
            "items": [],
            "exits": {
                "north": "center",
                "west": "exit_hatch",
                "east": "rover_launch_bay",
            }
        },
        "rover_launch_bay": {
            "description": "You are in the rover launch bay. There are rovers and equipment everywhere.",
            "items": [],
            "exits": {
                "north": "storage_room",
                "west": "engine_room"
            }
        },
        "exit_hatch": {
            "description": "You are at the exit hatch. You can exit the spaceship from here.",
            "items": [],
            "exits": {
                "north": "communications_room",
                "east": "engine_room",
            }
        }
    },

}

if __name__ == "__main__":
    player = Player("Player1", interactions)
    while True:
        command = input("Enter command: ").strip().lower()
        if command == "exit":
            break
        elif command.startswith("move"):
            parts = command.split()
            if len(parts) < 2:
                print("You must specify a direction")
                continue
            direction = parts[1]
            player.move(direction)
        else:
            print("Invalid command")

## End Dhyan's Code
