import time
import random
import difflib

class GameError(Exception):
    pass

class Colors:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

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
            "old_rover_alive": True,
            "has_working_antenna": False,
            "three_move_cutscene_played": False,
        }

    def get_absolute_direction(self, facing, relative_direction):
        try:
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
                if relative_direction in ["north", "south", "east", "west"]:
                    return relative_direction
                raise GameError(f"Invalid direction: {relative_direction}")
            
            directions = ["north", "east", "south", "west"]
            offsets = {"front": 0, "right": 1, "back": 2, "left": -1}
            
            if facing not in directions:
                raise GameError(f"Invalid facing direction: {facing}")
            
            facing_index = directions.index(facing)
            abs_index = (facing_index + offsets[relative_direction]) % 4
            return directions[abs_index]
            
        except Exception as e:
            raise GameError(f"Direction calculation failed: {str(e)}")

    def move(self, direction):
        try:
            if not direction:
                raise GameError("Please specify a direction to move")
                
            room = self.rooms.get(self.current_room)
            if not room:
                raise GameError(f"Current room '{self.current_room}' not found")
            
            absolute_direction = self.get_absolute_direction(self.facing_direction, direction.lower().strip())

            if absolute_direction not in room.exits:
                raise GameError(f"Cannot move {absolute_direction} from {self.current_room}")
                
            new_room_name = room.exits[absolute_direction]

            # Handle special room cases
            if new_room_name == "communications_room" and not self.flags.get("comms_unlocked"):
                code = input(f"{Colors.YELLOW}A keypad flashes: ENTER ACCESS CODE >> {Colors.RESET}").strip().upper()
                if code == "EMBER-IRIS-8924":
                    print(f"{Colors.GREEN}Access granted. The door slides open.{Colors.RESET}")
                    self.flags["comms_unlocked"] = True
                else:
                    print(f"{Colors.RED}Access denied. The door remains sealed.{Colors.RESET}")
                    return
                    
            elif new_room_name == "exit_hatch":
                action = "exit" if room.name != "open_area" else "enter"
                confirm = input(f"You are about to {action} the rover. Are you sure? (yes/no) ").strip().lower()
                if confirm != "yes":
                    print(f"You decide to stay {'inside' if room.name != 'open_area' else 'outside'}.")
                    return
                
                cutscene_text = ["Depressurising the airlock..."] if room.name != "open_area" else ["Entering the spaceship..."]
                Cutscene(cutscene_text, speed=0.5, lineDelay=1).play()
                
                self.current_room = "open_area" if room.name != "open_area" else "exit_hatch"
                self.facing_direction = "west" if room.name != "open_area" else "east"
                self.moves.append(self.current_room)
                print(self.rooms[self.current_room].description)
                
                if room.name != "open_area":
                    self.flags["three_move_cutscene_played"] = True
                return
                
            elif new_room_name == "old_rover_pad" and self.flags.get("old_rover_alive"):
                Cutscene([
                    "You approach the Old Rover.",
                    "It looks battered, but its antenna is intact.",
                    "You can hear a faint hum as you get closer."
                ], speed=0.04, lineDelay=2).play()
                Cutscene(old_rover.dialogue, speed=0.04, lineDelay=2).play()
                old_rover.interaction()

            # Update player position
            self.current_room = new_room_name
            self.facing_direction = absolute_direction
            print(self.rooms[self.current_room].description)
            self.moves.append(self.current_room)
            
        except GameError as e:
            print(f"Movement error: {str(e)}")
        except Exception as e:
            print(f"Unexpected movement error: {str(e)}")

    def look(self):
        try:
            room = self.rooms.get(self.current_room)
            if not room:
                raise GameError("Current room not found")
                
            print(room.description)
            if room.items:
                print("You see the following items:")
                for item in room.items:
                    print(f"- {Colors.CYAN}{item.name}{Colors.RESET}")
            else:
                print("There seems to be no items in this room.")
                
        except GameError as e:
            print(f"Look error: {str(e)}")
        except Exception as e:
            print(f"Unexpected look error: {str(e)}")

    def view_inventory(self): 
        try:
            if not self.inventory:
                print("You currently have no items with you.")
            else:
                print("You are carrying:")
                for item in self.inventory: 
                    print(f"- {item.name}")
                    
        except Exception as e:
            print(f"Error viewing inventory: {str(e)}")

class Item:
    def __init__(self, name, description, requires=None, interactions=None, contains=None):
        self.name = name
        self.description = description
        self.requires = requires or []
        self.interactions = interactions or {}
        self.contains = contains or []

    def inspect(self):
        try:
            return f"{Colors.YELLOW}{self.interactions.get('inspect', self.description)}{Colors.RESET}"
        except Exception:
            return f"{Colors.YELLOW}{self.description}{Colors.RESET}"

