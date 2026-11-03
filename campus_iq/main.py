"""CAMPUS IQ entry point."""
from database.db import initialize_database
from ui.app import CampusIQApp

def main():
    initialize_database()
    CampusIQApp().mainloop()

if __name__ == "__main__":
    main()
