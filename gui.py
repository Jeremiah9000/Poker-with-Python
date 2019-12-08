import queue
import threading
from tkinter import *
import time
from PIL import ImageTk, Image


def ask_app(question, game=None):
    print("asking...")
    print(question)
    answer = None
    if game:
        game_info_q.put(game)
    game_event.wait()
    if not response_q.empty():
        answer = response_q.get()
    game_event.clear()

    return answer


class App(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.game_object = object

        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        list_of_frames = [StartPage, GamePage]

        for F in list_of_frames:
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.fresh = True
        self.show_frame(StartPage)

    def show_frame(self, context):
        frame = self.frames[context]
        print("waiting")
        if not self.fresh:
            time.sleep(0.1)
            frame.update(game_info_q.get())
        self.fresh = False
        frame.tkraise()


class StartPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        height = 500
        width = 800
        canvas = Canvas(self, height=height, width=width, bg="light green")
        canvas.pack()
        left_frame = Frame(canvas, bg='green', bd=5)
        left_frame.place(relx=0, rely=0, relwidth=0.5, relheight=1, anchor='nw')
        name_frame = Frame(left_frame, bg="light green", bd=5)
        name_frame.place(relx=0.5, rely=0.17, relwidth=0.9, relheight=0.7, anchor="n")
        self.p_entry_dict = {}
        for i in range(10):
            self.entry = Entry(name_frame, font=("Courier", 12), bd=3)
            self.p_entry_dict[f'player{i}_entry'] = self.entry
            x_off_set = i % 2
            y_off_set = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]
            self.entry.place(relx=(x_off_set*0.5), rely=(y_off_set[i]*0.2), relwidth=0.5, relheight=0.2)
        enter_player_label = Label(left_frame, text="Player Names:", font=("Courier", 12), bd=3)
        enter_player_label.place(relx=0.25, rely=0.07, relwidth=0.5, relheight=0.05)
        # self.entry.bind("<Return>", lambda _: self.button_click(self.entry.get()))

        right_frame = Frame(canvas, bg='green', bd=5)
        right_frame.place(relx=1, rely=0, relwidth=0.5, relheight=1, anchor='ne')
        self.sc_label = Label(right_frame, text="Starting Chips:", font=("Courier", 12), bd=3)
        self.sc_label.place(relx=0.25, rely=0.1, relwidth=0.5, relheight=0.05)
        self.sc_entry = Entry(right_frame, font=("Courier"), bd=3)
        self.sc_entry.place(relx=0.5, rely=0.17, relwidth=0.5, relheight=0.07, anchor="n")

        self.sb_label = Label(right_frame, text="Small-Blind Chips:", font=("Courier", 12), bd=3)
        self.sb_label.place(relx=0.25, rely=0.33, relwidth=0.5, relheight=0.05)
        self.sb_entry = Entry(right_frame, font=("Courier"), bd=3)
        self.sb_entry.place(relx=0.5, rely=0.4, relwidth=0.5, relheight=0.07, anchor="n")

        self.bb_label = Label(right_frame, text="Big-Blind Chips:", font=("Courier", 12), bd=3)
        self.bb_label.place(relx=0.25, rely=0.56, relwidth=0.5, relheight=0.05)
        self.bb_entry = Entry(right_frame, font=("Courier"), bd=3)
        self.bb_entry.place(relx=0.5, rely=0.63, relwidth=0.5, relheight=0.07, anchor="n")
        self.bb_entry.bind("<Return>", lambda _: self.button_click(self.p_entry_dict,
                                                                   controller))

        self.c_entry_dict = {'sc_entry': self.sc_entry, 'sb_entry': self.sb_entry, 'bb_entry': self.bb_entry}

        button = Button(right_frame, text="START", font=("Courier", 12), command=lambda: self.button_click(self.p_entry_dict, self.c_entry_dict, controller))
        button.place(relx=0.5, rely=0.9, relwidth=0.3, relheight=0.1, anchor="n")

    def button_click(self, p_entry_dict, c_entry_dict, controller):
        for key, value in p_entry_dict.items():
            p_entry_dict[key] = value.get()
        for key, value in c_entry_dict.items():
            p_entry_dict[key] = value.get()
        player_entry_list = []
        for value in p_entry_dict.values():
            player_entry_list.append(value)
        print(player_entry_list)
        player_entry_list = list(set(player_entry_list))
        for player in player_entry_list:
            if player == "":
                player_entry_list.remove(player)
        print(player_entry_list)
        if len(player_entry_list) < 2:
            print("not enough players")
            return
        for chips in c_entry_dict.values():
            try:
                chips = int(chips)
            except ValueError:
                print("Value Error")
                return
            if chips == "" or chips <= 0:
                print("chip entry error")
                return
        if not int(c_entry_dict['sc_entry']) > int(c_entry_dict['bb_entry']) > int(c_entry_dict['sb_entry']):
            print("chip entry error2 ")
            return
        setup = {
            "players": p_entry_dict,
            "chips": c_entry_dict
        }
        response_q.put(setup)
        game_event.set()
        controller.show_frame(GamePage)


