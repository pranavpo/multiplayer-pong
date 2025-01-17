import game
import server


def main():
    choice = input(
        "Do you want to run as 'client' or 'server'? ").strip().lower()
    if choice == "client":
        game.client()
        # run_game()  # Start the game loop only after the client is initialized
    elif choice == "server":
        server.server()
    else:
        print("Invalid choice. Exiting...")


main()