class Room:
    def __init__(self, name, description, exits, items=None):
        self.name = name
        self.description = description
        self.exits = exits
        self.items = items or []

class Cutscene:
    def __init__(self, text=None, speed=0.03, lineDelay=1):
        self.text = text if isinstance(text, list) else [str(text)] if text else []
        self.speed = max(0.01, min(float(speed), 0.1))
        self.lineDelay = max(0, float(lineDelay))

    def play(self):
        try:
            print("\n")
            for line in self.text:
                colored_line = f"{Colors.BLUE}{line}{Colors.RESET}"
                for char in str(colored_line):
                    print(char, end='', flush=True)
                    time.sleep(self.speed)
                time.sleep(self.lineDelay)
            print("\n")
        except Exception:
            print("\n<Cutscene playback failed>\n")

class NPC:
    def __init__(self, name, description, dialogue, interaction):
        self.name = name
        self.description = description
        self.dialogue = dialogue
        self.interaction = interaction

def interact_old_rover(player):
    try:
        lines = [
            f"{Colors.CYAN}The Old Rover lowers its voice module to a faint whisper.{Colors.RESET}",
            f"{Colors.GREEN}Old Rover: You need the antenna, don't you?{Colors.RESET}",
            f"{Colors.GREEN}Old Rover: If you take it... I will go dark.{Colors.RESET}",
            f"{Colors.GREEN}Old Rover: But maybe... maybe it's time.{Colors.RESET}",
            "",
            f"{Colors.YELLOW}What do you do?{Colors.RESET}",
            f"{Colors.BLUE}1. Harvest the antenna{Colors.RESET}",
            f"{Colors.BLUE}2. Leave Old Rover intact{Colors.RESET}"
        ]
        Cutscene(lines, speed=0.04, lineDelay=1.5).play()

        while True:
            choice = input("> ").strip()
            if choice == "1":
                Cutscene([
                    "You reach out slowly, disconnecting the antenna.",
                    "Old Rover: I knew this day would come.",
                    "The lights on its sensors fade.",
                    "You now have the beacon antenna.",
                    "Try using the emergency beacon in the communications room."
                ], speed=0.04, lineDelay=1.5).play()
                player.flags["old_rover_alive"] = False
                player.inventory.append(items["antenna"])
                break
            elif choice == "2":
                Cutscene([
                    "You step back. The Old Rover's sensors flash briefly.",
                    "The rover gets back to its exploration, as it has done for so long."
                ], speed=0.04, lineDelay=1.5).play()
                player.flags["old_rover_alive"] = True
                break
            else:
                print("Invalid choice. Please enter 1 or 2")
    except Exception:
        print("Rover interaction failed")