class GamePage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        self.restart = False
        self.responses = []
        self.list_of_button_r = []
        height = 500
        width = 800
        canvas = Canvas(self, height=height, width=width, bg="light green")
        canvas.pack()

        left_frame = Frame(canvas, bg='green', bd=5)
        left_frame.place(relx=0, rely=0, relwidth=0.5, relheight=1, anchor='nw')
        name_frame = Frame(left_frame, bg="light green", bd=5)
        name_frame.place(relx=0.5, rely=0, relwidth=1, relheight=1, anchor="n")

        self.frame_p0 = Frame(name_frame, bd=3, relief="groove")
        self.frame_p0.place(relwidth=0.5, relheight=0.2)
        self.name_label_p0 = Label(self.frame_p0, font=("Courier", 10), bd=3)
        self.name_label_p0.place(relx=0, rely=0, relheight=(1 / 3), relwidth=0.38)
        self.chips_label_p0 = Label(self.frame_p0, font=("Courier", 10), bd=3)
        self.chips_label_p0.place(relx=0, rely=(1 / 3), relheight=(1 / 3), relwidth=0.38)
        self.cards_frame_p0 = Frame(self.frame_p0, bd=3, relief="groove")
        self.cards_frame_p0.place(relx=0.38, relheight=1, relwidth=0.62)
        self.card1_p0 = Label(self.cards_frame_p0)
        self.card1_p0.place(relwidth=0.5, relheight=1)
        self.card2_p0 = Label(self.cards_frame_p0)
        self.card2_p0.place(relx=0.5, relwidth=0.5, relheight=1)
        self.stake_label_p0 = Label(self.frame_p0, bd=1, relief="groove")
        self.stake_label_p0.place(relx=0, rely=(2 / 3), relheight=(1 / 3), relwidth=0.38)

        self.frame_p1 = Frame(name_frame, bd=3, relief="groove")
        self.frame_p1.place(relx=0.5, rely=0, relwidth=0.5, relheight=0.2)
        self.name_label_p1 = Label(self.frame_p1, font=("Courier", 10), bd=3)
        self.name_label_p1.place(relx=0, rely=0, relheight=(1 / 3), relwidth=0.38)
        self.chips_label_p1 = Label(self.frame_p1, font=("Courier", 10), bd=3)
        self.chips_label_p1.place(relx=0, rely=(1 / 3), relheight=(1 / 3), relwidth=0.38)
        self.cards_frame_p1 = Frame(self.frame_p1, bd=3, relief="groove")
        self.cards_frame_p1.place(relx=0.38, relheight=1, relwidth=0.62)
        self.card1_p1 = Label(self.cards_frame_p1)
        self.card1_p1.place(relwidth=0.5, relheight=1)
        self.card2_p1 = Label(self.cards_frame_p1)
        self.card2_p1.place(relx=0.5, relwidth=0.5, relheight=1)
        self.stake_label_p1 = Label(self.frame_p1, bd=1, relief="groove")
        self.stake_label_p1.place(relx=0, rely=(2 / 3), relheight=(1 / 3), relwidth=0.38)

        self.frame_p2 = Frame(name_frame, bd=3, relief="groove")
        self.frame_p2.place(relx=0, rely=0.2, relwidth=0.5, relheight=0.2)
        self.name_label_p2 = Label(self.frame_p2, font=("Courier", 10), bd=3)
        self.name_label_p2.place(relx=0, rely=0, relheight=(1 / 3), relwidth=0.38)
        self.chips_label_p2 = Label(self.frame_p2, font=("Courier", 10), bd=3)
        self.chips_label_p2.place(relx=0, rely=(1 / 3), relheight=(1 / 3), relwidth=0.38)
        self.cards_frame_p2 = Frame(self.frame_p2, bd=3, relief="groove")
        self.cards_frame_p2.place(relx=0.38, relheight=1, relwidth=0.62)
        self.card1_p2 = Label(self.cards_frame_p2)
        self.card1_p2.place(relwidth=0.5, relheight=1)
        self.card2_p2 = Label(self.cards_frame_p2)
        self.card2_p2.place(relx=0.5, relwidth=0.5, relheight=1)
        self.stake_label_p2 = Label(self.frame_p2, bd=1, relief="groove")
        self.stake_label_p2.place(relx=0, rely=(2 / 3), relheight=(1 / 3), relwidth=0.38)

        self.frame_p3 = Frame(name_frame, bd=3, relief="groove")
        self.frame_p3.place(relx=0.5, rely=0.2, relwidth=0.5, relheight=0.2)
        self.name_label_p3 = Label(self.frame_p3, font=("Courier", 10), bd=3)
        self.name_label_p3.place(relx=0, rely=0, relheight=(1 / 3), relwidth=0.38)
        self.chips_label_p3 = Label(self.frame_p3, font=("Courier", 10), bd=3)
        self.chips_label_p3.place(relx=0, rely=(1 / 3), relheight=(1 / 3), relwidth=0.38)
        self.cards_frame_p3 = Frame(self.frame_p3, bd=3, relief="groove")
        self.cards_frame_p3.place(relx=0.38, relheight=1, relwidth=0.62)
        self.card1_p3 = Label(self.cards_frame_p3)
        self.card1_p3.place(relwidth=0.5, relheight=1)
        self.card2_p3 = Label(self.cards_frame_p3)
        self.card2_p3.place(relx=0.5, relwidth=0.5, relheight=1)
        self.stake_label_p3 = Label(self.frame_p3, bd=1, relief="groove")
        self.stake_label_p3.place(relx=0, rely=(2 / 3), relheight=(1 / 3), relwidth=0.38)

        self.frame_p4 = Frame(name_frame, bd=3, relief="groove")
        self.frame_p4.place(relx=0, rely=0.4, relwidth=0.5, relheight=0.2)
        self.name_label_p4 = Label(self.frame_p4, font=("Courier", 10), bd=3)
        self.name_label_p4.place(relx=0, rely=0, relheight=(1 / 3), relwidth=0.38)
        self.chips_label_p4 = Label(self.frame_p4, font=("Courier", 10), bd=3)
        self.chips_label_p4.place(relx=0, rely=(1 / 3), relheight=(1 / 3), relwidth=0.38)
        self.cards_frame_p4 = Frame(self.frame_p4, bd=3, relief="groove")
        self.cards_frame_p4.place(relx=0.38, relheight=1, relwidth=0.62)
        self.card1_p4 = Label(self.cards_frame_p4)
        self.card1_p4.place(relwidth=0.5, relheight=1)
        self.card2_p4 = Label(self.cards_frame_p4)
        self.card2_p4.place(relx=0.5, relwidth=0.5, relheight=1)
        self.stake_label_p4 = Label(self.frame_p4, bd=1, relief="groove")
        self.stake_label_p4.place(relx=0, rely=(2 / 3), relheight=(1 / 3), relwidth=0.38)

        self.frame_p5 = Frame(name_frame, bd=3, relief="groove")
        self.frame_p5.place(relx=0.5, rely=0.4, relwidth=0.5, relheight=0.2)
        self.name_label_p5 = Label(self.frame_p5, font=("Courier", 10), bd=3)
        self.name_label_p5.place(relx=0, rely=0, relheight=(1 / 3), relwidth=0.38)
        self.chips_label_p5 = Label(self.frame_p5, font=("Courier", 10), bd=3)
        self.chips_label_p5.place(relx=0, rely=(1 / 3), relheight=(1 / 3), relwidth=0.38)
        self.cards_frame_p5 = Frame(self.frame_p5, bd=3, relief="groove")
        self.cards_frame_p5.place(relx=0.38, relheight=1, relwidth=0.62)
        self.card1_p5 = Label(self.cards_frame_p5)
        self.card1_p5.place(relwidth=0.5, relheight=1)
        self.card2_p5 = Label(self.cards_frame_p5)
        self.card2_p5.place(relx=0.5, relwidth=0.5, relheight=1)
        self.stake_label_p5 = Label(self.frame_p5, bd=1, relief="groove")
        self.stake_label_p5.place(relx=0, rely=(2 / 3), relheight=(1 / 3), relwidth=0.38)

        self.frame_p6 = Frame(name_frame, bd=3, relief="groove")
        self.frame_p6.place(relx=0, rely=0.6, relwidth=0.5, relheight=0.2)
        self.name_label_p6 = Label(self.frame_p6, font=("Courier", 10), bd=3)
        self.name_label_p6.place(relx=0, rely=0, relheight=(1 / 3), relwidth=0.38)
        self.chips_label_p6 = Label(self.frame_p6, font=("Courier", 10), bd=3)
        self.chips_label_p6.place(relx=0, rely=(1 / 3), relheight=(1 / 3), relwidth=0.38)
        self.cards_frame_p6 = Frame(self.frame_p6, bd=3, relief="groove")
        self.cards_frame_p6.place(relx=0.38, relheight=1, relwidth=0.62)
        self.card1_p6 = Label(self.cards_frame_p6)
        self.card1_p6.place(relwidth=0.5, relheight=1)
        self.card2_p6 = Label(self.cards_frame_p6)
        self.card2_p6.place(relx=0.5, relwidth=0.5, relheight=1)
        self.stake_label_p6 = Label(self.frame_p6, bd=1, relief="groove")
        self.stake_label_p6.place(relx=0, rely=(2 / 3), relheight=(1 / 3), relwidth=0.38)

        self.frame_p7 = Frame(name_frame, bd=3, relief="groove")
        self.frame_p7.place(relx=0.5, rely=0.6, relwidth=0.5, relheight=0.2)
        self.name_label_p7 = Label(self.frame_p7, font=("Courier", 10), bd=3)
        self.name_label_p7.place(relx=0, rely=0, relheight=(1 / 3), relwidth=0.38)
        self.chips_label_p7 = Label(self.frame_p7, font=("Courier", 10), bd=3)
        self.chips_label_p7.place(relx=0, rely=(1 / 3), relheight=(1 / 3), relwidth=0.38)
        self.cards_frame_p7 = Frame(self.frame_p7, bd=3, relief="groove")
        self.cards_frame_p7.place(relx=0.38, relheight=1, relwidth=0.62)
        self.card1_p7 = Label(self.cards_frame_p7)
        self.card1_p7.place(relwidth=0.5, relheight=1)
        self.card2_p7 = Label(self.cards_frame_p7)
        self.card2_p7.place(relx=0.5, relwidth=0.5, relheight=1)
        self.stake_label_p7 = Label(self.frame_p7, bd=1, relief="groove")
        self.stake_label_p7.place(relx=0, rely=(2 / 3), relheight=(1 / 3), relwidth=0.38)

        self.frame_p8 = Frame(name_frame, bd=3, relief="groove")
        self.frame_p8.place(relx=0, rely=0.8, relwidth=0.5, relheight=0.2)
        self.name_label_p8 = Label(self.frame_p8, font=("Courier", 10), bd=3)
        self.name_label_p8.place(relx=0, rely=0, relheight=(1 / 3), relwidth=0.38)
        self.chips_label_p8 = Label(self.frame_p8, font=("Courier", 10), bd=3)
        self.chips_label_p8.place(relx=0, rely=(1 / 3), relheight=(1 / 3), relwidth=0.38)
        self.cards_frame_p8 = Frame(self.frame_p8, bd=3, relief="groove")
        self.cards_frame_p8.place(relx=0.38, relheight=1, relwidth=0.62)
        self.card1_p8 = Label(self.cards_frame_p8)
        self.card1_p8.place(relwidth=0.5, relheight=1)
        self.card2_p8 = Label(self.cards_frame_p8)
        self.card2_p8.place(relx=0.5, relwidth=0.5, relheight=1)
        self.stake_label_p8 = Label(self.frame_p8, bd=1, relief="groove")
        self.stake_label_p8.place(relx=0, rely=(2 / 3), relheight=(1 / 3), relwidth=0.38)

        self.frame_p9 = Frame(name_frame, bd=3, relief="groove")
        self.frame_p9.place(relx=0.5, rely=0.8, relwidth=0.5, relheight=0.2)
        self.name_label_p9 = Label(self.frame_p9, font=("Courier", 10), bd=3)
        self.name_label_p9.place(relx=0, rely=0, relheight=(1 / 3), relwidth=0.38)
        self.chips_label_p9 = Label(self.frame_p9, font=("Courier", 10), bd=3)
        self.chips_label_p9.place(relx=0, rely=(1 / 3), relheight=(1 / 3), relwidth=0.38)
        self.cards_frame_p9 = Frame(self.frame_p9, bd=3, relief="groove")
        self.cards_frame_p9.place(relx=0.38, relheight=1, relwidth=0.62)
        self.card1_p9 = Label(self.cards_frame_p9)
        self.card1_p9.place(relwidth=0.5, relheight=1)
        self.card2_p9 = Label(self.cards_frame_p9)
        self.card2_p9.place(relx=0.5, relwidth=0.5, relheight=1)
        self.stake_label_p9 = Label(self.frame_p9, bd=1, relief="groove")
        self.stake_label_p9.place(relx=0, rely=(2 / 3), relheight=(1 / 3), relwidth=0.38)

        # self.entry.bind("<Return>", lambda _: self.button_click(self.entry.get()))

        right_frame = Frame(canvas, bg='green', bd=5)
        right_frame.place(relx=1, rely=0, relwidth=0.5, relheight=1, anchor='ne')

        self.cc_frame = Frame(right_frame, bd=2, relief="raised")
        self.cc_frame.place(relx=0, rely=0, relwidth=1, relheight=0.2)

        self.cc_1 = Label(self.cc_frame, bg="green")
        self.cc_1.place(relwidth=(.50 / 3), relheight=1)
        card_d1 = ImageTk.PhotoImage(
            Image.open("cards\default.png").resize((55, 85), Image.ANTIALIAS))
        self.cc_1.image = card_d1
        self.cc_1.configure(image=card_d1)

        self.cc_2 = Label(self.cc_frame, bg="green")
        self.cc_2.place(relx=(.50 / 3), relwidth=(.50 / 3), relheight=1)
        card_d2 = ImageTk.PhotoImage(
            Image.open("cards\default.png").resize((55, 85), Image.ANTIALIAS))
        self.cc_2.image = card_d2
        self.cc_2.configure(image=card_d2)

        self.cc_3 = Label(self.cc_frame, bg="green")
        self.cc_3.place(relx=(.50 / 3) * 2, relwidth=(.50 / 3), relheight=1)
        card_d3 = ImageTk.PhotoImage(
            Image.open("cards\default.png").resize((55, 85), Image.ANTIALIAS))
        self.cc_3.image = card_d3
        self.cc_3.configure(image=card_d3)

        self.cc_4 = Label(self.cc_frame, bg="green")
        self.cc_4.place(relx=(.50 / 3) * 3, relwidth=0.25, relheight=1)
        card_d4 = ImageTk.PhotoImage(
            Image.open("cards\default.png").resize((55, 85), Image.ANTIALIAS))
        self.cc_4.image = card_d4
        self.cc_4.configure(image=card_d4)

        self.cc_5 = Label(self.cc_frame, bg="green")
        self.cc_5.place(relx=((.50 / 3) * 3) + 0.25, relwidth=0.25, relheight=1)
        card_d5 = ImageTk.PhotoImage(
            Image.open("cards\default.png").resize((55, 85), Image.ANTIALIAS))
        self.cc_5.image = card_d5
        self.cc_5.configure(image=card_d5)

        self.pot_label = Label(right_frame, text="pot: ", font=("Courier", 12), bd=3)
        self.pot_label.place(relx=0, rely=0.2, relwidth=0.5, relheight=0.04)

        # self.dealer_label = Label(right_frame, text="dealer: ", font=("Courier", 12), bd=3)
        # self.dealer_label.place(relx=0, rely=0.28, relwidth=0.5, relheight=0.04)

        # self.sb_label = Label(right_frame, text="small-blind: ", font=("Courier", 12), bd=3)
        # self.sb_label.place(relx=0, rely=0.33, relwidth=0.5, relheight=0.04)

        # self.bb_label = Label(right_frame, text="big-blind: ", font=("Courier", 12), bd=3)
        # self.bb_label.place(relx=0, rely=0.38, relwidth=0.5, relheight=0.04)

        self.action_frame = Frame(right_frame, bd=2, relief="raised", bg="green")
        self.action_frame.place(rely=0.5, relwidth=1, relheight=0.5)
        self.action_cover_label = Label(self.action_frame, bg="light green")
        self.action_cover_label.place(relx=0, rely=0, relheight=1, relwidth=1)

        self.actor_label = Label(self.action_frame, text="Actor: ", font=("Courier", 12), bd=3)
        self.actor_label.place(relwidth=1, relheight=0.06)

        self.new_round_label = Label(self.action_frame, text="New Round?", font=("Courier", 9), bd=3)
        self.new_round_label.place(relx=0.8, rely=0.05, relheight=0.1, relwidth=0.2)
        self.button_y = Button(self.action_frame, text="Yes", command=lambda: self.action_input("yes"))
        self.button_y.place(relx=0.8, rely=0.15, relheight=0.1, relwidth=0.2)
        self.button_n = Button(self.action_frame, text="No", command=lambda: self.action_input("no"))
        self.button_n.place(relx=0.8, rely=0.25, relheight=0.1, relwidth=0.2)

        self.raise_entry = Entry(self.action_frame, font=("Courier", 9), bd=3)
        self.raise_entry.place(relx=0, rely=1, relheight=0.12, relwidth=0.22, anchor="sw")
        self.raise_button = Button(self.action_frame, text="RAISE", font=("Courier", 9), bd=3,
                                   command=lambda: self.action_input(self.raise_entry.get()))
        self.raise_button.place(relx=0.22, rely=1, relheight=0.12, relwidth=0.22, anchor="sw")

        self.winner_label = Label(self.action_frame, font=("Courier", 12), bd=3)
        self.winner_label.place(relx=0, rely=(1 / 3), relwidth=0.75, relheight=0.3)

    def update(self, game):
        self.new_round_label.lower(self.action_cover_label)
        self.button_y.lower(self.action_cover_label)
        self.button_n.lower(self.action_cover_label)
        self.raise_entry.lower(self.action_cover_label)
        self.raise_button.lower(self.action_cover_label)
        self.winner_label.lower(self.action_cover_label)
        if self.restart:
            card1 = ImageTk.PhotoImage(Image.open(str("cards\default.png")).resize((55, 85), Image.ANTIALIAS))
            self.cc_1.image = card1
            self.cc_1.configure(image=card1)

            card1 = ImageTk.PhotoImage(Image.open(str("cards\default.png")).resize((55, 85), Image.ANTIALIAS))
            self.cc_2.image = card1
            self.cc_2.configure(image=card1)

            card1 = ImageTk.PhotoImage(Image.open(str("cards\default.png")).resize((55, 85), Image.ANTIALIAS))
            self.cc_3.image = card1
            self.cc_3.configure(image=card1)

            card1 = ImageTk.PhotoImage(Image.open(str("cards\default.png")).resize((55, 85), Image.ANTIALIAS))
            self.cc_4.image = card1
            self.cc_4.configure(image=card1)

            card1 = ImageTk.PhotoImage(Image.open(str("cards\default.png")).resize((55, 85), Image.ANTIALIAS))
            self.cc_5.image = card1
            self.cc_5.configure(image=card1)
            self.restart = False
        if game['round_over']:
            time.sleep(0.3)
            self.new_round_label.lift(self.action_cover_label)
            self.button_y.lift(self.action_cover_label)
            self.button_n.lift(self.action_cover_label)
            winners = []
            scores = []
            players_not_out = []
            for player in game['players']:
                if not player.isOut:
                    players_not_out.append(player)
            for player in players_not_out:
                if player.win:
                    winners.append(player)
                    scores.append(player.score)
            print(f"gui thinks winners are: {winners}")
            print(f"and thinks scores are: {scores}")
            if scores == [[]]:
                self.winner_label["text"] = "Winner: " + str(winners)
            else:
                try:
                    for player in players_not_out:
                        if player.win:
                            if player.score == max(scores):
                                self.winner_label["text"] = "Winner: " + str(winners) + "\n" + player.score_interpretation
                except IndexError:
                    pass
            self.winner_label.lift(self.action_cover_label)

            self.restart = True

            return
        if game['need_raise_info']:
            self.raise_entry.lift(self.action_cover_label)
            self.raise_button.lift(self.action_cover_label)
        try:
            card1 = ImageTk.PhotoImage(
                Image.open("cards\\" + str(game['community_cards'][0]) + ".png").resize((55, 85), Image.ANTIALIAS))
            self.cc_1.image = card1
            self.cc_1.configure(image=card1)

            card1 = ImageTk.PhotoImage(
                Image.open("cards\\" + str(game['community_cards'][1]) + ".png").resize((55, 85), Image.ANTIALIAS))
            self.cc_2.image = card1
            self.cc_2.configure(image=card1)

            card1 = ImageTk.PhotoImage(
                Image.open("cards\\" + str(game['community_cards'][2]) + ".png").resize((55, 85), Image.ANTIALIAS))
            self.cc_3.image = card1
            self.cc_3.configure(image=card1)

            card1 = ImageTk.PhotoImage(
                Image.open("cards\\" + str(game['community_cards'][3]) + ".png").resize((55, 85), Image.ANTIALIAS))
            self.cc_4.image = card1
            self.cc_4.configure(image=card1)

            card1 = ImageTk.PhotoImage(
                Image.open("cards\\" + str(game['community_cards'][4]) + ".png").resize((55, 85), Image.ANTIALIAS))
            self.cc_5.image = card1
            self.cc_5.configure(image=card1)
        except IndexError:
            pass
        try:
            self.name_label_p0["text"] = game['players'][0].name
            self.name_label_p1["text"] = game['players'][1].name
            self.name_label_p2["text"] = game['players'][2].name
            self.name_label_p3["text"] = game['players'][3].name
            self.name_label_p4["text"] = game['players'][4].name
            self.name_label_p5["text"] = game['players'][5].name
            self.name_label_p6["text"] = game['players'][6].name
            self.name_label_p7["text"] = game['players'][7].name
            self.name_label_p8["text"] = game['players'][8].name
            self.name_label_p9["text"] = game['players'][9].name
        except IndexError:
            pass
        try:
            self.chips_label_p0["text"] = "Chips:\n" + str(game['players'][0].chips)
            self.chips_label_p1["text"] = "Chips:\n" + str(game['players'][1].chips)
            self.chips_label_p2["text"] = "Chips:\n" + str(game['players'][2].chips)
            self.chips_label_p3["text"] = "Chips:\n" + str(game['players'][3].chips)
            self.chips_label_p4["text"] = "Chips:\n" + str(game['players'][4].chips)
            self.chips_label_p5["text"] = "Chips:\n" + str(game['players'][5].chips)
            self.chips_label_p6["text"] = "Chips:\n" + str(game['players'][6].chips)
            self.chips_label_p7["text"] = "Chips:\n" + str(game['players'][7].chips)
            self.chips_label_p8["text"] = "Chips:\n" + str(game['players'][8].chips)
            self.chips_label_p9["text"] = "Chips:\n" + str(game['players'][9].chips)
        except IndexError:
            pass
        try:
            card1 = ImageTk.PhotoImage(
                Image.open("cards\\" + str(game['players'][0].cards[0]) + ".png").resize((55, 85),
                                                                                              Image.ANTIALIAS))
            self.card1_p0.image = card1
            self.card1_p0.configure(image=card1)

            card1 = ImageTk.PhotoImage(
                Image.open("cards\\" + str(game['players'][1].cards[0]) + ".png").resize((55, 85),
                                                                                              Image.ANTIALIAS))
            self.card1_p1.image = card1
            self.card1_p1.configure(image=card1)

            card1 = ImageTk.PhotoImage(
                Image.open("cards\\" + str(game['players'][2].cards[0]) + ".png").resize((55, 85),
                                                                                              Image.ANTIALIAS))
            self.card1_p2.image = card1
            self.card1_p2.configure(image=card1)

            card1 = ImageTk.PhotoImage(
                Image.open("cards\\" + str(game['players'][3].cards[0]) + ".png").resize((55, 85),
                                                                                              Image.ANTIALIAS))
            self.card1_p3.image = card1
            self.card1_p3.configure(image=card1)

            card1 = ImageTk.PhotoImage(
                Image.open("cards\\" + str(game['players'][4].cards[0]) + ".png").resize((55, 85),
                                                                                              Image.ANTIALIAS))
            self.card1_p4.image = card1
            self.card1_p4.configure(image=card1)

            card1 = ImageTk.PhotoImage(
                Image.open("cards\\" + str(game['players'][5].cards[0]) + ".png").resize((55, 85),
                                                                                              Image.ANTIALIAS))
            self.card1_p5.image = card1
            self.card1_p5.configure(image=card1)

            card1 = ImageTk.PhotoImage(
                Image.open("cards\\" + str(game['players'][6].cards[0]) + ".png").resize((55, 85),
                                                                                              Image.ANTIALIAS))
            self.card1_p6.image = card1
            self.card1_p6.configure(image=card1)

            card1 = ImageTk.PhotoImage(
                Image.open("cards\\" + str(game['players'][7].cards[0]) + ".png").resize((55, 85),
                                                                                              Image.ANTIALIAS))
            self.card1_p7.image = card1
            self.card1_p7.configure(image=card1)

            card1 = ImageTk.PhotoImage(
                Image.open("cards\\" + str(game['players'][8].cards[0]) + ".png").resize((55, 85),
                                                                                              Image.ANTIALIAS))
            self.card1_p8.image = card1
            self.card1_p8.configure(image=card1)

            card1 = ImageTk.PhotoImage(
                Image.open("cards\\" + str(game['players'][9].cards[0]) + ".png").resize((55, 85),
                                                                                              Image.ANTIALIAS))
            self.card1_p9.image = card1
            self.card1_p9.configure(image=card1)
        except IndexError:
            pass
        try:
            card2 = ImageTk.PhotoImage(
                Image.open("cards\\" + str(game['players'][0].cards[1]) + ".png").resize((55, 85),
                                                                                              Image.ANTIALIAS))
            self.card2_p0.image = card2
            self.card2_p0.configure(image=card2)

            card2 = ImageTk.PhotoImage(
                Image.open("cards\\" + str(game['players'][1].cards[1]) + ".png").resize((55, 85),
                                                                                              Image.ANTIALIAS))
            self.card2_p1.image = card2
            self.card2_p1.configure(image=card2)

            card2 = ImageTk.PhotoImage(
                Image.open("cards\\" + str(game['players'][2].cards[1]) + ".png").resize((55, 85),
                                                                                              Image.ANTIALIAS))
            self.card2_p2.image = card2
            self.card2_p2.configure(image=card2)

            card2 = ImageTk.PhotoImage(
                Image.open("cards\\" + str(game['players'][3].cards[1]) + ".png").resize((55, 85),
                                                                                              Image.ANTIALIAS))
            self.card2_p3.image = card2
            self.card2_p3.configure(image=card2)

            card2 = ImageTk.PhotoImage(
                Image.open("cards\\" + str(game['players'][4].cards[1]) + ".png").resize((55, 85),
                                                                                              Image.ANTIALIAS))
            self.card2_p4.image = card2
            self.card2_p4.configure(image=card2)

            card2 = ImageTk.PhotoImage(
                Image.open("cards\\" + str(game['players'][5].cards[1]) + ".png").resize((55, 85),
                                                                                              Image.ANTIALIAS))
            self.card2_p5.image = card2
            self.card2_p5.configure(image=card2)

            card2 = ImageTk.PhotoImage(
                Image.open("cards\\" + str(game['players'][6].cards[1]) + ".png").resize((55, 85),
                                                                                              Image.ANTIALIAS))
            self.card2_p6.image = card2
            self.card2_p6.configure(image=card2)

            card2 = ImageTk.PhotoImage(
                Image.open("cards\\" + str(game['players'][7].cards[1]) + ".png").resize((55, 85),
                                                                                              Image.ANTIALIAS))
            self.card2_p7.image = card2
            self.card2_p7.configure(image=card2)

            card2 = ImageTk.PhotoImage(
                Image.open("cards\\" + str(game['players'][8].cards[1]) + ".png").resize((55, 85),
                                                                                              Image.ANTIALIAS))
            self.card2_p8.image = card2
            self.card2_p8.configure(image=card2)

            card2 = ImageTk.PhotoImage(
                Image.open("cards\\" + str(game['players'][9].cards[1]) + ".png").resize((55, 85),
                                                                                              Image.ANTIALIAS))
            self.card2_p9.image = card2
            self.card2_p9.configure(image=card2)
        except IndexError:
            pass
        try:
            self.stake_label_p0["text"] = "Stake: " + str(game['players'][0].stake)
            self.stake_label_p1["text"] = "Stake: " + str(game['players'][1].stake)
            self.stake_label_p2["text"] = "Stake: " + str(game['players'][2].stake)
            self.stake_label_p3["text"] = "Stake: " + str(game['players'][3].stake)
            self.stake_label_p4["text"] = "Stake: " + str(game['players'][4].stake)
            self.stake_label_p5["text"] = "Stake: " + str(game['players'][5].stake)
            self.stake_label_p6["text"] = "Stake: " + str(game['players'][6].stake)
            self.stake_label_p7["text"] = "Stake: " + str(game['players'][7].stake)
            self.stake_label_p8["text"] = "Stake: " + str(game['players'][8].stake)
            self.stake_label_p9["text"] = "Stake: " + str(game['players'][9].stake)
        except IndexError:
            pass
        self.pot_label["text"] = "Pot: " + str(game['pot'])
        winners = []
        for player in game['players']:
            if player.isWinner:
                winners.append(player)
        if game['game_over']:
            self.actor_label["text"] = "Winner!: " + str(winners[0])
            return
        print(f"round ended: {game['round_over']}")

        for player in game['players']:
            if player.isActing:
                self.actor_label["text"] = str(player.name)

        variable = StringVar(self.action_frame)
        variable.initialize("ACTION")
        w = OptionMenu(self.action_frame, variable, *game['possible_responses'])
        w.place(relx=0, rely=0.05, relheight=0.1, relwidth=0.3)
        button_go = Button(self.action_frame, text="GO", font=("Courier", 10),
                           command=lambda: self.action_input(variable.get()))
        button_go.place(relx=1, rely=1, relheight=0.3, relwidth=0.3, anchor="se")

    def action_input(self, entry0):

        response_q.put(entry0)
        game_event.set()
        time.sleep(0.1)
        if not game_info_q.empty():
            self.update(game_info_q.get())


game_event = threading.Event()
game_info_q = queue.Queue()
response_q = queue.Queue()


def run_app():
    app = App()
    app.mainloop()


t1 = threading.Thread(target=run_app)
t1.start()
