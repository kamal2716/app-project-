"""CAMPUS IQ desktop UI with role-aware workflows."""
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from datetime import date
from pathlib import Path
from config import APP_NAME, COLORS, WINDOW_SIZE, MIN_WINDOW_SIZE
from ui.login import LoginView
from ui.components import MetricCard, section_title, styled_button
from database.db import connection
from services.analytics import dashboard_metrics
from services.bookings import list_facilities, create_booking, list_bookings, review_booking
from services.maintenance import create_request, update_status, list_requests
from services.assets import list_assets, add_asset, set_asset_condition
from services.notifications import list_notifications, unread_count, mark_all_read, mark_read
from utils.exporters import export_rows

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")
ADMIN="Administrator"

class CampusIQApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME+" | Smart Campus Operations")
        self.geometry(WINDOW_SIZE); self.minsize(*MIN_WINDOW_SIZE)
        self.configure(fg_color=COLORS["canvas"]); self.user=None
        self.show_login()
    def clear(self):
        for child in self.winfo_children(): child.destroy()
    def show_login(self):
        self.user=None; self.clear()
        LoginView(self,self.on_login).pack(fill="both",expand=True)
    def on_login(self,user):
        self.user=user; self.build_shell(); self.show_dashboard()
    def build_shell(self):
        self.clear(); self.grid_columnconfigure(1,weight=1); self.grid_rowconfigure(0,weight=1)
        side=ctk.CTkFrame(self,width=238,corner_radius=0,fg_color=COLORS["navy"])
        side.grid(row=0,column=0,sticky="nsew"); side.grid_propagate(False)
        ctk.CTkLabel(side,text="CAMPUS IQ",font=("Segoe UI",23,"bold"),text_color="white").pack(anchor="w",padx=24,pady=(28,2))
        ctk.CTkLabel(side,text="OPERATIONS INTELLIGENCE",font=("Segoe UI",9,"bold"),text_color="#AFC2E7").pack(anchor="w",padx=25,pady=(0,25))
        role=self.user["role"]
        groups=[("OVERVIEW",[("Dashboard",self.show_dashboard)]),
          ("CAMPUS",[("Facilities",self.show_facilities),("Bookings",self.show_bookings),("Assets",self.show_assets),("Maintenance",self.show_maintenance)]),
          ("INSIGHTS",[("Energy & analytics",self.show_energy),("Notifications",self.show_notifications),("Reports",self.show_reports)])]
        for heading,items in groups:
            ctk.CTkLabel(side,text=heading.upper(),font=("Segoe UI",9,"bold"),text_color="#8DA6D3").pack(anchor="w",padx=24,pady=(8,5))
            for label,command in items:
                # Navigation visibility is based on the signed-in role.
                if label=="Assets" and role not in (ADMIN,"Lab Assistant"): continue
                if label=="Energy & analytics" and role not in (ADMIN,"Faculty"): continue
                if label=="Reports" and role not in (ADMIN,"Faculty","Maintenance Staff"): continue
                ctk.CTkButton(side,text=label,anchor="w",height=39,corner_radius=9,fg_color="transparent",hover_color=COLORS["navy_light"],text_color="#F3F6FC",font=("Segoe UI",12),command=command).pack(fill="x",padx=13,pady=2)
        ctk.CTkFrame(side,fg_color="#314675",height=1).pack(fill="x",padx=20,pady=(22,12))
        ctk.CTkLabel(side,text=self.user["full_name"],text_color="white",font=("Segoe UI",12,"bold")).pack(anchor="w",padx=22)
        ctk.CTkLabel(side,text=role,text_color="#B9C8E2",font=("Segoe UI",10)).pack(anchor="w",padx=22,pady=(2,12))
        ctk.CTkButton(side,text="Sign out",height=36,fg_color="#314675",hover_color="#405889",command=self.show_login).pack(fill="x",padx=14,pady=(0,18))
        self.content=ctk.CTkFrame(self,fg_color=COLORS["canvas"],corner_radius=0)
        self.content.grid(row=0,column=1,sticky="nsew"); self.content.grid_columnconfigure(0,weight=1); self.content.grid_rowconfigure(1,weight=1)
        header=ctk.CTkFrame(self.content,fg_color="white",height=68,corner_radius=0); header.grid(row=0,column=0,sticky="ew"); header.grid_columnconfigure(0,weight=1)
        ctk.CTkLabel(header,text="Campus workspace",text_color=COLORS["muted"],font=("Segoe UI",12)).grid(row=0,column=0,sticky="w",padx=28,pady=22)
        count=unread_count(self.user["id"])
        ctk.CTkButton(header,text=f"Notifications  ({count})",width=150,fg_color=COLORS["blue_soft"],text_color=COLORS["navy"],hover_color="#D9E7FF",command=self.show_notifications).grid(row=0,column=1,padx=20,pady=12)
    def page(self,title,subtitle):
        for child in self.content.winfo_children()[1:]: child.destroy()
        body=ctk.CTkScrollableFrame(self.content,fg_color="transparent"); body.grid(row=1,column=0,sticky="nsew",padx=26,pady=22)
        section_title(body,title,subtitle).pack(anchor="w",pady=(0,20)); return body
    def table(self,parent,columns,rows):
        wrap=ctk.CTkFrame(parent,fg_color="white",corner_radius=14,border_width=1,border_color=COLORS["line"])
        tree=ttk.Treeview(wrap,columns=columns,show="headings",height=11)
        style=ttk.Style(); style.theme_use("clam")
        style.configure("Treeview",background="white",foreground=COLORS["ink"],fieldbackground="white",rowheight=34,font=("Segoe UI",10))
        style.configure("Treeview.Heading",background="#F1F5FA",foreground=COLORS["navy"],font=("Segoe UI",10,"bold"),relief="flat")
        for col in columns: tree.heading(col,text=col.replace("_"," ").title()); tree.column(col,width=135,anchor="w")
        for row in rows: tree.insert("","end",values=[row.get(c,"") for c in columns])
        tree.pack(fill="both",expand=True,padx=10,pady=10); return wrap,tree
    def show_dashboard(self):
        data=dashboard_metrics(); body=self.page("Good day, "+self.user["full_name"].split()[0],"Here is what is happening across your campus today.")
        cards=ctk.CTkFrame(body,fg_color="transparent"); cards.pack(fill="x")
        for i,(label,value,caption,color) in enumerate([("Buildings",data["buildings"],"Registered blocks",COLORS["blue"]),("Facilities",data["facilities"],"Rooms and shared spaces",COLORS["cyan"]),("Tracked assets",data["assets"],"Equipment in registry",COLORS["green"]),("Open maintenance",data["pending"],"Requires attention",COLORS["amber"]),("Today's bookings",data["bookings"],"Pending or approved",COLORS["blue"]),("Needs repair",data["damaged"],"Assets flagged",COLORS["red"])]):
            cards.grid_columnconfigure(i%3,weight=1); MetricCard(cards,label,value,caption,color).grid(row=i//3,column=i%3,sticky="ew",padx=(0,12),pady=(0,12))
        lower=ctk.CTkFrame(body,fg_color="transparent"); lower.pack(fill="both",expand=True,pady=8)
        left=ctk.CTkFrame(lower,fg_color="white",corner_radius=16,border_width=1,border_color=COLORS["line"]); left.pack(side="left",fill="both",expand=True,padx=(0,10))
        ctk.CTkLabel(left,text="Maintenance pulse",font=("Segoe UI",16,"bold"),text_color=COLORS["ink"]).pack(anchor="w",padx=18,pady=(18,12))
        for row in data["recent"]:
            ctk.CTkLabel(left,text=f"#{row['id']}  {row['item']}  •  {row['priority']}  •  {row['status']}",text_color=COLORS["ink"]).pack(anchor="w",padx=18,pady=7)
        if not data["recent"]: ctk.CTkLabel(left,text="No maintenance requests yet.",text_color=COLORS["muted"]).pack(pady=20)
        right=ctk.CTkFrame(lower,fg_color="white",corner_radius=16,width=250); right.pack(side="right",fill="y")
        ctk.CTkLabel(right,text="Energy this month",font=("Segoe UI",15,"bold"),text_color=COLORS["ink"]).pack(anchor="w",padx=18,pady=(18,8))
        ctk.CTkLabel(right,text=f"{data['energy']:,.0f} kWh",font=("Segoe UI",28,"bold"),text_color=COLORS["navy"]).pack(anchor="w",padx=18)
        ctk.CTkLabel(right,text="Recorded meter data only",text_color=COLORS["muted"]).pack(anchor="w",padx=18,pady=4)
        styled_button(right,"View energy analytics",self.show_energy).pack(fill="x",padx=16,pady=18)
    def show_facilities(self):
        body=self.page("Facilities","Campus rooms and shared spaces. Administrators can register new facilities.")
        if self.user["role"]==ADMIN:
            form=ctk.CTkFrame(body,fg_color="white",corner_radius=12); form.pack(fill="x",pady=(0,14))
            with connection() as conn: buildings=[dict(r) for r in conn.execute("SELECT id,name FROM buildings ORDER BY name")]
            room=ctk.CTkEntry(form,placeholder_text="Room code",width=125); room.grid(row=0,column=0,padx=7,pady=12)
            name=ctk.CTkEntry(form,placeholder_text="Facility name",width=190); name.grid(row=0,column=1,padx=7)
            typ=ctk.CTkComboBox(form,values=["Classroom","Laboratory","Seminar Hall","Meeting Room","Library"],width=145); typ.grid(row=0,column=2,padx=7)
            bld=ctk.CTkComboBox(form,values=[f"{b['id']} | {b['name']}" for b in buildings],width=170); bld.grid(row=0,column=3,padx=7)
            cap=ctk.CTkEntry(form,placeholder_text="Capacity",width=90); cap.grid(row=0,column=4,padx=7)
            def add_facility():
                try:
                    if not bld.get(): raise ValueError("Select a building.")
                    with connection() as conn: conn.execute("INSERT INTO facilities(building_id,room_code,name,facility_type,capacity) VALUES(?,?,?,?,?)",(int(bld.get().split("|")[0]),room.get().strip(),name.get().strip(),typ.get(),int(cap.get())))
                    messagebox.showinfo("Facility","Facility registered."); self.show_facilities()
                except Exception as exc: messagebox.showerror("Unable to add facility",str(exc))
            styled_button(form,"Add facility",add_facility).grid(row=0,column=5,padx=8)
        with connection() as conn: rows=[dict(r) for r in conn.execute("""SELECT f.id,f.room_code,f.name,f.facility_type,b.name building_name,f.floor_number,f.capacity,f.status,f.condition FROM facilities f JOIN buildings b ON b.id=f.building_id ORDER BY b.name,f.room_code""")]
        self.table(body,("id","room_code","name","facility_type","building_name","floor_number","capacity","status","condition"),rows)[0].pack(fill="x")
    def show_bookings(self):
        role=self.user["role"]; body=self.page("Facility bookings","Request a room and follow its approval status.")
        facilities=list_facilities()
        if role in ("Student","Faculty"):
            form=ctk.CTkFrame(body,fg_color="white",corner_radius=14); form.pack(fill="x",pady=(0,14))
            fac=ctk.CTkComboBox(form,values=[f"{x['id']} | {x['name']} ({x['building_name']})" for x in facilities],width=260); fac.grid(row=0,column=0,padx=8,pady=12)
            dt=ctk.CTkEntry(form,placeholder_text="YYYY-MM-DD",width=130); dt.insert(0,date.today().isoformat()); dt.grid(row=0,column=1,padx=8)
            st=ctk.CTkEntry(form,placeholder_text="Start HH:MM",width=110); st.insert(0,"10:00"); st.grid(row=0,column=2,padx=8)
            et=ctk.CTkEntry(form,placeholder_text="End HH:MM",width=110); et.insert(0,"11:00"); et.grid(row=0,column=3,padx=8)
            purpose=ctk.CTkEntry(form,placeholder_text="Purpose",width=190); purpose.grid(row=1,column=0,padx=8,pady=8)
            attendees=ctk.CTkEntry(form,placeholder_text="Participants",width=110); attendees.insert(0,"10"); attendees.grid(row=1,column=1,padx=8)
            def submit():
                try:
                    if not fac.get(): raise ValueError("Select a facility.")
                    create_booking(int(fac.get().split("|")[0]),self.user["id"],dt.get(),st.get(),et.get(),purpose.get(),int(attendees.get()))
                    messagebox.showinfo("Booking","Request submitted and awaiting review."); self.show_bookings()
                except Exception as exc: messagebox.showerror("Booking not created",str(exc))
            styled_button(form,"Submit request",submit).grid(row=1,column=2,padx=8)
        rows=list_bookings(None if role==ADMIN else self.user["id"])
        wrap,tree=self.table(body,("id","facility","building","requester","booking_date","start_time","end_time","purpose","attendees","status"),rows); wrap.pack(fill="x")
        if role==ADMIN:
            actions=ctk.CTkFrame(body,fg_color="transparent"); actions.pack(anchor="e",pady=10)
            def decide(status):
                sel=tree.selection()
                if not sel: messagebox.showwarning("Select request","Select a booking row first."); return
                vals=tree.item(sel[0],"values")
                try: review_booking(int(vals[0]),status,self.user["id"]); messagebox.showinfo("Booking",f"Request {status.lower()}."); self.show_bookings()
                except Exception as exc: messagebox.showerror("Review failed",str(exc))
            styled_button(actions,"Approve",lambda:decide("Approved")).pack(side="left",padx=5)
            styled_button(actions,"Reject",lambda:decide("Rejected"),kind="light").pack(side="left",padx=5)
    def show_assets(self):
        body=self.page("Asset register","Equipment inventory and condition tracking.")
        if self.user["role"] in (ADMIN,"Lab Assistant"):
            form=ctk.CTkFrame(body,fg_color="white",corner_radius=12); form.pack(fill="x",pady=(0,12))
            code=ctk.CTkEntry(form,placeholder_text="Asset code",width=135); code.grid(row=0,column=0,padx=6,pady=12)
            name=ctk.CTkEntry(form,placeholder_text="Asset name",width=180); name.grid(row=0,column=1,padx=6)
            cat=ctk.CTkComboBox(form,values=["Computer","Laptop","Projector","Printer","Lab Instrument","Networking","Furniture"],width=150); cat.grid(row=0,column=2,padx=6)
            serial=ctk.CTkEntry(form,placeholder_text="Serial number",width=160); serial.grid(row=0,column=3,padx=6)
            def add():
                try: add_asset(code.get(),name.get(),cat.get(),serial.get(),None,None); messagebox.showinfo("Asset","Asset added."); self.show_assets()
                except Exception as exc: messagebox.showerror("Unable to add asset",str(exc))
            styled_button(form,"Add asset",add).grid(row=0,column=4,padx=6)
        rows=list_assets(); wrap,tree=self.table(body,("asset_code","name","category","serial_number","building","room","condition","status"),rows); wrap.pack(fill="x")
        if self.user["role"] in (ADMIN,"Lab Assistant"):
            actions=ctk.CTkFrame(body,fg_color="transparent"); actions.pack(anchor="e",pady=10)
            def mark():
                sel=tree.selection()
                if not sel: messagebox.showwarning("Select asset","Select an asset first."); return
                asset=next((a for a in rows if a["asset_code"]==tree.item(sel[0],"values")[0]),None)
                if asset:
                    set_asset_condition(asset["id"],"Needs Repair"); messagebox.showinfo("Asset","Asset marked as needing repair."); self.show_assets()
            styled_button(actions,"Mark selected needs repair",mark,kind="light")
    def show_maintenance(self):
        role=self.user["role"]; body=self.page("Maintenance desk","Report a campus fault and track repair progress.")
        facilities=list_facilities(); assets=list_assets()
        # Students are allowed to report faults too; they only see their own tickets.
        form=ctk.CTkFrame(body,fg_color="white",corner_radius=12); form.pack(fill="x",pady=(0,14))
        targets=[f"Facility: {x['id']} | {x['name']}" for x in facilities]+[f"Asset: {x['id']} | {x['name']}" for x in assets]
        target=ctk.CTkComboBox(form,values=targets,width=270); target.grid(row=0,column=0,padx=8,pady=12)
        category=ctk.CTkComboBox(form,values=["Electrical","Equipment","Internet","Furniture","Plumbing","Infrastructure"],width=150); category.grid(row=0,column=1,padx=8)
        desc=ctk.CTkEntry(form,placeholder_text="Describe the issue clearly",width=300); desc.grid(row=0,column=2,padx=8)
        def submit():
            try:
                val=target.get()
                if not val: raise ValueError("Select the affected facility or asset.")
                if val.startswith("Facility:"): fid=int(val.split("|")[0].split(":")[1]); aid=None
                else: aid=int(val.split("|")[0].split(":")[1]); fid=None
                rid=create_request(self.user["id"],fid,aid,category.get(),desc.get())
                messagebox.showinfo("Maintenance",f"Request #{rid} submitted."); self.show_maintenance()
            except Exception as exc: messagebox.showerror("Unable to submit",str(exc))
        styled_button(form,"Submit report",submit).grid(row=0,column=3,padx=8)
        rows=list_requests(None if role in (ADMIN,"Maintenance Staff") else self.user["id"])
        wrap,tree=self.table(body,("id","item","category","description","priority","status","reporter","reported_at"),rows); wrap.pack(fill="x")
        if role in (ADMIN,"Maintenance Staff"):
            actions=ctk.CTkFrame(body,fg_color="transparent"); actions.pack(anchor="e",pady=10)
            status=ctk.CTkComboBox(actions,values=["Assigned","In Progress","Resolved","Closed"],width=150); status.pack(side="left",padx=6)
            def update():
                sel=tree.selection()
                if not sel: messagebox.showwarning("Select request","Select a request first."); return
                try: update_status(int(tree.item(sel[0],"values")[0]),status.get(),self.user["id"]); messagebox.showinfo("Maintenance","Status updated and reporter notified."); self.show_maintenance()
                except Exception as exc: messagebox.showerror("Update failed",str(exc))
            styled_button(actions,"Update selected",update).pack(side="left")
    def show_energy(self):
        body=self.page("Energy intelligence","Recorded building-level meter readings. Demo data is not live IoT telemetry.")
        with connection() as conn:
            rows=[dict(r) for r in conn.execute("""SELECT e.recorded_on,b.name building,e.meter_id,e.consumption_kwh,e.cost,e.source FROM energy_records e JOIN buildings b ON b.id=e.building_id ORDER BY recorded_on DESC""")]
            totals=[dict(r) for r in conn.execute("""SELECT b.name,COALESCE(SUM(e.consumption_kwh),0) kwh,COALESCE(SUM(e.cost),0) cost FROM buildings b LEFT JOIN energy_records e ON e.building_id=b.id GROUP BY b.id""")]
            monthly=[dict(r) for r in conn.execute("""SELECT substr(recorded_on,1,7) month,SUM(consumption_kwh) kwh FROM energy_records GROUP BY substr(recorded_on,1,7) ORDER BY month""")]
        if monthly:
            try:
                from matplotlib.figure import Figure
                from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
                fig=Figure(figsize=(8,2.7),dpi=100); ax=fig.add_subplot(111)
                ax.bar([x["month"] for x in monthly],[x["kwh"] for x in monthly]); ax.set_ylabel("kWh"); ax.set_title("Recorded monthly consumption"); fig.tight_layout()
                chart=FigureCanvasTkAgg(fig,master=body); chart.draw(); chart.get_tk_widget().pack(fill="x",pady=(0,12))
            except Exception as exc: ctk.CTkLabel(body,text=f"Chart unavailable: {exc}").pack()
        self.table(body,("name","kwh","cost"),totals)[0].pack(fill="x",pady=(0,12))
        self.table(body,("recorded_on","building","meter_id","consumption_kwh","cost","source"),rows)[0].pack(fill="x")
    def show_notifications(self):
        body=self.page("Notifications","Booking decisions and maintenance updates for your account.")
        styled_button(body,"Mark all as read",lambda:(mark_all_read(self.user["id"]),self.show_notifications()),kind="light").pack(anchor="e",pady=(0,10))
        rows=list_notifications(self.user["id"])
        if not rows: ctk.CTkLabel(body,text="You're all caught up.",text_color=COLORS["muted"]).pack(pady=30); return
        for item in rows:
            card=ctk.CTkFrame(body,fg_color="white",corner_radius=12,border_width=1,border_color=COLORS["line"]); card.pack(fill="x",pady=5)
            ctk.CTkLabel(card,text=("● " if not item["is_read"] else "")+item["title"],font=("Segoe UI",13,"bold"),text_color=COLORS["ink"]).pack(anchor="w",padx=14,pady=(10,2))
            ctk.CTkLabel(card,text=item["message"],text_color=COLORS["muted"],wraplength=760).pack(anchor="w",padx=14,pady=(0,4))
            ctk.CTkLabel(card,text=item["created_at"],text_color=COLORS["muted"],font=("Segoe UI",9)).pack(anchor="w",padx=14,pady=(0,9))
            if not item["is_read"]: ctk.CTkButton(card,text="Mark read",width=90,height=28,command=lambda nid=item["id"]:(mark_read(nid,self.user["id"]),self.show_notifications())).pack(anchor="e",padx=12,pady=(0,8))
    def show_reports(self):
        body=self.page("Reports & exports","Choose a dataset and export it to the exact location you select.")
        options=[("Facilities","SELECT room_code,name,facility_type,status,condition FROM facilities",["Room","Name","Type","Status","Condition"]),("Assets","SELECT asset_code,name,category,condition,status FROM assets",["Asset code","Name","Category","Condition","Status"]),("Maintenance","SELECT id,category,description,priority,status,reported_at FROM maintenance_requests",["ID","Category","Description","Priority","Status","Reported"]),("Bookings","SELECT id,booking_date,start_time,end_time,purpose,attendees,status FROM facility_bookings",["ID","Date","Start","End","Purpose","Attendees","Status"]),("Energy","SELECT recorded_on,meter_id,consumption_kwh,cost,source FROM energy_records",["Date","Meter","kWh","Cost","Source"])]
        for title,sql,headers in options:
            card=ctk.CTkFrame(body,fg_color="white",corner_radius=12); card.pack(fill="x",pady=6)
            ctk.CTkLabel(card,text=title,font=("Segoe UI",14,"bold"),text_color=COLORS["ink"]).pack(side="left",padx=16,pady=14)
            def export(query=sql,cols=headers,label=title):
                path=filedialog.asksaveasfilename(defaultextension=".xlsx",initialfile=label.lower()+"_report.xlsx",filetypes=[("Excel workbook","*.xlsx"),("CSV","*.csv"),("PDF","*.pdf")])
                if not path:return
                try:
                    with connection() as conn: rows=[tuple(r) for r in conn.execute(query)]
                    result=export_rows(path,cols,rows); messagebox.showinfo("Export complete",f"Report saved to:\n{result}")
                except Exception as exc: messagebox.showerror("Export failed",str(exc))
            styled_button(card,"Export",export,kind="light").pack(side="right",padx=14,pady=8)
