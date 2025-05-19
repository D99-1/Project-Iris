## Dhyan's Code
import time

#Saatviks Code 
items_data = {
    "crate": {
        "description": "A large crate, possibly containing supplies.",
        "interactions": {
            "open": "You open the crate and find some supplies inside.",
            "inspect": "The crate is sturdy and well-sealed."
        },
        "requires": None,
    },
    "box": {
        "description": "A simple cardboard box, sealed shut.",
        "interactions": {
            "inspect": "The box looks fragile but holds something inside."
        },
        "requires": None,
    },
    "locked box": {
        "description": "A small locked box, you need a key to open it.",
        "interactions": {
            "inspect": "The box is locked tight; maybe a key will open it.",
            "open": "It's locked! You can't open it without a key."
        },
        "requires": "key",
    },
}
#end saatviks code 

## Dhyan's Code
class Player:
    def __init__(self, name, interactions):
        self.name = name
        self.interactions = interactions
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
        room = self.interactions[self.current_room]
        absolute_direction = self.get_absolute_direction(self.facing_direction, direction)

        if absolute_direction in room["exits"]:
            new_room_name = room["exits"][absolute_direction]
            self.current_room = new_room_name
            self.facing_direction = absolute_direction
            print(f"{self.name} moved {direction} (facing {absolute_direction}) to {self.current_room}")
            print(self.interactions[self.current_room]["description"])
        else:
            print(f"Cannot move {direction} ({absolute_direction}) from {self.current_room}")
    #End Dhyan 
    #Start Saatvik 
    def look(self):
        room = self.interactions[self.current_room]
        print(room["description"])
        if room["items"]:
            print("You see the following items:")
            for item in room["items"]:
                print(f"-{item}")
        else: 
            print("There seems to be no items in this room.")
    
    def view_inventory(self):
        if not self.inventory:
            print("You currently have no items with you.")
        else:
            print("You are carrying:")
            for item in self.inventory: 
                print(f"-{item}")
                
    def inspect_item(self, item_name):
        if item_name in self.inventory or item_name in self.interactions[self.current_room]["items"]:
            item_info = items_data.get(item_name)
            if item_info and "inspect" in item_info["interactions"]:
                print(item_info["interactions"]["inspect"])
            elif item_info:
                print(item_info["description"])
            else:
                print("There is nothing special about it.")
        else:
            print(f"There is no {item_name} here to inspect.") 

    def pick_up_item(self, item_name):
        room_items = self.interactions[self.current_room]["items"]
        if item_name in room_items:
            self.inventory.append(item_name)
            room_items.remove(item_name)
            print(f"You picked up the {item_name}.")
        else:
            print(f"There is no {item_name} here to pick up.")

    #End Saatvik 
## Dhyan's Code
class Item:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        
class Cutscene:
    def __init__(self, name, text=[], speed=0.03, lineDelay=1):
        self.name = name
        self.text = text
        self.speed = speed
        self.lineDelay = lineDelay

    def play(self):
        print(chr(27) + "[2J")
        for line in self.text:
            print("\n\n")
            for char in line:
                print(char, end='', flush=True)
                time.sleep(self.speed)
            time.sleep(self.lineDelay)
        print("\n")

# interactions and rooms object
interactions = {
        "center":{
            "description": "You are in the center of the spaceship.",
            "items": ["crate"],
            "exits": {
                "west": "communications_room",
                "east": "storage_room",
                "north": "control_room",
                "south": "engine_room"
            }
        },
        "communications_room": {
            "description": "You are in the communications room.",
            "items": ["main control panel", "laptop", "navigation panel", "engine control", "power control", "killswitch"],
            "exits": {
                "east": "center",
                "south": "exit_hatch",
            }
        },
        "storage_room": {
            "description": "You are in the storage room.",
            "items": ["crate", "box", "locked box", "air tight containment capsule"],
            "exits": {
                "west": "center",
                "south": "rover_launch_bay",
            }
        },
        "control_room": {
            "description": "You are in the control room.",
            "items": [],
            "exits": {
                "south": "center",
            }
        },
        "engine_room": {
            "description": "You are in the engine room.",
            "items": [],
            "exits": {
                "north": "center",
                "west": "exit_hatch",
                "east": "rover_launch_bay",
            }
        },
        "rover_launch_bay": {
            "description": "You are in the rover launch bay.",
            "items": [],
            "exits": {
                "north": "storage_room",
                "west": "engine_room"
            }
        },
        "exit_hatch": {
            "description": "You are at the exit hatch.",
            "items": [],
            "exits": {
                "north": "communications_room",
                "east": "engine_room",
            }
        },
        "open_area":{
            "description":"You roam free on the lands of Mars.",
            "items":[],
            "exits": {
                "north": "north_debris",
                "west": "habitat_air_lock",
                "south": "south_debris",
                "east": "exit_hatch"
            }
        },
        "south_debris":{
            "description": "You are in the south debris area.",
            "items": [],
            "exits": {
                "north": "open_area",
                "west": "habitat_sleeping_quarters",
                "east": "rover_pad",
            }
        },
        "north_debris":{
            "description": "You are in the north debris area.",
            "items": [],
            "exits": {
                "south": "open_area",
                "west": "habitat_storage_room",
                "east": "old_rover_pad",
            }
        },
        "habitat_air_lock":{
            "description": "You are in the habitat air lock.",
            "items": [],
            "exits": {
                "north": "open_area",
                "south": "habitat_sleeping_quarters",
            }
        },
        "habitat_irrigation_area": {
            "description": "You are in the habitat irrigation area.",
            "items": [],
            "exits": {
                "north": "habitat_storage_room",
                "south": "habitat_air_lock"
            }
        },
        "habitat_sleeping_quarters": {
            "description": "You are in the habitat sleeping quarters.",
            "items": [],
            "exits": {
                "north": "habitat_air_lock",
                "east": "south_debris",
            }
        },
        "habitat_storage_room": {
            "description": "You are in the habitat storage room.",
            "items": [],
            "exits": {
                "south": "habitat_irrigation_area",
                "east": "north_debris",
            }
        },
        "rover_pad": {
            "description": "You are in the rover pad.",
            "items": [],
            "exits": {
                "west": "south_debris",
            }
        },
        "old_rover_pad": {
            "description": "You are in the old rover pad.",
            "items": [],
            "exits": {
                "west": "north_debris",
            }
        },
}

if __name__ == "__main__":
    player = Player("Player1", interactions)
    intro_cutscene = Cutscene("Intro", ["You wake up in a spaceship, disoriented and confused. You need to find a way out.", "You look around and see a crate in the center of the room."], speed=0.05, lineDelay=2)
    intro_cutscene.play()

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
        elif command == "look":
            player.look()
        elif command == "inventory":
            player.view_inventory()
        else:
            print("Invalid command")

## End Dhyan's Code