items = { 
    "sticky_note": Item("Sticky Note", "A dusty yellow sticky-note", 
                       interactions={'inspect': "\"don't forget the password!\nEMBER-IRIS-8924\n      — Halberg\""}),
    "mre": Item("MRE's", "A pack of MRE's (Meals Ready to Eat).", 
               interactions={"inspect": "These will keep you fed for a while."}),
    "old_air_filter": Item("Old Air Filter", "An old air filter, covered in dust.", 
                          interactions={"inspect": "It looks like it hasn't been used in a long time."}),
    "empty_containers": Item("Empty Containers", "A few empty containers", 
                            interactions={"inspect": "They are empty and useless now."}),
    "north_metal_scraps": Item("Metal Scraps", "A pile of metal scraps", 
                              interactions={"inspect": "These could be useful for repairs."}),
    "sealed_briefcase": Item("Sealed Briefcase", "Sealed Black Briefcase with an embossed US government seal", 
                            interactions={"inspect": "It seems to be locked with a rusty padlock. You'll need something with leverage to break it open."}, 
                            requires=["Rusty Spanner"], 
                            contains=["iris"]),
    "rusty_spanner": Item("Rusty Spanner", "A rusty spanner.", 
                         interactions={"inspect": "It might still be useful for some repairs."}),
    "torn_clothing": Item("Torn Clothing", "A pile of ripped clothes", 
                         interactions={"inspect": "This doesn't look like it's useful anymore."}),
    "iris": Item("Iris", "A small black box with a small screen and a few buttons.", 
                interactions={"inspect":"The handbook is still attached. It reads:\n\nIRIS: STRICTLY CONFIDENTIAL\n\nFOR AUTHORISED PERSONNEL ONLY\n\nDO NOT ATTEMPT TO ACCESS WITHOUT PROPER AUTHORISATION\n\n-------------------------\n\nIRIS is a self-regulating, life support system designed to preserve designated subjects indefinitely in the event of catastrophic failure in hostile environments.\n\nOnce activated, IRIS *will* take care of you, however IRIS remains a prototype at this stage\n\nThere are known tendencies for IRIS to emit unintended UHF signals, known to cause interterrestrial interference and potentially attract extraterrestrial attention.\n\nAT THIS POINT IN TIME, IRIS IS NOT TO BE ACTIVATED, RISK OF FAILURE REMAINS TOO HIGH.\n\nA small, handwritten note is taped below the empty power slot: 'Requires a standard 250-volt portable power cell to initiate.'"}),
    "unstable_power_cell": Item("Unstable Power Cell", "A portable 250-volt power cell. It feels warm to the touch and hums faintly.", 
                               interactions={"inspect": "The casing is cracked, and a warning label reads: 'CAUTION: Unstable. Risk of UHF signal leakage.' This must be the power source for IRIS."}),
    "headphones": Item("Headphones", "A good old pair of wired headphones.", 
                      interactions={"inspect": "These were probably used to communicate with earth."}),
    "radio": Item("Radio", "A small radio device", 
                 interactions={"inspect": "It seems to be broken, doesn't look like it's in a repairable condition."}),
    "emergency_beacon": Item("Emergency Beacon", "A small emergency beacon", 
                            interactions={"inspect": "This could be useful to call back to Earth for help. You need a working antenna to activate this."}),
    "broken_antenna": Item("Broken Antenna", "A broken antenna", 
                          interactions={"inspect": "It seems to be damaged beyond repair. This would've been used to activate the emergency beacon."}),
    "communications_manual": Item("Communications Manual", "A manual for the communications system.", 
                                interactions={"inspect":"Communications Manual: \n\nThis manual contains information on how to operate the communications system, including troubleshooting steps for common issues:\n\n To activate general communications, press the green 'Power' button on the console and tune frequency to 145.800 MHz, fine-tune as required.\n\n For emergency communications, use the dedicated emergency beacon.\nAttach the portable antenna to the beacon and hold the red button for 5 seconds, a blue light should activate.\nOnce the singal is received by earth, a green light will activate.\nThe beacon will display a red light if an antenna is not attached.\n\n\nThe light is red indeed, you need an antenna.\nThe antenna that's laying around here is broken. Where can you possibly find a working antenna?\nMaybe the old rovers that are active from the previous mission may have some.\nThe old mission was North of our spaceship."}),
    "antenna": Item("Antenna", "A working antenna", 
                   interactions={"inspect": "This antenna is in good condition and can be used to activate the emergency beacon."}),
    "flickering_datapad": Item("Flickering Datapad", "A datapad with a cracked screen", 
                              interactions={"inspect": "The battery is almost dead. The screen shows a single, corrupted log entry: 'Sol 36: ...strange readings from the northern ridge. It's not geological. Re-calibrating the deep-scan array...' The screen dies."}),
    "oily_rag": Item("Oily Rag", "A greasy rag left on a console.", 
                    interactions={"inspect": "It smells strongly of hydraulic fluid. It's covered in grime."}),
    "nutrient_paste_crate": Item("Nutrient Paste Crate", "A large crate of emergency rations.", 
                               interactions={"inspect": "A manifest is taped to the side: 'CONTENTS: 150x Nutrient Paste Tubes. FLAVOR: Gray.' The crate is sealed shut."}),
    "small_wrench": Item("Small Wrench", "A small, adjustable wrench lying on the floor.", 
                        interactions={"inspect": "It's a standard-issue 10mm wrench. It seems too small to be useful for any of the heavy machinery here."}),
    "warning_placard": Item("Warning Placard", "A faded warning placard bolted to the wall.", 
                           interactions={"inspect": "The placard reads: 'CAUTION: Airlock door must remain sealed during dust storms. In case of emergency, communications manual is located in the comms room.'"}),
    "strange_rock": Item("Strange Rock", "A peculiar-looking rock, different from the surrounding regolith.", 
                        interactions={"inspect": "The rock has an unusual, almost metallic sheen. It's probably just a high concentration of iron ore."}),
    "scorched_panel": Item("Scorched Panel", "A scorched panel from the habitat's outer wall.", 
                          interactions={"inspect": "This panel looks like it was hit by a massive power surge. The circuits are completely fried."}),
    "withered_plant": Item("Withered Plant", "The desiccated remains of a small plant in a pot.", 
                          interactions={"inspect": "This was once someone's attempt to grow something green on Mars. It has long since died."}),
    "halbergs_datapad": Item("Halberg's Datapad", "A personal datapad lying half-buried under a torn blanket.", 
                            interactions={"inspect": "It's Dr. Halberg's datapad. The final entry is open:\n\n'Sol 37. The storm is too much. I had to lock down the comms room, but I'm always forgetting that blasted code. I stuck a note somewhere obvious near my seat in the control room. If IRIS is our only hope, I pray the briefcase is still in the north debris field where I left it. The old spanner should be there too. Someone has to make it.'"}),
    "soil_kit": Item("Soil Analysis Kit", "A soil analysis kit, dropped on the floor.", 
                    interactions={"inspect": "The last analysis reads: 'Sample 42. High iron-oxide content. Trace organic compounds... anomalous reading detected. Recommend further investigation.'"}),
    "old_rover_tracks": Item("Old Rover Tracks", "Deep tracks in the dust.", 
                            interactions={"inspect": "These tracks lead away from the pad and into the vast Martian landscape. The Old Rover has been busy."}),
}

