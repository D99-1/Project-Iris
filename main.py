import time

class Player:
    def __init__(self, name, rooms):
        self.name = name
        self.rooms = rooms
        self.current_room = "rover_pad"
        self.inventory = []
        self.facing_direction = "north"
        self.moves = []
        self.flags = {
            "comms_unlocked": False,
        }

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

            if new_room_name == "communications_room" and not self.flags.get("comms_unlocked"):
                code = input("A keypad flashes: ENTER ACCESS CODE >> ").strip().upper()
                if code == "EMBER-IRIS-8924":
                    print("Access granted. The door slides open.")
                    self.flags["comms_unlocked"] = True
                else:
                    print("Access denied. The door remains sealed.")
                    return
            elif new_room_name == "exit_hatch" and not room.name == "open_area":
                confirm = input("You are about to exit the rover. Are you sure? (yes/no) ").strip().lower()
                if confirm != "yes":
                    print("You decide to stay inside the rover.")
                    return
                else:
                    cutscene = Cutscene([
                        "Depressurising the airlock...",
                    ], speed=0.5, lineDelay=1)
                    cutscene.play()
                    self.current_room = "open_area"
                    self.facing_direction = "west"
                    self.moves.append(self.current_room)
                    print(self.rooms[self.current_room].description)
                    self.flags["three_move_cutscene_played"] = True
                    return
            elif new_room_name == "exit_hatch" and room.name == "open_area":
                confirm = input("You are about to enter the spaceship. Are you sure? (yes/no) ").strip().lower()
                if confirm != "yes":
                    print("You decide to stay outside.")
                    return
                else:
                    cutscene = Cutscene([
                        "Entering the spaceship...",
                    ], speed=0.5, lineDelay=1)
                    cutscene.play()
                    self.current_room = "exit_hatch"
                    self.facing_direction = "east"
                    self.moves.append(self.current_room)
                    print(self.rooms[self.current_room].description)
                    return
            elif new_room_name == "habitat_sleeping_quarters" and not self.flags.get("sleeping_quarters_visited"):
                cutscene = Cutscene([
                    "You enter the habitat's sleeping quarters.",
                    "It looks like a mess, the wall is missing.",
                    "Outside, you see the ruins of the habitat."
                ], speed=0.04, lineDelay=2)
                cutscene.play()
                self.flags["sleeping_quarters_visited"] = True
            elif new_room_name == "habitat_storage_room" and not self.flags.get("storage_room_visited"):
                cutscene = Cutscene([
                    "You enter the habitat's storage room.",
                    "It's not storing anything anymore",
                    "just the dusty remains of what used to be here.",
                    "The wall no longer exists",
                    "Outside, you see a pile of debris."
                ], speed=0.04, lineDelay=2)
                cutscene.play()
                self.flags["storage_room_visited"] = True

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
    "sticky_note": Item("Sticky Note", "A dusty yellow sticky-note, stuck onto the side panel near Dr. Halberg's seat", interactions={'inspect': "\"don't forget the password!\nEMBER-IRIS-8924\n     — Halberg\""}),
    "mre": Item("MRE's", "A pack of MRE's (Meals Ready to Eat).", interactions={"inspect": "These will keep you fed for a while."}),
    "old_air_filter": Item("Old Air Filter", "An old air filter, covered in dust.", interactions={"inspect": "It looks like it hasn't been used in a long time."}),
    "empty_containers": Item("Empty Containers", "A few empty containers, likely used for storage.", interactions={"inspect": "They are empty and useless now."}),
    "north_metal_scraps": Item("Metal Scraps", "A pile of metal scraps", interactions={"inspect": "These could be useful for repairs."}),
    "sealed_briefcase": Item("Sealed Briefcase", "Sealed Black Briefcase with an embossed US government seal",interactions={"inspect": "It seems to be locked with a rusty padlock. No key in sight."},requires=["Rusty Spanner"],contains=["iris"]),
    "rusty_spanner": Item("Rusty Spanner", "A rusty spanner.", interactions={"inspect": "It might still be useful for some repairs."}),
    "torn_clothing": Item("Torn Clothing", "A pile of ripped clothes", interactions={"inspect": "This doesn't look like it's useful anymore."}),
    "iris": Item("Iris", "A small large black box with a small screen and a few buttons. It seems to be some kind of device.", interactions={"inspect":"There is a handbook attached to the device. It reads:\n\nIRIS: STRICTLY CONFIDENTIAL\n\nFOR AUTHORISED PERSONNEL ONLY\n\nDO NOT ATTEMPT TO ACCESS WITHOUT PROPER AUTHORISATION\n\n-------------------------\n\nIRIS is a self-regulating, life support system designed to preserve designated subjects indefinitely in the event of catastrophic failure in hostile environments.\n\nOnce activated, IRIS *will* take care of you, however IRIS remains a prototype at this stage\n\nThere are known tendencies for IRIS to emit unintended UHF signals, known to cause interterstrial interference and potentially attract extraterrestrial attention.\n\nAT THIS POINT IN TIME, IRIS IS NOT TO BE ACTIVATED, RISK OF FAILURE REMAINS TOO HIGH."}),
    "headphones": Item("Headphones", "A good old pair of wired headphones.", interactions={"inspect": "These were probably used to communicate with earth."}),
    "radio": Item("Radio", "A small radio device, likely used for communication.", interactions={"inspect": "It seems to be broken, doesn't look like it's in a repairable condition."}),
    "emergency_beacon": Item("Emergency Beacon", "A small emergency beacon, used to signal for help.", interactions={"inspect": "This could be useful to call back to Earth for help. You need a working antenna to activate this."}),
    "broken_antenna": Item("Broken Antenna", "A broken antenna, likely used for communication.", interactions={"inspect": "It seems to be damaged beyond repair. This would've been used to activate the emergency beacon."}),
}
rooms = {
    "center": Room("center", "You are in the center of the ship.", {"west": "communications_room", "east": "storage_room", "north": "control_room", "south": "engine_room"}, []),
    "communications_room": Room("communications_room", "You are in the communications room.", {"east": "center", "south": "exit_hatch"}, [items["headphones"], items["broken_antenna"], items["radio"], items["emergency_beacon"]]),
    "storage_room": Room("storage_room", "You are in the storage room.", {"west": "center", "south": "rover_launch_bay"}, []), 
    "control_room": Room("control_room", "You are in the control room.", {"south": "center"}, [items["sticky_note"]]),
    "engine_room": Room("engine_room", "You are in the engine room.", {"north": "center", "west": "exit_hatch", "east": "rover_launch_bay"}, []),
    "rover_launch_bay": Room("rover_launch_bay", "You are in the rover launch bay.", {"north": "storage_room", "west": "engine_room"}, []),
    "exit_hatch": Room("exit_hatch", "You are at the exit hatch.", {"north": "communications_room", "east": "engine_room"}, []),
    "open_area": Room("open_area", "You roam free on the lands of Mars.", {"north": "north_debris", "west": "habitat_air_lock", "south": "south_debris", "east": "exit_hatch"}, []),
    "south_debris": Room("south_debris", "You are in the south debris area.", {"north": "open_area", "west": "habitat_sleeping_quarters"}, []),
    "north_debris": Room("north_debris", "You are in the north debris area.", {"south": "open_area", "west": "habitat_storage_room", "east": "old_rover_pad"}, [items["mre"], items["old_air_filter"], items["north_metal_scraps"], items["empty_containers"], items["sealed_briefcase"], items["torn_clothing"], items["rusty_spanner"]]),
    "habitat_air_lock": Room("habitat_air_lock", "You are in the habitat air lock.", {"north": "habitat_irrigation_area", "south": "habitat_sleeping_quarters"}, []),
    "habitat_irrigation_area": Room("habitat_irrigation_area", "You are in the habitat irrigation area.", {"north": "habitat_storage_room", "south": "habitat_air_lock"}, []),
    "habitat_sleeping_quarters": Room("habitat_sleeping_quarters", "You are in the habitat sleeping quarters.", {"north": "habitat_air_lock", "east": "south_debris"}, []),
    "habitat_storage_room": Room("habitat_storage_room", "You are in the habitat storage room.", {"south": "habitat_irrigation_area", "east": "north_debris"}, []),
    "rover_pad": Room("rover_pad", "You are in the rover pad.", {"north": "rover_launch_bay"}, []),
    "old_rover_pad": Room("old_rover_pad", "You are in the old rover pad.", {"west": "north_debris"}, []),
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
            if len(self.player.moves) == 3 and not self.player.flags.get("three_move_cutscene_played"):
                Cutscene([
                    "The dust storm sure hit hard...",
                    "You should probably check if something is damaged outside,",
                    "try exiting through the airlock."
                ], speed=0.03, lineDelay=2).play()
                self.player.flags["three_move_cutscene_played"] = True
            

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
