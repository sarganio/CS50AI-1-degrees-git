import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):  # source - person_id, target - person_id
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    # TODO
    shortersPath = []
    exploredSet = QueueFrontier()
    frontier = QueueFrontier()
    # create the initial node as source
    currentNode = Node([None, source], None, neighbors_for_person(source))
    frontier.add(currentNode)
    while (True):
        # if the frontier is empty then there's no solution
        if frontier.empty():
            return None
        # remove a node from the fronteir
        currentNode = frontier.remove()
        # check if the target node was found
        if (currentNode.state[1] == target):
            # if so generate the path from source to target
            return generate_path_to_target(shortersPath, currentNode, source)
        # add current node to the explored state
        exploredSet.add(currentNode)
        # add resulting nodes to the frontier if they aren't already in the frontier or in the explored set
        for neighbor in neighbors_for_person(currentNode.state[1]):
            if (not frontier.contains_state(neighbor) and not exploredSet.contains_state(neighbor)):
                neighbornodeToAdd = Node(neighbor, currentNode, neighbors_for_person(neighbor[1]))
                frontier.add(neighbornodeToAdd)
                # check if the neighbor is the target node
                if (neighbor[1] == target):
                    currentNode = neighbornodeToAdd
                    return generate_path_to_target(shortersPath, currentNode, source)
                

def generate_path_to_target(shortersPath, currentNode, source):

    while (currentNode.state[1] != source):
        shortersPath.append(currentNode.state)
        currentNode = currentNode.parent

    shortersPath.reverse()
    return shortersPath

        
def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for neighbor_id in movies[movie_id]["stars"]:
            # skip if the neighbor found is the input person - don't return the person in it's neighbors list
            if (neighbor_id == person_id):
                continue
            neighbors.add((movie_id, neighbor_id))
    return neighbors


if __name__ == "__main__":
    main()