rooms = {
    "center": Room("center", "You are in the center of the ship, a nexus connecting the main sections.", 
                  {"west": "communications_room", "east": "storage_room", "north": "control_room", "south": "engine_room"}, 
                  [items["flickering_datapad"]]),
    "communications_room": Room("communications_room", "You are in the communications room. Consoles are dark and silent.", 
                              {"east": "center", "south": "exit_hatch"}, 
                              [items["headphones"], items["broken_antenna"], items["radio"], items["emergency_beacon"], items["communications_manual"]]),
    "storage_room": Room("storage_room", "You are in the storage room. Shelves are mostly empty.", 
                        {"west": "center", "south": "rover_launch_bay"}, 
                        [items["nutrient_paste_crate"], items["empty_containers"]]), 
    "control_room": Room("control_room", "You are in the control room. The main viewscreen is cracked.", 
                        {"south": "center"}, 
                        [items["sticky_note"]]),
    "engine_room": Room("engine_room", "You are in the engine room. The low hum of dormant machinery fills the air. Tucked away behind a coolant pipe, you see something.", 
                       {"north": "center", "west": "exit_hatch", "east": "rover_launch_bay"}, 
                       [items["unstable_power_cell"], items["oily_rag"]]),
    "rover_launch_bay": Room("rover_launch_bay", "You are in the rover launch bay. A fine layer of red dust covers everything.", 
                            {"north": "storage_room", "west": "engine_room"}, 
                            []),
    "exit_hatch": Room("exit_hatch", "You are at the exit hatch. The outer door is sealed tight.", 
                      {"north": "communications_room", "east": "engine_room"}, 
                      [items["warning_placard"]]),
    "open_area": Room("open_area", "You roam free on the lands of Mars. The red desert stretches to the horizon.", 
                     {"north": "north_debris", "west": "habitat_air_lock", "south": "south_debris", "east": "exit_hatch"}, 
                     [items["strange_rock"]]),
    "south_debris": Room("south_debris", "You are in the south debris area, amidst twisted metal from the habitat.", 
                        {"north": "open_area", "west": "habitat_sleeping_quarters"}, 
                        [items["scorched_panel"], items["torn_clothing"]]),
    "north_debris": Room("north_debris", "You are in the north debris area. This seems to be where supplies were offloaded.", 
                        {"south": "open_area", "west": "habitat_storage_room", "east": "old_rover_pad"}, 
                        [items["mre"], items["old_air_filter"], items["north_metal_scraps"], items["sealed_briefcase"], items["rusty_spanner"]]),
    "habitat_air_lock": Room("habitat_air_lock", "You are in the habitat air lock. The inner door hangs ajar.", 
                           {"north": "habitat_irrigation_area", "south": "habitat_sleeping_quarters"}, 
                           []),
    "habitat_irrigation_area": Room("habitat_irrigation_area", "You are in the habitat irrigation area. A row of empty planters lines the wall.", 
                                  {"north": "habitat_storage_room", "south": "habitat_air_lock"}, 
                                  [items["withered_plant"], items["soil_kit"]]),
    "habitat_sleeping_quarters": Room("habitat_sleeping_quarters", "You are in the habitat sleeping quarters. A gaping hole in the wall reveals the red landscape.", 
                                    {"north": "habitat_air_lock", "east": "south_debris"}, 
                                    [items["halbergs_datapad"]]),
    "habitat_storage_room": Room("habitat_storage_room", "You are in the habitat storage room. Most of the contents have been sucked out through a tear in the hull.", 
                               {"south": "habitat_irrigation_area", "east": "north_debris"}, 
                               []),
    "rover_pad": Room("rover_pad", "You are in the rover pad, your only sanctuary from the storm.", 
                     {"north": "rover_launch_bay"}, 
                     [items["small_wrench"]]),
    "old_rover_pad": Room("old_rover_pad", "You are at the old rover pad. It looks like it hasn't been used for years.", 
                         {"west": "north_debris"}, 
                         [items["old_rover_tracks"]]),
}

