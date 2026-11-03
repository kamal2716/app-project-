"""Main CAMPUS IQ desktop application and dashboard."""
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from datetime import date
from config import APP_NAME, COLORS, WINDOW_SIZE, MIN_WINDOW_SIZE
from ui.login import LoginView
from ui.components import MetricCard, section_title, styled_button
from services.analytics import dashboard_metrics
from services.bookings import list_facilities, create_booking, list_bookings
from services.maintenance import create_request, update_status
from services.assets import list_assets, add_asset, set_asset_condition
from database.db import connection
from utils.exporters import export_rows

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class CampusIQApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME+"  |  Smart Campus Operations")
        self.geometry(WINDOW_SIZE); self.minsize(*MIN_WINDOW_SIZE)
        self.configure(fg_color=COLORS["canvas"])
        self.user=None
        self.show_login()

    def clear(self):
        for child in self.winfo_children(): child.destroy()

    def show_login(self):
        self.clear()
        LoginView(self,self.on_login).pack(fill="both",expand=True)

    def on_login(self,user):
        self.user=user
        self.build_shell()
        self.show_dashboard()

    def build_shell(self):
        self.clear()
        self.grid_columnconfigure(1,weight=1); self.grid_rowconfigure(0,weight=1)
        side=ctk.CTkFrame(self,width=238,corner_radius=0,fg_color=COLORS["navy"])
        side.grid(row=0,column=0,sticky="nsew"); side.grid_propagate(False)
        ctk.CTkLabel(side,text="CAMPUS IQ",font=("Segoe UI",23,"bold"),text_color="white").pack(anchor="w",padx=24,pady=(28,2))
        ctk.CTkLabel(side,text="OPERATIONS INTELLIGENCE",font=("Segoe UI",9,"bold"),text_color="#AFC2E7").pack(anchor="w",padx=25,pady=(0,28))
        groups=[
            ("OVERVIEW",[("▦  Dashboard",self.show_dashboard)]),
            ("CAMPUS",[("▤  Facilities",self.show_facilities),("▣  Bookings",self.show_bookings),("▧  Assets",self.show_assets),("⚙  Maintenance",self.show_maintenance)]),
            ("INSIGHTS",[("◷  Energy & analytics",self.show_energy),("⇩  Reports",self.show_reports)])]
        for heading,items in groups:
            ctk.CTkLabel(side,text=heading,font=("Segoe UI",9,"bold"),text_color="#8DA6D3").pack(anchor="w",padx=24,pady=(8,5))
            for label,command in items:
                ctk.CTkButton(side,text=label,anchor="w",height=40,corner_radius=9,fg_color="transparent",
                    hover_color=COLORS["navy_light"],text_color="#F3F6FC",font=("Segoe UI",12),command=command).pack(fill="x",padx=13,pady=2)
        ctk.CTkFrame(side,fg_color="#314675",height=1).pack(fill="x",padx=20,pady=(22,12))
        ctk.CTkLabel(side,text=self.user["full_name"],text_color="white",font=("Segoe UI",12,"bold")).pack(anchor="w",padx=22)
        ctk.CTkLabel(side,text=self.user["role"],text_color="#B9C8E2",font=("Segoe UI",10)).pack(anchor="w",padx=22,pady=(2,12))
        ctk.CTkButton(side,text="↪  Sign out",height=36,fg_color="#314675",hover_color="#405889",command=self.show_login).pack(fill="x",padx=14,pady=(0,18))
        self.content=ctk.CTkFrame(self,fg_color=COLORS["canvas"],corner_radius=0)
        self.content.grid(row=0,column=1,sticky="nsew")
        self.content.grid_columnconfigure(0,weight=1); self.content.grid_rowconfigure(1,weight=1)
        header=ctk.CTkFrame(self.content,fg_color="white",height=68,corner_radius=0)
        header.grid(row=0,column=0,sticky="ew"); header.grid_columnconfigure(0,weight=1)
        ctk.CTkLabel(header,text="Campus workspace",text_color=COLORS["muted"],font=("Segoe UI",12)).grid(row=0,column=0,sticky="w",padx=28,pady=22)
        ctk.CTkLabel(header,text="●  Demo environment",text_color=COLORS["green"],font=("Segoe UI",11,"bold")).grid(row=0,column=1,padx=28)

    def page(self,title,subtitle):
        for child in self.content.winfo_children()[1:]: child.destroy()
        body=ctk.CTkScrollableFrame(self.content,fg_color="transparent")
        body.grid(row=1,column=0,sticky="nsew",padx=26,pady=22)
        section_title(body,title,subtitle).pack(anchor="w",pady=(0,20))
        return body

    def show_dashboard(self):
        data=dashboard_metrics()
        body=self.page("Good day, "+self.user["full_name"].split()[0], "Here is what is happening across your campus today.")
        cards=ctk.CTkFrame(body,fg_color="transparent"); cards.pack(fill="x")
        for i,(label,value,caption,color) in enumerate([
            ("Buildings",data["buildings"],"Registered blocks",COLORS["blue"]),
            ("Facilities",data["facilities"],"Rooms and shared spaces",COLORS["cyan"]),
            ("Tracked assets",data["assets"],"Equipment in registry",COLORS["green"]),
            ("Open maintenance",data["pending"],"Requires attention",COLORS["amber"]),
            ("Today's bookings",data["bookings"],"Pending or approved",COLORS["blue"]),
            ("Needs repair",data["damaged"],"Assets flagged",COLORS["red"])]):
            cards.grid_columnconfigure(i%3,weight=1)
            MetricCard(cards,label,value,caption,color).grid(row=i//3,column=i%3,sticky="ew",padx=(0,12),pady=(0,12))
        lower=ctk.CTkFrame(body,fg_color="transparent"); lower.pack(fill="both",expand=True,pady=8)
        left=ctk.CTkFrame(lower,fg_color="white",corner_radius=16,border_width=1,border_color=COLORS["line"])
        left.pack(side="left",fill="both",expand=True,padx=(0,10))
        ctk.CTkLabel(left,text="Maintenance pulse",font=("Segoe UI",16,"bold"),text_color=COLORS["ink"]).pack(anchor="w",padx=18,pady=(18,12))
        for row in data["recent"]:
            line=ctk.CTkFrame(left,fg_color="#F8FAFD",corner_radius=10); line.pack(fill="x",padx=14,pady=5)
            ctk.CTkLabel(line,text=f"#{row['id']}  {row['item']}",font=("Segoe UI",12,"bold"),text_color=COLORS["ink"]).pack(anchor="w",padx=12,pady=(8,1))
            ctk.CTkLabel(line,text=f"{row['category']}  •  {row['priority']} priority  •  {row['status']}",font=("Segoe UI",10),text_color=COLORS["muted"]).pack(anchor="w",padx=12,pady=(0,8))
        if not data["recent"]: ctk.CTkLabel(left,text="No maintenance requests recorded.",text_color=COLORS["muted"]).pack(pady=20)
        right=ctk.CTkFrame(lower,fg_color="white",corner_radius=16,border_width=1,border_color=COLORS["line"],width=270)
        right.pack(side="right",fill="y")
        ctk.CTkLabel(right,text="Energy snapshot",font=("Segoe UI",16,"bold"),text_color=COLORS["ink"]).pack(anchor="w",padx=18,pady=(18,8))
        ctk.CTkLabel(right,text=f"{data['energy']:,.0f} kWh",font=("Segoe UI",30,"bold"),text_color=COLORS["navy"]).pack(anchor="w",padx=18,pady=3)
        ctk.CTkLabel(right,text="Recorded this month",text_color=COLORS["muted"]).pack(anchor="w",padx=18)
        styled_button(right,"View energy analytics",self.show_energy).pack(fill="x",padx=16,pady=20)

    def table(self,parent,columns,rows):
        wrap=ctk.CTkFrame(parent,fg_color="white",corner_radius=14,border_width=1,border_color=COLORS["line"])
        tree=ttk.Treeview(wrap,columns=columns,show="headings",height=12)
        style=ttk.Style(); style.theme_use("clam")
        style.configure("Treeview",background="white",foreground=COLORS["ink"],fieldbackground="white",rowheight=34,font=("Segoe UI",10))
        style.configure("Treeview.Heading",background="#F1F5FA",foreground=COLORS["navy"],font=("Segoe UI",10,"bold"),relief="flat")
        style.map("Treeview",background=[("selected","#E5EEFF")],foreground=[("selected",COLORS["navy"])])
        for col in columns: tree.heading(col,text=col.replace("_"," ").title()); tree.column(col,width=135,anchor="w")
        for row in rows: tree.insert("","end",values=[row.get(c,"") for c in columns])
        tree.pack(fill="both",expand=True,padx=10,pady=10)
        return wrap,tree

    def show_facilities(self):
        body=self.page("Facilities","Browse registered campus spaces and their availability.")
        rows=[]
        with connection() as conn:
            rows=[dict(r) for r in conn.execute("""SELECT f.room_code,f.name,f.facility_type,b.name building_name,f.floor_number,f.capacity,f.status,f.condition
                FROM facilities f JOIN buildings b ON b.id=f.building_id ORDER BY b.name,f.room_code""")]
        self.table(body,("room_code","name","facility_type","building_name","floor_number","capacity","status","condition"),rows)[0].pack(fill="x")

    def show_bookings(self):
        body=self.page("Facility bookings","Create a reservation request. Time overlaps and capacity are validated.")
        facilities=list_facilities()
        if self.user["role"] in ("Student","Faculty","Administrator"):
            form=ctk.CTkFrame(body,fg_color="white",corner_radius=14,border_width=1,border_color=COLORS["line"]); form.pack(fill="x",pady=(0,15))
            ctk.CTkLabel(form,text="New booking request",font=("Segoe UI",15,"bold"),text_color=COLORS["ink"]).grid(row=0,column=0,columnspan=4,sticky="w",padx=16,pady=14)
            fac=ctk.CTkComboBox(form,values=[f"{x['id']} | {x['name']} ({x['building_name']})" for x in facilities],width=260); fac.grid(row=1,column=0,padx=12,pady=8)
            dt=ctk.CTkEntry(form,placeholder_text="YYYY-MM-DD",width=140); dt.insert(0,date.today().isoformat()); dt.grid(row=1,column=1,padx=8)
            st=ctk.CTkEntry(form,placeholder_text="Start HH:MM",width=110); st.insert(0,"10:00"); st.grid(row=1,column=2,padx=8)
            et=ctk.CTkEntry(form,placeholder_text="End HH:MM",width=110); et.insert(0,"11:00"); et.grid(row=1,column=3,padx=8)
            purpose=ctk.CTkEntry(form,placeholder_text="Purpose of booking",width=260); purpose.grid(row=2,column=0,padx=12,pady=8)
            attendees=ctk.CTkEntry(form,placeholder_text="Participants",width=140); attendees.insert(0,"10"); attendees.grid(row=2,column=1,padx=8)
            def submit():
                try:
                    fid=int(fac.get().split("|")[0].strip())
                    create_booking(fid,self.user["id"],dt.get().strip(),st.get().strip(),et.get().strip(),purpose.get().strip(),int(attendees.get()))
                    messagebox.showinfo("Booking","Request submitted for approval."); self.show_bookings()
                except Exception as exc: messagebox.showerror("Booking not created",str(exc))
            styled_button(form,"Submit request",submit).grid(row=2,column=2,padx=8,pady=8)
        rows=list_bookings()
        if self.user["role"] not in ("Administrator","Faculty"): rows=[r for r in rows if r["user_id"]==self.user["id"]]
        cols=("id","facility","building","booking_date","start_time","end_time","purpose","attendees","status")
        self.table(body,cols,rows)[0].pack(fill="x")

    def show_assets(self):
        body=self.page("Asset register","Track equipment, condition and availability across campus.")
        if self.user["role"] in ("Administrator","Lab Assistant"):
            form=ctk.CTkFrame(body,fg_color="white",corner_radius=14); form.pack(fill="x",pady=(0,14))
            code=ctk.CTkEntry(form,placeholder_text="Asset code",width=150); code.grid(row=0,column=0,padx=8,pady=12)
            name=ctk.CTkEntry(form,placeholder_text="Asset name",width=210); name.grid(row=0,column=1,padx=8)
            cat=ctk.CTkComboBox(form,values=["Computer","Laptop","Projector","Printer","Lab Instrument","Networking","Furniture"],width=165); cat.grid(row=0,column=2,padx=8)
            serial=ctk.CTkEntry(form,placeholder_text="Serial number (optional)",width=190); serial.grid(row=0,column=3,padx=8)
            def add():
                try: add_asset(code.get(),name.get(),cat.get(),serial.get(),None,None); messagebox.showinfo("Asset","Asset added."); self.show_assets()
                except Exception as exc: messagebox.showerror("Unable to add asset",str(exc))
            styled_button(form,"Add asset",add).grid(row=0,column=4,padx=8)
        rows=list_assets()
        cols=("asset_code","name","category","serial_number","building","room","condition","status")
        wrap,tree=self.table(body,cols,rows); wrap.pack(fill="x")
        if self.user["role"] in ("Administrator","Lab Assistant"):
            action=ctk.CTkFrame(body,fg_color="transparent"); action.pack(anchor="e",pady=10)
            def mark_repair():
                selected=tree.selection()
                if not selected: messagebox.showwarning("Select asset","Select an asset row first."); return
                code=tree.item(selected[0],"values")[0]
                target=next((a for a in rows if a["asset_code"]==code),None)
                if target:
                    set_asset_condition(target["id"],"Needs Repair"); messagebox.showinfo("Updated","Asset flagged for repair."); self.show_assets()
            styled_button(action,"Mark selected as needs repair",mark_repair,kind="light").pack()

    def show_maintenance(self):
        body=self.page("Maintenance desk","Log faults and follow requests through the repair workflow.")
        facilities=list_facilities(); assets=list_assets()
        if self.user["role"] not in ("Student",):
            form=ctk.CTkFrame(body,fg_color="white",corner_radius=14); form.pack(fill="x",pady=(0,14))
            target=ctk.CTkComboBox(form,values=["Facility: "+str(x["id"])+" | "+x["name"] for x in facilities]+["Asset: "+str(x["id"])+" | "+x["name"] for x in assets],width=280); target.grid(row=0,column=0,padx=10,pady=12)
            category=ctk.CTkComboBox(form,values=["Electrical","Equipment","Internet","Furniture","Plumbing","Infrastructure"],width=160); category.grid(row=0,column=1,padx=8)
            desc=ctk.CTkEntry(form,placeholder_text="Describe the issue",width=340); desc.grid(row=0,column=2,padx=8)
            def submit():
                try:
                    val=target.get()
                    if val.startswith("Facility:"): fid=int(val.split("|")[0].split(":")[1]); aid=None
                    else: aid=int(val.split("|")[0].split(":")[1]); fid=None
                    rid=create_request(self.user["id"],fid,aid,category.get(),desc.get())
                    messagebox.showinfo("Maintenance",f"Request #{rid} created."); self.show_maintenance()
                except Exception as exc: messagebox.showerror("Unable to create request",str(exc))
            styled_button(form,"Log request",submit).grid(row=0,column=3,padx=10)
        with connection() as conn:
            rows=[dict(r) for r in conn.execute("""SELECT m.id,m.category,m.description,m.priority,m.status,m.reported_at,
                COALESCE(f.name,a.name,'Campus item') item,u.full_name reporter
                FROM maintenance_requests m LEFT JOIN facilities f ON f.id=m.facility_id LEFT JOIN assets a ON a.id=m.asset_id
                JOIN users u ON u.id=m.reported_by ORDER BY m.id DESC""")]
        cols=("id","item","category","description","priority","status","reporter","reported_at")
        wrap,tree=self.table(body,cols,rows); wrap.pack(fill="x")
        if self.user["role"] in ("Administrator","Maintenance Staff"):
            controls=ctk.CTkFrame(body,fg_color="transparent"); controls.pack(anchor="e",pady=10)
            status=ctk.CTkComboBox(controls,values=["Assigned","In Progress","Resolved","Closed"],width=160); status.pack(side="left",padx=7)
            def update():
                selected=tree.selection()
                if not selected: messagebox.showwarning("Select request","Select a request first."); return
                rid=int(tree.item(selected[0],"values")[0])
                try: update_status(rid,status.get(),self.user["id"]); messagebox.showinfo("Maintenance","Request status updated."); self.show_maintenance()
                except Exception as exc: messagebox.showerror("Update failed",str(exc))
            styled_button(controls,"Update status",update).pack(side="left")

    def show_energy(self):
        body=self.page("Energy intelligence","Building-level electricity records. Demo records are labelled in the database.")
        with connection() as conn:
            rows=[dict(r) for r in conn.execute("""SELECT e.recorded_on,b.name building,e.meter_id,e.consumption_kwh,e.cost,e.source
                FROM energy_records e JOIN buildings b ON b.id=e.building_id ORDER BY recorded_on DESC""")]
            totals=[dict(r) for r in conn.execute("""SELECT b.name,COALESCE(SUM(e.consumption_kwh),0) kwh,
                COALESCE(SUM(e.cost),0) cost FROM buildings b LEFT JOIN energy_records e ON e.building_id=b.id GROUP BY b.id""")]
        self.table(body,("building","kwh","cost"),totals)[0].pack(fill="x",pady=(0,14))
        self.table(body,("recorded_on","building","meter_id","consumption_kwh","cost","source"),rows)[0].pack(fill="x")

    def show_reports(self):
        body=self.page("Reports & exports","Export current campus datasets for project reviews and operational audits.")
        options=[("Facilities","SELECT room_code,name,facility_type,status,condition FROM facilities",["Room","Name","Type","Status","Condition"]),
            ("Assets","SELECT asset_code,name,category,condition,status FROM assets",["Asset code","Name","Category","Condition","Status"]),
            ("Maintenance","SELECT id,category,description,priority,status,reported_at FROM maintenance_requests",["ID","Category","Description","Priority","Status","Reported"]),
            ("Energy","SELECT recorded_on,meter_id,consumption_kwh,cost,source FROM energy_records",["Date","Meter","kWh","Cost","Source"])]
        for title,sql,headers in options:
            card=ctk.CTkFrame(body,fg_color="white",corner_radius=13); card.pack(fill="x",pady=6)
            ctk.CTkLabel(card,text=title,font=("Segoe UI",14,"bold"),text_color=COLORS["ink"]).pack(side="left",padx=16,pady=14)
            def export(sql=sql,headers=headers,title=title):
                with connection() as conn: rows=[tuple(r) for r in conn.execute(sql)]
                path=filedialog.asksaveasfilename(defaultextension=".xlsx",initialfile=title.lower()+"_report.xlsx",filetypes=[("Excel workbook","*.xlsx"),("CSV","*.csv"),("PDF","*.pdf")])
                if not path:return
                kind=path.rsplit(".",1)[-1].lower()
                try: result=export_rows(path.split("/")[-1],headers,rows,kind); messagebox.showinfo("Export complete",f"Report saved to:\n{result}")
                except Exception as exc: messagebox.showerror("Export failed",str(exc))
            styled_button(card,"Export",export,kind="light").pack(side="right",padx=14,pady=8)
