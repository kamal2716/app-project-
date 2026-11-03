"""Reusable, consistently styled interface components."""
import customtkinter as ctk
from config import COLORS

class MetricCard(ctk.CTkFrame):
    def __init__(self,master,label,value,caption,accent,**kwargs):
        super().__init__(master,fg_color="white",corner_radius=16,border_width=1,border_color=COLORS["line"],**kwargs)
        self.grid_columnconfigure(0,weight=1)
        ctk.CTkLabel(self,text=label,text_color=COLORS["muted"],font=("Segoe UI",12,"bold")).grid(row=0,column=0,sticky="w",padx=18,pady=(16,4))
        ctk.CTkLabel(self,text=str(value),text_color=COLORS["ink"],font=("Segoe UI",28,"bold")).grid(row=1,column=0,sticky="w",padx=18)
        ctk.CTkLabel(self,text=caption,text_color=accent,font=("Segoe UI",11)).grid(row=2,column=0,sticky="w",padx=18,pady=(3,16))

def section_title(master,title,subtitle=None):
    box=ctk.CTkFrame(master,fg_color="transparent")
    ctk.CTkLabel(box,text=title,font=("Segoe UI",24,"bold"),text_color=COLORS["ink"]).pack(anchor="w")
    if subtitle: ctk.CTkLabel(box,text=subtitle,font=("Segoe UI",12),text_color=COLORS["muted"]).pack(anchor="w",pady=(4,0))
    return box

def styled_button(master,text,command,kind="primary",**kwargs):
    fill={"primary":COLORS["navy"],"success":COLORS["green"],"danger":COLORS["red"],"light":"#EDF2F8"}.get(kind,COLORS["navy"])
    color=COLORS["ink"] if kind=="light" else "white"
    return ctk.CTkButton(master,text=text,command=command,fg_color=fill,hover_color=COLORS["navy_light"],
        text_color=color,corner_radius=9,height=38,font=("Segoe UI",12,"bold"),**kwargs)