old_rover = NPC(
    name="Old Rover",
    description=f"{Colors.GREEN}A battered exploration unit with an intact antenna. It hums faintly as you approach. {Colors.RESET}",
    dialogue=[
        f"{Colors.GREEN}Old Rover: I remember this crater. Dust storms used to dance here like children. {Colors.RESET}",
        f"{Colors.GREEN}Old Rover: Most of my memory banks are corrupted... but I remember the stars. {Colors.RESET}",
        f"{Colors.GREEN}Old Rover: My antenna still works... keeps me connected to the sky. {Colors.RESET}"
    ],
    interaction=lambda player: interact_old_rover(player)  # Fixed player reference
)

class Game:
    def __init__(self, player, rooms):
        self.player = player
        self.rooms = rooms
        self.running = True
        self.commands = {
            # Movement
            "move": self.command_move,
            "m": self.command_move,
            "go": self.command_move,
            "g": self.command_move,
            
            # Observation
            "look": self.command_look,
            "l": self.command_look,
            "whereami": self.command_look,
            "exits": self.command_exits,
            "ex": self.command_exits,
            
            # Inventory
            "inventory": self.command_inventory,
            "inv": self.command_inventory,
            "i": self.command_inventory,
            "e": self.command_inventory,
            
            # Interaction
            "take": self.command_take,
            "t": self.command_take,
            "pickup": self.command_take,
            "get": self.command_take,
            "use": self.command_use,
            "u": self.command_use,
            "inspect": self.command_inspect,
            "ins": self.command_inspect,
            "examine": self.command_inspect,
            "exam": self.command_inspect,
            
            # System
            "help": self.command_help,
            "h": self.command_help,
            "?": self.command_help,
            "quit": self.command_exit,
            "q": self.command_exit,
            "exit": self.command_exit
        }
        self.pending_command = None

    def start(self):
        try:
            print(self.rooms[self.player.current_room].description)
            while self.running:
                try:
                    command_input = input("\n> ").strip()
                    if not command_input:
                        continue
                    
                    # Handle pending command continuation
                    if self.pending_command:
                        # If user enters a base command, override pending command
                        if command_input.split()[0] in self.commands:
                            self.pending_command = None
                            self.handle_command(command_input)
                        else:
                            full_command = f"{self.pending_command} {command_input}"
                            self.pending_command = None
                            self.handle_command(full_command)
                    else:
                        self.handle_command(command_input)
                    
                    # Trigger 3-move cutscene
                    if len(self.player.moves) == 3 and not self.player.flags.get("three_move_cutscene_played"):
                        Cutscene([
                            "The dust storm sure hit hard... ",
                            "You should probably check if something is damaged outside, ",
                            "try exiting through the airlock. "
                        ], speed=0.03, lineDelay=2).play()
                        self.player.flags["three_move_cutscene_played"] = True
                        
                except Exception as e:
                    print(f"Command error: {str(e)}")
                    
        except Exception as e:
            print(f"Critical game error: {str(e)}")
            print("Game session terminated unexpectedly.")


    def handle_command(self, command_input):
        if not command_input:
            return

        try:
            parts = command_input.split()
            command = parts[0].lower()
            args = parts[1:]

            if command in self.commands:
                self.commands[command](args)
            else:
                # Spelling suggestion for commands
                suggestions = difflib.get_close_matches(command, self.commands.keys(), n=1, cutoff=0.6)
                if suggestions:
                    print(f"{Colors.RED}Command not found. Did you mean '{Colors.YELLOW}{suggestions[0]}{Colors.RED}'?{Colors.RESET}")
                else:
                    raise GameError(f"Unknown command: '{command}'. Type 'help' for available commands.")
                    
        except GameError as e:
            print(f"Error: {str(e)}")
        except Exception as e:
            print(f"Unexpected command error: {str(e)}")

    def command_move(self, args):
        try:
            if not args:
                self.pending_command = "move"
                raise GameError("Move where? (e.g., north, left)")
                
            self.player.move(" ".join(args))
        except GameError as e:
            print(f"Move error: {str(e)}")
        except Exception as e:
            print(f"Unexpected move error: {str(e)}")

    def command_look(self, args):
        try:
            self.player.look()
        except Exception as e:
            print(f"Look command failed: {str(e)}")

    def command_inventory(self, args):
        try:
            self.player.view_inventory()
        except Exception as e:
            print(f"Inventory command failed: {str(e)}")


    def command_take(self, args):
        try:
            if not args:
                self.pending_command = "take"
                raise GameError("Take what?")
                
            item_name = " ".join(args)
            room = self.rooms.get(self.player.current_room)
            if not room:
                raise GameError("Current room not found")
            
            # Get available items for spellcheck
            available_items = [item.name.lower() for item in room.items]
            inventory_items = [item.name.lower() for item in self.player.inventory]
            
            # Check if item exists
            item = next((i for i in room.items if i.name.lower() == item_name.lower()), None)
            if not item:
                # Spellcheck suggestion
                suggestions = difflib.get_close_matches(item_name, available_items, n=1, cutoff=0.5)
                if suggestions:
                    raise GameError(f"No item named '{item_name}' found. Did you mean '{suggestions[0]}'?")
                raise GameError(f"No item named '{item_name}' found here")
                
            # Check if item already in inventory
            if any(i.name.lower() == item_name.lower() for i in self.player.inventory):
                raise GameError(f"You already have {item.name}")
                
            self.player.inventory.append(item)
            room.items.remove(item)
            print(f"You picked up the {item.name}.")
            
        except GameError as e:
            print(f"Take error: {str(e)}")
        except Exception as e:
            print(f"Unexpected take error: {str(e)}")


    def command_use(self, args):
        try:
            if not args:
                self.pending_command = "use"
                raise GameError("Use what? (e.g., spanner on briefcase)")
                
            if "on" not in args:
                self.pending_command = "use " + " ".join(args)
                raise GameError("Use on what? (syntax: use <item> on <target>)")
                
            on_idx = args.index("on")
            item_name = " ".join(args[:on_idx])
            target_name = " ".join(args[on_idx+1:])

            tool = next((i for i in self.player.inventory if i.name.lower() == item_name.lower()), None)
            if not tool:
                raise GameError(f"You don't have an item named '{item_name}'")

            # Handle IRIS activation
            if tool.name == "Unstable Power Cell" and target_name.lower() == "iris":
                target_in_inventory = next((i for i in self.player.inventory if i.name.lower() == "iris"), None)
                if target_in_inventory:
                    self.trigger_iris_ending()
                    return
                else:
                    raise GameError("You need to have the IRIS device in your inventory to use the power cell on it.")

            room = self.rooms[self.player.current_room]
            target = next((i for i in room.items if i.name.lower() == target_name.lower()), None)
            in_inventory = False
            if not target:
                target = next((i for i in self.player.inventory if i.name.lower() == target_name.lower()), None)
                in_inventory = bool(target)

            if not target:
                raise GameError(f"There is no '{target_name}' here or in your inventory")

            # Emergency Beacon win condition
            if tool.name == "Antenna" and target.name == "Emergency Beacon":
                Cutscene([
                    "You attach the antenna onto the emergency beacon.",
                    "The red error light turns blue and then... it turns green.",
                    "A faint buzzing sound confirms the signal is broadcasting.",
                    "Now it's just a matter of waiting...",
                    "",
                    "Hours pass.",
                    "Then... a sound. A voice crackles through the comms.",
                    "\"We received your signal. Help is on the way.\"",
                    "You're going home."
                ], speed=0.04, lineDelay=2).play()
                print("=== GAME END ===")
                self.running = False
                return

            # Handle item requirements
            if target.requires and tool.name in target.requires:
                print(f"You used {tool.name} on {target.name}.")
                if target.contains:
                    print(f"{target.name} opens, revealing:")
                    for content_name in target.contains:
                        content = items.get(content_name)
                        if not content:
                            continue
                        self.player.inventory.append(content)
                        print(f"- {content.name} (added to inventory)")
                    # Remove the used-up container
                    if in_inventory:
                        self.player.inventory.remove(target)
                    else:
                        room.items.remove(target)
                return

            print(f"Using {tool.name} on {target.name} did nothing.")
            
        except GameError as e:
            print(f"Use error: {str(e)}")
        except Exception as e:
            print(f"Unexpected use error: {str(e)}")

    def trigger_iris_ending(self):
        Cutscene([
            "You slot the humming power cell into the IRIS device.",
            "The screen flickers to life, bathing you in a cold, blue light.",
            "IRIS: 'Primary power detected. Life support protocol IRIS now active.'",
            "IRIS: 'Calibration required. Please respond to prompts to stabilize system core.'",
            "IRIS: 'Failure to comply may result in... unintended consequences.'"
        ], speed=0.04, lineDelay=2).play()

        calibration_success = True
        prompts = {
            "First, reroute auxiliary power. Do you route to [1] shields or [2] life-support?": "2",
            "Next, align the gravimetric field. Set frequency to [1] 77.3 GHz or [2] 99.1 GHz?": "1",
            "Finally, purge the coolant system. Do you [1] vent externally or [2] recycle coolant?": "1"
        }

        for prompt, correct_answer in prompts.items():
            print(f"IRIS: '{prompt}'")
            choice = input("> ").strip()
            if choice != correct_answer:
                calibration_success = False
                Cutscene(["IRIS: 'Calibration failed. System integrity compromised.'"]).play()
                break
            else:
                Cutscene(["IRIS: '...Acknowledged.'"], speed=0.01, lineDelay=0.5).play()
        
        if calibration_success:
            Cutscene(["IRIS: 'Calibration successful. System is stable.'"]).play()

        Cutscene([
            "The device hums louder, its light intensifying.",
            "IRIS: 'Final activation sequence initiated.'",
            "IRIS: 'Warning: Prototype stabilization field may have unpredictable results.'",
            "A countdown appears on the screen: 5... 4... 3..."
        ], speed=0.04, lineDelay=1.5).play()

        print("\nWhat do you do?")
        print("1. Trust the device. Let IRIS activate.")
        
        has_spanner = any(item.name == "Rusty Spanner" for item in self.player.inventory)
        if has_spanner:
            print("2. This is a mistake! Smash the device with the spanner!")

        while True:
            choice = input("> ").strip()
            if choice == '1':
                extraterrestrial_chance = 0.80 if not calibration_success else 0.55
                if random.random() < extraterrestrial_chance:
                    Cutscene([
                        "IRIS: 'Activation complete. Emitting preservation field...'",
                        "The blue light pulses... but the device emits a high-pitched whine.",
                        "IRIS: 'WARNING! UNKNOWN UHF INTERFERENCE DETECTED! SOURCE... APPROACHING!'",
                        "The spaceship's hull groans, not from the wind, but from a shadow falling over it.",
                        "You look out the viewport to see something vast and dark descending from the Martian sky.",
                        "IRIS attracted the wrong kind of attention.",
                        "\n=== ENDING: UNEXPECTED RESCUE ==="
                    ], speed=0.04, lineDelay=2).play()
                else:
                    Cutscene([
                        "IRIS: 'Activation complete. Biostabilization commencing.'",
                        "A wave of cold energy washes over you. Your muscles lock, your breathing stops, but you feel no panic.",
                        "Your vision is filled with a serene, endless blue light.",
                        "You are safe. Preserved. Waiting for a rescue that may never come.",
                        "You are immortal on the red planet. Forever.",
                        "\n=== ENDING: THE LONELY IMMORTAL ==="
                    ], speed=0.04, lineDelay=2).play()
                break
            elif choice == '2' and has_spanner:
                Cutscene([
                    "You grip the rusty spanner and swing with all your might!",
                    "Sparks erupt as metal screams against plastic.",
                    "IRIS: 'ERROR! ERROR! SUBJECT NON-COMPLIANT! CATASTROPHIC-'",
                    "The light from the device dies with a final, pathetic flicker.",
                    "Silence returns to the rover. You are alone again, the silence deeper than before.",
                    "You chose your own fate, for better or worse.",
                    "\n=== ENDING: A DEFIANT FATE ==="
                ], speed=0.04, lineDelay=2).play()
                break
            else:
                print("Invalid choice. Please enter 1" + (" or 2" if has_spanner else ""))

        self.running = False

    def command_help(self, args):
        try:
            print(f"{Colors.BOLD}Available commands:{Colors.RESET}")
            print(f"{Colors.CYAN}-------------------{Colors.RESET}")
            
            # Grouped command explanations
            help_sections = {
                "Movement": [
                    ("move/go/g/m <direction>", "Navigate in a direction (north/south/left/etc)"),
                    ("exits/ex", "Show available exits from current location")
                ],
                "Observation": [
                    ("look/l/whereami", "View current location description"),
                    ("inspect/ins/exam/i <item>", "Examine an item closely")
                ],
                "Inventory": [
                    ("inventory/inv/e/i", "View your carried items"),
                    ("take/t/pickup <item>", "Pick up an item"),
                    ("use/u <item> on <target>", "Use an item on something")
                ],
                "System": [
                    ("help/h/?", "Show this help screen"),
                    ("quit/q/exit", "Exit the game")
                ]
            }
            
            # Print grouped commands
            for category, commands in help_sections.items():
                print(f"\n{Colors.BOLD}{category}:{Colors.RESET}")
                for cmd, desc in commands:
                    print(f"  {Colors.GREEN}{cmd}{Colors.RESET}")
                    print(f"      {desc}")
            
            print(f"\n{Colors.YELLOW}Examples:{Colors.RESET}")
            print(f"  {Colors.CYAN}m north{Colors.RESET} - Move north")
            print(f"  {Colors.CYAN}t spanner{Colors.RESET} - Pick up the rusty spanner")
            print(f"  {Colors.CYAN}i beacon{Colors.RESET} - Inspect the emergency beacon")
            print(f"  {Colors.CYAN}u antenna on beacon{Colors.RESET} - Use antenna on beacon")
            
        except Exception as e:
            print(f"Help command failed: {str(e)}")

    def command_exit(self, args):
        try:
            print("Exiting game.")
            self.running = False
        except Exception as e:
            print(f"Exit command failed: {str(e)}")

    def command_exits(self, args):
        try:
            room = self.rooms.get(self.player.current_room)
            if not room:
                raise GameError("Current room not found")
                
            if not room.exits:
                print("There are no visible exits from this location.")
            else:
                print("Available exits:")
                for direction, target in room.exits.items():
                    print(f"- {direction.capitalize()} to {target.replace('_', ' ').title()}")
        except Exception as e:
            print(f"Error showing exits: {str(e)}")

    def command_inspect(self, args):      
        try:
            if not args:          
                self.pending_command = "inspect"
                raise GameError("Inspect what?")
                
            item_name = " ".join(args)
            room = self.rooms.get(self.player.current_room)
            if not room:
                raise GameError("Current room not found")
            
            # Check inventory first
            item = next((i for i in self.player.inventory if i.name.lower() == item_name.lower()), None)
            # If not in inventory, check the room
            if not item:
                item = next((i for i in room.items if i.name.lower() == item_name.lower()), None)
            
            if not item:
                # Spellcheck for items
                available_items = [item.name.lower() for item in room.items]
                inventory_items = [item.name.lower() for item in self.player.inventory]
                all_items = available_items + inventory_items
                
                suggestions = difflib.get_close_matches(item_name, all_items, n=1, cutoff=0.5)
                if suggestions:
                    raise GameError(f"No item named '{item_name}' found. Did you mean '{suggestions[0]}'?")
                raise GameError(f"There is no '{item_name}' here or in your inventory")
                
            print(item.inspect())
            
        except GameError as e:
            print(f"Inspect error: {str(e)}")
        except Exception as e:
            print(f"Unexpected inspect error: {str(e)}")

