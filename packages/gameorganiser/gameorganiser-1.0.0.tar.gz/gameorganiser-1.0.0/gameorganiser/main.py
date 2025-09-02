import json
import os


def load_game_data(filename):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_directory, filename)

    if os.path.exists(full_path):
        with open(full_path, "r") as file:
            return json.load(file)
    else:
        print(f"File {filename} not found. Starting a new save file")
        return {"games": [] }

def save_game_data(filename, data):
        script_directory = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(script_directory, filename)

        with open(full_path, "w") as file:
            json.dump(data, file, indent=4)

def add_game(data, name, game_type, row, col):
        game = {
            "name": name,
            "type": game_type,
            "row": row,
            "col": col
        }
        data["games"].append(game)

def main():
  filename = input("Enter the game file name (e.g., games.json): ")
  data = load_game_data(filename)

  while True:
      print("\nMenu:")
      print("1. Add a new game")
      print("2. View all games")
      print("3. Save and exit")

      choice = input("Enter your choice: ")

      if choice == '1':
            name = input("Enter game name: ")
            game_type = input("Enter game type: ")
            row = int(input("Enter rows number: "))
            col = int(input("Enter columns number: "))
            add_game(data, name, game_type, row, col)

      elif choice == "2":
            if data["games"]:
                for idx, game in enumerate(data["games"], start=1):
                    print(f"{idx}. Name: {game['name']}, Type: {game['type']}, Rows: {game['row']}, Columns: {game['col']}")
            else:
                print("No games available.")

      elif choice =="3":
        print("Attempting to save game data...")
        save_game_data(filename, data)
        print("Game data saved. Exiting...")
        input("Press Enter to exit...")
        break

      else:
        print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/