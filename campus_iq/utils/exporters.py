"""Report exports to CSV, Excel and PDF."""
from pathlib import Path
import csv
from config import EXPORT_DIR

def export_rows(filename,headers,rows,kind="csv"):
    EXPORT_DIR.mkdir(parents=True,exist_ok=True)
    path=EXPORT_DIR/filename
    if kind=="csv":
        with path.open("w",newline="",encoding="utf-8-sig") as handle:
            writer=csv.writer(handle); writer.writerow(headers); writer.writerows(rows)
    elif kind=="xlsx":
        from openpyxl import Workbook
        wb=Workbook(); ws=wb.active; ws.title="CAMPUS IQ Report"
        ws.append(headers)
        for row in rows: ws.append(list(row))
        ws.freeze_panes="A2"; ws.auto_filter.ref=ws.dimensions
        wb.save(path)
    elif kind=="pdf":
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4,landscape
        from reportlab.platypus import SimpleDocTemplate,Table,TableStyle,Paragraph,Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        doc=SimpleDocTemplate(str(path),pagesize=landscape(A4))
        data=[headers]+[list(map(str,r)) for r in rows]
        table=Table(data,repeatRows=1)
        table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#172554")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.35,colors.HexColor("#DCE3ED")),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F4F7FB")]),
            ("FONTSIZE",(0,0),(-1,-1),8),("PADDING",(0,0),(-1,-1),6)]))
        doc.build([Paragraph("CAMPUS IQ — Operational Report",getSampleStyleSheet()["Title"]),Spacer(1,12),table])
    else: raise ValueError("Unsupported export format.")
    return path