def validate_game_world():
    """Comprehensive world validation"""
    try:
        room_names = set(rooms.keys())
        errors = []
        
        # Validate room exits
        for room_name, room in rooms.items():
            for direction, target_room in room.exits.items():
                if target_room not in room_names:
                    errors.append(f"Room '{room_name}' has invalid exit: '{target_room}' doesn't exist")
        
        # Validate item references
        for room in rooms.values():
            for item in room.items:
                if item.name not in [i.name for i in items.values()]:
                    errors.append(f"Room '{room.name}' contains unknown item: '{item.name}'")
        
        # Validate NPC existence
        if "old_rover" not in globals():
            errors.append("NPC 'Old Rover' is not defined")
        
        if errors:
            print(f"{Colors.RED}Game world errors:{Colors.RESET}")
            for error in errors:
                print(f"  - {error}")
            return False
                
        return True
    except Exception as e:
        print(f"{Colors.RED}Validation error: {str(e)}{Colors.RESET}")
        return False

if __name__ == "__main__":
    try:
        if not validate_game_world():
            print(f"{Colors.RED}Critical errors in game world setup. Exiting.{Colors.RESET}")
            exit(1)
            
        player = Player("Player1", rooms)
        intro = Cutscene([
        f"{Colors.BLUE}Sol 37. The storm hit harder than anything predicted.{Colors.RESET} ",
        f"{Colors.BLUE}The habitat collapsed. You're the only one who made it to the rover in time.{Colors.RESET} ",
        f"{Colors.RED}Power is out. Oxygen is dropping. You have to get inside...{Colors.RESET}"
        ], speed=0.04, lineDelay=2)
        intro.play()

        game = Game(player, rooms)
        game.start()
        
    except Exception as e:
        print(f"{Colors.RED}Fatal error: {str(e)}{Colors.RESET}")
        print(f"{Colors.RED}Game cannot start.{Colors.RESET}")