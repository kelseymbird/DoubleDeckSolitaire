import tkinter as tk
from tkinter import messagebox
import random

# ----- Card and Game Logic -----
SUITS = ["♠","♥","♦","♣"]
RANKS = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
PILE_LABELS = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
DEAL_LABELS = ["A","2","3","4","5","6","7","8","9","10","DRAW","J","Q","K"]

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
    def __repr__(self):
        return f"{self.rank}{self.suit}"

class Game:
    def __init__(self, root):
        self.root = root
        self.root.title("Double Deck Solitaire")

        # Piles and foundations
        self.piles = {label: [] for label in PILE_LABELS}
        self.foundations = {f"{s}{direction}": [] for s in SUITS for direction in ("_up", "_down")}
        self.draw_pile = []
        self.active_pile = None

        # GUI containers
        self.pile_frames = {}
        self.foundation_frames = {}
        self.board_frame = tk.Frame(root)
        self.board_frame.pack()
        self.found_frame = tk.Frame(root)
        self.found_frame.pack(pady=10)

        self.create_deck()
        self.deal()
        self.render_foundations()
        self.render_piles()

    def create_deck(self):
        self.deck = [Card(s,r) for _ in range(2) for s in SUITS for r in RANKS]
        random.shuffle(self.deck)

    def deal(self):
        while self.deck:
            for label in DEAL_LABELS:
                if not self.deck: break
                card = self.deck.pop(0)
                if label == "DRAW":
                    # Cards dealt to the DRAW label go directly into the draw pile.
                    self.draw_pile.append(card)
                    continue

                self.piles[label].append(card)

                # Extra rules for DRAW pile
                if label in ["7","10","K"] and self.deck:
                    self.draw_pile.append(self.deck.pop(0))
                if card.rank=="A" and label!="DRAW":
                    for _ in range(2):
                        if self.deck: self.draw_pile.append(self.deck.pop(0))
                if label!="DRAW" and card.rank==label and self.deck:
                    self.draw_pile.append(self.deck.pop(0))

    # ----- GUI Rendering -----
    def get_playable_indices(self, label):
        pile = self.piles[label]
        if not pile:
            return set()
        playable = {0}
        if label == self.active_pile:
            playable.add(len(pile) - 1)
        return playable

    def render_piles(self):
        for frame in self.pile_frames.values():
            frame.destroy()
        self.pile_frames = {}

        for i, label in enumerate(DEAL_LABELS):
            frame = tk.Frame(self.board_frame, bd=2, relief="ridge")
            frame.grid(row=i//7, column=i%7, padx=5, pady=5)
            tk.Label(frame, text=label).pack()

            if label == "DRAW":
                tk.Button(frame, text=f"Click to Draw ({len(self.draw_pile)})", width=14, command=self.draw_from_draw).pack(pady=6)
                self.pile_frames[label] = frame
                continue

            playable_indices = self.get_playable_indices(label)
            if not self.piles[label]:
                tk.Label(frame, text="(empty)", fg="gray").pack()
            for idx, card in enumerate(self.piles[label]):
                btn = tk.Button(frame, text=str(card), width=6, command=lambda l=label, i=idx: self.play_card(l,i))
                if idx not in playable_indices:
                    btn.config(state="disabled")
                btn.pack()
            self.pile_frames[label] = frame

    def render_foundations(self):
        for frame in self.foundation_frames.values():
            frame.destroy()
        self.foundation_frames = {}
        for i, s in enumerate(SUITS):
            for j, dir in enumerate(["_up","_down"]):
                frame = tk.Frame(self.found_frame, bd=2, relief="ridge", width=60, height=80)
                frame.grid(row=j, column=i, padx=5)
                f_stack = self.foundations[s+dir]
                label = f_stack[-1] if f_stack else ("A→K" if dir=="_up" else "K→A")
                tk.Label(frame, text=str(label)).pack()
                self.foundation_frames[s+dir] = frame

    # ----- Game Logic -----
    def draw_from_draw(self):
        if not self.draw_pile:
            messagebox.showinfo("DRAW Empty","DRAW pile is empty!")
            self.check_game_end()
            return
        card = self.draw_pile.pop()
        self.active_pile = card.rank
        self.piles[self.active_pile].append(card)
        self.render_piles()

    def play_card(self, pile_label, idx):
        if idx not in self.get_playable_indices(pile_label):
            messagebox.showinfo("Invalid Move", "That card is not currently playable.")
            return

        card = self.piles[pile_label][idx]
        if self.can_move_to_foundation(card):
            self.move_to_foundation(card)
            del self.piles[pile_label][idx]
            self.render_piles()
            self.render_foundations()
            self.check_game_end()
        else:
            messagebox.showinfo("Invalid Move","Cannot move card to foundation!")

    def can_move_to_foundation(self, card):
        up = self.foundations[card.suit+"_up"]
        down = self.foundations[card.suit+"_down"]
        if (not up and card.rank=="A") or (up and self.next_rank(up[-1].rank)==card.rank):
            return True
        if (not down and card.rank=="K") or (down and self.prev_rank(down[-1].rank)==card.rank):
            return True
        return False

    def move_to_foundation(self, card):
        up = self.foundations[card.suit+"_up"]
        down = self.foundations[card.suit+"_down"]
        if (not up and card.rank=="A") or (up and self.next_rank(up[-1].rank)==card.rank):
            up.append(card)
        else:
            down.append(card)

    def next_rank(self, rank): return RANKS[RANKS.index(rank)+1] if rank!="K" else None
    def prev_rank(self, rank): return RANKS[RANKS.index(rank)-1] if rank!="A" else None

    def check_game_end(self):
        all_complete = all(len(self.foundations[s+"_up"])==13 and len(self.foundations[s+"_down"])==13 for s in SUITS)
        no_moves = all(
            all(not self.can_move_to_foundation(self.piles[label][idx]) for idx in self.get_playable_indices(label))
            for label in self.piles
        )
        
        if all_complete:
            messagebox.showinfo("You Win!","Congratulations! All foundations complete!")
        elif no_moves and not self.draw_pile:
            messagebox.showinfo("Game Over","No valid moves left and DRAW pile is empty!")

# ----- Run the game -----
if __name__=="__main__":
    root = tk.Tk()
    game = Game(root)
    root.mainloop()
