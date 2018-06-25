#!/bin/python
# -*- coding: utf-8 -*-

import sys
import random
import copy
import time

class Game(object):

  # gameplay mechanics
  PIECES = 9
  AREAS = 3
  MURDERERS = 2

  DELAY = 0.1

  def __init__(self, players, murderers, areas):
    # create areas where pieces can move to each turn
    self.areas = [[] for i in range(areas)]

    # create the deck
    self.pieces = [i for i in range(players)]

    # shuffle the deck
    random_pieces = copy.copy(self.pieces)
    random.shuffle(random_pieces)

    # draw the player from the deck
    self.player = random_pieces.pop()

    # draw the number of murderers from the deck
    self.murderers = [random_pieces.pop() for i in range(murderers)]

    # visitors make up the remainder of the deck
    self.visitors = random_pieces

    # record the number of turns it takes for the game
    self.turn = 1

  def slow_print(self, txt, speed = 1.0):
    """
    Slowly prints text character-by-character
    """
    for c in txt:
      sys.stdout.write(c)
      sys.stdout.flush()
      time.sleep(Game.DELAY * speed)


  def print_intro(self):
    print ""
    print "*** ::::::::::::::::::::::::::::::::::::: ***"
    print "*** ::                                 :: ***"
    print "*** ::   // VULCAN MURDER MYSTERY //   :: ***"
    print "*** ::     .====.        ___ .==.   o  :: ***"
    print "*** ::     |::::|  .===, |:| |::| =/ \=:: ***"
    print "*** :: .___|::::|  |:::| |:| |::| | 0 |:: ***"
    print "*** :: |:::|====|  |:::|-----|::| |:::|:: ***"
    print "*** :: |===|::::|  |===::::::|::| |___|:: ***"
    print "*** :: ![]:!:[]:!  ! []::::x:|[]| || ||:: ***"
    print "*** ::---------------------------------:: ***"
    print "*** ::                                 :: ***"
    print "*** ::  --  --  --  --  --  --  --  -- :: ***"
    print "*** ::                                 :: ***"
    print "*** ::---------------------------------:: ***"
    print "*** ::::::::::::::::::::::::::::::::::::: ***"
    print ""
    self.narrate("Upon Red Mountain sits Vulcan, a statue to honor Birmingham's ironworkers.")
    x = {1: 'a murderer has',
         2: 'a duo of murderers have',
         3: 'a trio of murderers have'}
    n = Game.MURDERERS
    txt = x[n] if n in x.keys() else '%d murderers have' % n
    self.narrate("On this night, %s taken advantage of the winter storm" % txt)
    self.narrate("...and are murdering visitors one by one")
    self.narrate("You are the Doctor, and alone can you keep the murderers from killing")
    self.narrate("Here is the sequence of play:")
    self.narrate("  - The game is played in rounds")
    self.narrate("  - Each round consists of the visitors moving to different areas")
    self.narrate("  - Next, the murderers move to an area")
    self.narrate("  - You then move to an area")
    self.narrate("  - The power goes out, and the murderers pick one victim")
    self.narrate("  - You can then pick anyone to accuse of murder")
    self.narrate("  - The game continues until all visitors are dead or all murderers are found")

  def print_board(self):
    """
    Prints the state of the board (all of the areas
    and who is in them currently)
    """
    for area_idx in range(len(self.areas)):
      area = self.areas[area_idx]
      txt = ", ".join([str(i) for i in area])
      print "*** AREA %2d: %s" % (area_idx+1, txt)

  def print_turn_header(self):
    s = "\n"
    s += "*** ::::::::::::::\n"
    s += "*** :: TURN %3d ::\n" % self.turn
    s += "*** ::::::::::::::\n"
    self.slow_print(s, 0.1)
    
  def narrate(self, text):
    """
    Slowly narrates some text for the player
    """
    self.slow_print(">>>")
    time.sleep(Game.DELAY * 0.5)
    self.slow_print(" CHRONICLEUR: " + text + "\n", 0.5)
    time.sleep(Game.DELAY)

  def random_area(self):
    """
    Returns an index to a random area on the board
    """
    return random.randint(0, len(self.areas)-1)

  def clear_areas(self):
    """
    Clears all pieces from the areas on the board. This
    should be done at the start of each turn
    """
    for i in range(len(self.areas)):
      self.areas[i] = []

  def place(self, area, piece):
    """
    Place a piece in an area - this doesn't remove them from
    any other area, fyi
    """
    self.areas[area].append(piece)
    self.areas[area].sort()

  def place_visitors(self):
    """
    Place the visitors in the different areas of the
    board. This is done randomly
    """
    self.clear_areas()
    for x in self.visitors:
      self.place(self.random_area(), x)

  def place_murderers(self):
    """
    Places weremurderers in the different areas. The weremurderers
    will try to be placed where they can do the most damage
    or cause confusion without alerting the player.

    For now we will just randomly place weremurderers.
    """
    for x in self.murderers:
      area = random.randint(0, len(self.areas)-1)
      self.place(area, x)

  def is_murderer_in_area(self, area):
    for w in self.murderers:
      if w in area:
        return True
    return False

  def build_kill_list(self):
    """
    Gets the list of all pieces that the murderers can kill. This
    means any pieces that are in the same area as a murderer.

    Note that the player prevents the murderers from killing. So
    we reject areas where the player is present.

    We store the pieces with a 'kill score' that is calculated
    to disguise the murderers' identity.
    """
    kill_list = []
    for area in self.areas:
      if not self.player in area and self.is_murderer_in_area(area):
        local_kill_list = []
        for piece in area:
          if not piece in self.murderers:
            local_kill_list.append(piece)
        score = len(local_kill_list)
        for piece in local_kill_list:
          kill_list.append((score, piece))
    return kill_list

  def best_kill(self):
    """
    Gets the best kill to be made. Returns -1 if no kill can be made.
    """
    kill_list = self.build_kill_list()
    kill_list.sort()
    kill_list.reverse()
    if len(kill_list) == 0:
      return -1
    else:
      best_score = kill_list[0][0]
      best_scores = filter(lambda x: x[0] == best_score, kill_list)
      random.shuffle(best_scores)
      return best_scores[0][1]

  def kill(self, piece):
    """
    Kills a piece, removing them from the game
    """
    self.remove_from_list(self.pieces, piece)
    self.remove_from_list(self.murderers, piece)
    self.remove_from_list(self.visitors, piece)

  def remove_from_list(self, l, x):
    """
    Ensures element 'x' is not in list 'l'
    """
    if x in l: l.remove(x)

  def game_won(self):
    return self.murderers == []

  def game_lost(self):
    return self.visitors == []

  def suspects(self, piece):
    """
    Takes a look at the board and determines all
    possible suspects for a 'victim' piece
    """
    for area in self.areas:
      if piece in area:
        result = copy.copy(area)
        result.remove(piece)
        return result
    return []

  def play_turn(self):
    """
    Plays a turn of the game
    """
    self.print_turn_header()
    self.turn += 1
    self.place_visitors()
    self.place_murderers()
    self.print_board()
    self.narrate("Doctor, which area do you want to protect?")
    area = self.get_input_in(range(1,Game.AREAS+1))
    self.place(area-1, self.player)
    to_kill = self.best_kill()
    if to_kill == -1:
      self.narrate("The group has not dwindled in number.")
    else:
      self.narrate("✞ %d has met their fate ✞" % to_kill)
      suspects = self.suspects(to_kill)
      self.narrate("I suspect " + ", ".join([str(i) for i in suspects]))
      self.kill(to_kill)
    self.narrate("Given the facts, would you like to execute anyone?")
    accuse_str = self.get_input_in(["y", "n"])
    if accuse_str == "y":
      self.narrate("Very well, which soul shall be reaped?")
      options = copy.copy(self.visitors)
      options.extend(self.murderers)
      options.sort()
      accuse = self.get_input_in(options)
      self.narrate("✞ %d has been strangled to death ✞" % (accuse))
      self.kill(accuse)

  def get_input_in(self, options):
    """
    Gets input from the user for a given set of options.
    """
    opts = ", ".join([str(i) for i in options])
    decoder_fun = lambda x: next(opt for opt in options if str(opt) == x)
    return self.get_input(decoder_fun, opts)

  def get_input(self, decoder_fun, opts = ""):
    """
    Gets input from the user via decoder function, and will re-ask
    if the decoder function raises an exception
    """
    result = None
    while result == None:
      raw = ""
      if opts == "":
        raw = raw_input("input: ")
      else:
        raw = raw_input("input [%s]: " % opts)
      try:
        result = decoder_fun(raw)
      except:
        self.narrate("I don't quite catch your meaning?")
        result = None
    return result
     
if __name__ == '__main__':
  game = Game(Game.PIECES, Game.MURDERERS, Game.AREAS)
  game.print_intro()
  while True:
    game.play_turn()
    if game.game_lost():
      game.narrate("You're devoured alone by the murderers. No one hears your scream.")
      game.narrate("You lost after %d turns" % (game.turn))
      break
    elif game.game_won():
      game.narrate("You've choked out the lives of all the murderers. Good job.")
      game.narrate("And it only took %d turns!" % (game.turn))
      visitors = Game.PIECES - Game.MURDERERS - 1
      game.narrate("You saved %d out of %d visitors, not counting yourself." % (len(game.visitors), visitors))
      break
