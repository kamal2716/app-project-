"""Professional login screen."""
import customtkinter as ctk
from tkinter import messagebox
from services.auth import authenticate
from config import COLORS

class LoginView(ctk.CTkFrame):
    def __init__(self,master,on_success):
        super().__init__(master,fg_color=COLORS["canvas"])
        self.on_success=on_success
        panel=ctk.CTkFrame(self,corner_radius=22,fg_color="white",border_width=1,border_color=COLORS["line"],width=430)
        panel.place(relx=.5,rely=.5,anchor="center")
        ctk.CTkLabel(panel,text="CAMPUS IQ",font=("Segoe UI",30,"bold"),text_color=COLORS["navy"]).pack(padx=42,pady=(38,4))
        ctk.CTkLabel(panel,text="Campus operations, made intelligent.",text_color=COLORS["muted"]).pack(padx=30,pady=(0,28))
        self.username=ctk.CTkEntry(panel,width=340,height=44,placeholder_text="Username")
        self.username.pack(padx=40,pady=7)
        self.password=ctk.CTkEntry(panel,width=340,height=44,placeholder_text="Password",show="•")
        self.password.pack(padx=40,pady=7)
        ctk.CTkButton(panel,text="Sign in",width=340,height=44,corner_radius=10,fg_color=COLORS["navy"],command=self.login).pack(padx=40,pady=(18,12))
        ctk.CTkLabel(panel,text="DEMO ACCESS",font=("Segoe UI",10,"bold"),text_color=COLORS["muted"]).pack(pady=(5,3))
        ctk.CTkLabel(panel,text="admin / Admin@123",font=("Segoe UI",12),text_color=COLORS["ink"]).pack(pady=(0,30))
        self.password.bind("<Return>",lambda _e:self.login())
    def login(self):
        user=authenticate(self.username.get(),self.password.get())
        if user: self.on_success(user)
        else: messagebox.showerror("Sign-in failed","Username or password is incorrect.")
