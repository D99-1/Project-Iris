import time

class Player:
    def __init__(self, name, rooms):
        self.name = name
        self.rooms = rooms
        self.current_room = "rover_pad"
        self.inventory = []
        self.facing_direction = "north"
        self.moves = []

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
            self.moves.append(self.current_room)
        else:
            print(f"Cannot move {direction} from {self.current_room}")

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
                print(f"- {item.name}")

class Item:
    def __init__(self, name, description, requires=None, interactions=None, contains=None):
        self.name = name
        self.description = description
        self.requires = requires
        self.interactions = interactions or {}
        self.contains = contains or []

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
        print("\n\n")

class GameState:
    def __init__(self):
        self.current_act = 1
        self.log_accessed = False
        self.iris_found = False
        self.iris_activated = False
        self.turns_since_iris = 0
        self.has_solar_parts = False
        self.has_beacon = False

items = {
    "halberg_log": Item("halberg_log", "Encrypted log from Dr. Halberg.", interactions={"inspect": "Iris isn’t dormant. It’s sending something. Somewhere."}),
    "iris_container": Item("iris_container", "A sealed container labeled: BLACK IRIS – US DEPARTMENT OF DEFENSE.", interactions={"inspect": "UNTESTED SYSTEM – DO NOT ACTIVATE WITHOUT PRIMARY FAILURE\nSIGNAL PROTOCOL: ALPHA-VOID"}),
    "solar_parts": Item("solar_parts", "Spare solar panel components salvaged from the debris."),
    "beacon": Item("beacon", "A jury-rigged emergency beacon from an old rover."),
}

rooms = {
    "center": Room("center", "You are in the center of the ship.", {"west": "communications_room", "east": "storage_room", "north": "control_room", "south": "engine_room"}, []),
    "communications_room": Room("communications_room", "You are in the communications room.", {"east": "center", "south": "exit_hatch"}, []),
    "storage_room": Room("storage_room", "You are in the storage room.", {"west": "center", "south": "rover_launch_bay"}, []), 
    "control_room": Room("control_room", "You are in the control room.", {"south": "center"}, [items["halberg_log"]]),
    "engine_room": Room("engine_room", "You are in the engine room.", {"north": "center", "west": "exit_hatch", "east": "rover_launch_bay"}, []),
    "rover_launch_bay": Room("rover_launch_bay", "You are in the rover launch bay.", {"north": "storage_room", "west": "engine_room"}, []),
    "exit_hatch": Room("exit_hatch", "You are at the exit hatch.", {"north": "communications_room", "east": "engine_room"}, []),
    "open_area": Room("open_area", "You roam free on the lands of Mars.", {"north": "north_debris", "west": "habitat_air_lock", "south": "south_debris", "east": "exit_hatch"}, []),
    "south_debris": Room("south_debris", "You are in the south debris area.", {"north": "open_area", "west": "habitat_sleeping_quarters", "east": "rover_pad"}, [items["solar_parts"]]),
    "north_debris": Room("north_debris", "You are in the north debris area.", {"south": "open_area", "west": "habitat_storage_room", "east": "old_rover_pad"}, [items["iris_container"]]),
    "habitat_air_lock": Room("habitat_air_lock", "You are in the habitat air lock.", {"north": "open_area", "south": "habitat_sleeping_quarters"}, []),
    "habitat_irrigation_area": Room("habitat_irrigation_area", "You are in the habitat irrigation area.", {"north": "habitat_storage_room", "south": "habitat_air_lock"}, []),
    "habitat_sleeping_quarters": Room("habitat_sleeping_quarters", "You are in the habitat sleeping quarters.", {"north": "habitat_air_lock", "east": "south_debris"}, []),
    "habitat_storage_room": Room("habitat_storage_room", "You are in the habitat storage room.", {"south": "habitat_irrigation_area", "east": "north_debris"}, []),
    "rover_pad": Room("rover_pad", "You are in the rover pad.", {"north": "rover_launch_bay"}, []),
    "old_rover_pad": Room("old_rover_pad", "You are in the old rover pad.", {"west": "north_debris"}, [items["beacon"]]),
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
            "inspect": self.command_inspect,
        }

    def start(self):
        print(self.rooms[self.player.current_room].description)
        while self.running:
            command_input = input("\n> ").strip().lower()
            self.handle_command(command_input)
            if len(player.moves) == 3:
                Cutscene([
                    "The dust storm sure hit hard...",
                    "You should probably check if something is damaged outside,",
                    "try exiting through the airlock."
                ], speed=0.03, lineDelay=2).play()

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
            print("Use what on what?")
            return
        if "on" in args:
            on_idx = args.index("on")
            item_name = " ".join(args[:on_idx])
            target_name = " ".join(args[on_idx+1:])
        else:
            print("Syntax: use <item> on <target>")
            return

        tool = next((i for i in self.player.inventory if i.name.lower() == item_name), None)
        if not tool:
            print(f"You don't have an item named '{item_name}'.")
            return

        room = self.rooms[self.player.current_room]
        target = next((i for i in room.items if i.name.lower() == target_name), None)
        in_inventory = False
        if not target:
            target = next((i for i in self.player.inventory if i.name.lower() == target_name), None)
            in_inventory = bool(target)

        if not target:
            print(f"There is no '{target_name}' here or in your inventory.")
            return

        if target.requires and tool.name in target.requires:
            print(f"You used {tool.name} on {target.name}.")
            print(f"{target.name} opens, revealing:")
            for content_name in target.contains:
                content = items[content_name]
                if in_inventory:
                    self.player.inventory.append(content)
                    print(f"- {content.name} (added to inventory)")
                else:
                    room.items.append(content)
                    print(f"- {content.name} (dropped in the room)")
            if in_inventory:
                self.player.inventory.remove(target)
            else:
                room.items.remove(target)
            return

        print(f"Using {tool.name} on {target.name} did nothing.")

#end saatviks code
    def command_help(self, args):
        print("Available commands:")
        for cmd in self.commands:
            print(f"- {cmd}")

    def command_exit(self, args):
        print("Exiting game.")
        self.running = False
#saatviks code 
    def command_inspect(self, args):       
        if not args:            
            print("Inspect what?")
            return
        item_name = " ".join(args)
        item = next((i for i in self.player.inventory if i.name.lower() == item_name), None)
        if not item:
            room = self.rooms[self.player.current_room]
            item = next((i for i in room.items if i.name.lower() == item_name), None)
        if not item:
            print(f"There is no '{item_name}' here or in your inventory.")
            return
        print(item.inspect())
#end saatviks code 

if __name__ == "__main__":
    player = Player("Player1", rooms)
    intro = Cutscene([
    "Sol 37. The storm hit harder than anything predicted.",
    "The habitat collapsed. You're the only one who made it to the rover in time.",
    "Power is out. Oxygen is dropping. You have to get back inside..."
    ], speed=0.04, lineDelay=2)
    intro.play()

    game = Game(player, rooms)
    game.start()

## End Dhyan's Code 
