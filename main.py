## Dhyan's Code
import time

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
            print(self.rooms[self.current_room].description)
        else:
            print(f"Cannot move {direction} from {self.current_room}")
#saatviks code 
    def look(self):
        room = self.rooms[self.current_room]
        print(room.description)
        if room.items:
            print("You see the following items:")
            for item in room.items:
                print(f"- {item.name}")
        else:
            print("There seems to be no items in this room.")

    
    def view_inventory(self): 
        if not self.inventory:
            print("You currently have no items with you.")
        else:
            print("You are carrying:")
            for item in self.inventory: 
                print(f"-{item.name}")

#end saatviks code 
## Dhyan's Code
class Item:
    def __init__(self, name, description, requires=None, interactions=None):
        self.name = name
        self.description = description
        self.requires = requires
        self.interactions = interactions or {}
#saatviks code       
    def inspect(self):
        if "inspect" in self.interactions:
            return self.interactions["inspect"]
        return self.description
#end saatviks code
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
#saatviks code
items = {
    "crate": Item("crate", "A large crate, it seems to be bolted shut.", requires=["crowbar"]),
    "crowbar": Item("crowbar","A sturdy iron crowbar, perfect for prying off bolts and nails."),
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
                    [items["crowbar"]]
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

class Game:
    def __init__(self, player, rooms):
        self.player = player
        self.rooms = rooms
        self.running = True
        self.commands = {
            "move": self.command_move,
            "look": self.command_look,
            "inventory": self.command_inventory,
            "take": self.command_take,
            "pickup": self.command_take,
            "use": self.command_use,
            "help": self.command_help,
            "exit": self.command_exit,
        }

    def start(self):
        print(self.rooms[self.player.current_room].description)
        while self.running:
            command_input = input("\n> ").strip().lower()
            self.handle_command(command_input)

    def handle_command(self, command_input):
        if not command_input:
            return

        parts = command_input.split()
        command = parts[0]
        args = parts[1:]

        if command in self.commands:
            self.commands[command](args)
        else:
            print("Unknown command. Type 'help' for a list of commands.")

    def command_move(self, args):
        if not args:
            print("Move where?")
            return
        self.player.move(args[0])

    def command_look(self, args):
        self.player.look()

    def command_inventory(self, args):
        self.player.view_inventory()

    def command_take(self, args):
        if not args:
            print("Take what?")
            return
        item_name = " ".join(args)
        room = self.rooms[self.player.current_room]
        for item in room.items:
            if item.name.lower() == item_name:
                self.player.inventory.append(item)
                room.items.remove(item)
                print(f"You picked up the {item.name}.")
                return
        print(f"No item named '{item_name}' found here.")
#saatviks code
    def command_use(self, args):
        if not args:
            print("Use what?")
            return
        item_name = " ".join(args)     
        item_to_use = next((item for item in self.player.inventory if item.name.lower() == item_name), None)
        if not item_to_use:
            print(f"You don't have an item named '{item_name}'.")
            return
        current_room = self.rooms[self.player.current_room]
        for room_item in current_room.items:
            if room_item.requires and item_to_use.name in room_item.requires:
                print(f"You used {item_to_use.name} on {room_item.name}.")
                print(f"{room_item.name} opens or changes in some way.")
                current_room.items.remove(room_item)
                return
        print(f"You used the {item_to_use.name}, but nothing happened.")

#end saatviks code
    def command_help(self, args):
        print("Available commands:")
        for cmd in self.commands:
            print(f"- {cmd}")

    def command_exit(self, args):
        print("Exiting game.")
        self.running = False

if __name__ == "__main__":
    player = Player("Player1", rooms)
    intro = Cutscene([
        "You wake up in a spaceship, disoriented and confused.",
        "You look around and see a crate in the center of the room."
    ], speed=0.05, lineDelay=2)
    intro.play()

    game = Game(player, rooms)
    game.start()

## End Dhyan's Code
