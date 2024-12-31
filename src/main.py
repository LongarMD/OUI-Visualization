from common.app import App
from modules.main_menu import MainMenu


def main():
    app = App()
    MainMenu.show()

    app.mainloop()


if __name__ == "__main__":
    main()
