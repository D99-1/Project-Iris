## Dhyan's Code
import time

#Saatviks Code 
#end saatviks code 

## Dhyan's Code
class Player:
    def __init__(self, name, rooms):
        self.name = name
        self.rooms = rooms
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
        room = self.rooms[self.current_room]
        absolute_direction = self.get_absolute_direction(self.facing_direction, direction)

        if absolute_direction in room.exits:
            new_room_name = room.exits[absolute_direction]
            self.current_room = new_room_name
            self.facing_direction = absolute_direction
            print(f"{self.name} moved {direction} (facing {absolute_direction}) to {self.current_room}")
            print(self.rooms[self.current_room].description)
        else:
            print(f"Cannot move {direction} ({absolute_direction}) from {self.current_room}")

    def look(self):
        room = self.rooms[self.current_room]
        print(room.description)
        if room.items:
            print("You see the following items:")
            for item in room.items:
                print(f"- {item.name}")
        else:
            print("There seems to be no items in this room.")

    
    def view_inventory(self): #allows the player to view their inventory 
        if not self.inventory:
            print("You currently have no items with you.")
        else:
            print("You are carrying:")
            for item in self.inventory: 
                print(f"-{item}")

    #End Saatvik 
## Dhyan's Code
class Item:
    def __init__(self, name, description, requires=None, interactions=None):
        self.name = name
        self.description = description
        self.requires = requires
        self.interactions = interactions or {}
        
    def inspect(self):
        if "inspect" in self.interactions:
            return self.interactions["inspect"]
        return self.description

class Room:
    def __init__(self, name, description, exits, items):
        self.name = name
        self.description = description
        self.exits = exits
        self.items = items

        
class Cutscene:
    def __init__(self, text=[], speed=0.03, lineDelay=1):
        self.text = text
        self.speed = speed
        self.lineDelay = lineDelay

    def play(self):
        print("\n\n")
        for line in self.text:
            print("\n\n")
            for char in line:
                print(char, end='', flush=True)
                time.sleep(self.speed)
            time.sleep(self.lineDelay)
        print("\n")

# interactions and rooms object
items = {
    "crate": Item("crate", "A large crate, it seems to be locked.", requires=["key"]),
}

rooms = {
    "center": Room(
                    "center", 
                    "You are in the center of the shipship.", 
                    {"west": "communications_room", "east": "storage_room", "north": "control_room", "south": "engine_room"}, 
                    [items["crate"]]
                ),
    "communications_room": Room(
                    "communications_room", 
                    "You are in the communications room.", 
                    {"east": "center", "south": "exit_hatch"}, 
                    []
                ),
    "storage_room": Room(
                    "storage_room", 
                    "You are in the storage room.", 
                    {"west": "center", "south": "rover_launch_bay"}, 
                    []
                ),
    "control_room": Room(
                    "control_room", 
                    "You are in the control room.", 
                    {"south": "center"}, 
                    []
                ),
    "engine_room": Room(
                    "engine_room", 
                    "You are in the engine room.", 
                    {"north": "center", "west": "exit_hatch", "east": "rover_launch_bay"}, 
                    []
                ),
    "rover_launch_bay": Room(
                    "rover_launch_bay", 
                    "You are in the rover launch bay.", 
                    {"north": "storage_room", "west": "engine_room"}, 
                    []
                ),
    "exit_hatch": Room(
                    "exit_hatch", 
                    "You are at the exit hatch.", 
                    {"north": "communications_room", "east": "engine_room"}, 
                    []
                ),
    "open_area": Room(
                    "open_area", 
                    "You roam free on the lands of Mars.", 
                    {"north": "north_debris", "west": "habitat_air_lock", "south": "south_debris", "east": "exit_hatch"}, 
                    []
                ),
    "south_debris": Room(
                    "south_debris", 
                    "You are in the south debris area.", 
                    {"north": "open_area", "west": "habitat_sleeping_quarters", "east": "rover_pad"}, 
                    []
                ),
    "north_debris": Room(
                    "north_debris", 
                    "You are in the north debris area.", 
                    {"south": "open_area", "west": "habitat_storage_room", "east": "old_rover_pad"}, 
                    []
                ),
    "habitat_air_lock": Room(
                    "habitat_air_lock", 
                    "You are in the habitat air lock.", 
                    {"north": "open_area", "south": "habitat_sleeping_quarters"}, 
                    []
                ),
    "habitat_irrigation_area": Room(
                    "habitat_irrigation_area", 
                    "You are in the habitat irrigation area.", 
                    {"north": "habitat_storage_room", "south": "habitat_air_lock"}, 
                    []
                ),
    "habitat_sleeping_quarters": Room(
                    "habitat_sleeping_quarters", 
                    "You are in the habitat sleeping quarters.", 
                    {"north": "habitat_air_lock", "east": "south_debris"}, 
                    []
                ),
    "habitat_storage_room": Room(
                    "habitat_storage_room", 
                    "You are in the habitat storage room.", 
                    {"south": "habitat_irrigation_area", "east": "north_debris"}, 
                    []
                ),
    "rover_pad": Room(
                    "rover_pad", 
                    "You are in the rover pad.", 
                    {"west": "south_debris"}, 
                    []
                ),
    "old_rover_pad": Room(
                    "old_rover_pad", 
                    "You are in the old rover pad.", 
                    {"west": "north_debris"}, 
                    []
                )
}


if __name__ == "__main__":
    player = Player("Player1", rooms)
    intro_cutscene = Cutscene(["You wake up in a spaceship, disoriented and confused. You need to find a way out.", "You look around and see a crate in the center of the room."], speed=0.05, lineDelay=2)
    intro_cutscene.play()

    print(rooms["center"].description)

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
