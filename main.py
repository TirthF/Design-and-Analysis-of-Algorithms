import heapq

# ROAD NETWORK

graph = {
    "N1": [("N2", 4), ("N4", 6)],
    "N2": [("N1", 4), ("N3", 3), ("N5", 3)],
    "N3": [("N2", 3), ("N5", 4)],
    "N4": [("N1", 6), ("N5", 3)],
    "N5": [("N2", 3), ("N3", 4), ("N4", 3)]
}

# AMBULANCE DATA

ambulances = {
    "A1": {"location": "N1", "status": "Available"},
    "A2": {"location": "N4", "status": "Available"},
    "A3": {"location": "N2", "status": "Available"}
}

# EMERGENCY DATA

emergencies = {
    "E1": {"location": "N3", "severity": "Critical"},
    "E2": {"location": "N5", "severity": "Serious"},
    "E3": {"location": "N4", "severity": "Moderate"}
}

# Validate emergency locations and severity levels
valid_severities = ["Critical", "Serious", "Moderate"]

for emergency_id, details in emergencies.items():

    if details["location"] not in graph:
        raise ValueError(
            f"Invalid location for {emergency_id}: "
            f"{details['location']}"
        )

    if details["severity"] not in valid_severities:
        raise ValueError(
            f"Invalid severity for {emergency_id}: "
            f"{details['severity']}"
        )

# EMERGENCY PRIORITY

severity_priority = {
    "Critical": 3,
    "Serious": 2,
    "Moderate": 1
}

# DIJKSTRA'S SHORTEST PATH ALGORITHM

def dijkstra(graph, start, destination):

    distances = {
        node: float("inf")
        for node in graph
    }

    previous = {
        node: None
        for node in graph
    }

    distances[start] = 0

    priority_queue = [(0, start)]

    while priority_queue:

        current_distance, current_node = heapq.heappop(priority_queue)

        if current_distance > distances[current_node]:
            continue

        if current_node == destination:
            break

        for neighbor, travel_time in graph[current_node]:

            new_distance = current_distance + travel_time

            if new_distance < distances[neighbor]:

                distances[neighbor] = new_distance

                previous[neighbor] = current_node

                heapq.heappush(
                    priority_queue,
                    (new_distance, neighbor)
                )

    path = []

    current_node = destination

    while current_node is not None:

        path.append(current_node)

        current_node = previous[current_node]

    path.reverse()

    return distances[destination], path

# CREATE TRAVEL-TIME MATRIX

def create_travel_time_matrix(graph, ambulances, emergencies):

    travel_times = {}

    routes = {}

    for ambulance_id, ambulance_details in ambulances.items():

        travel_times[ambulance_id] = {}

        routes[ambulance_id] = {}

        ambulance_location = ambulance_details["location"]

        for emergency_id, emergency_details in emergencies.items():

            emergency_location = emergency_details["location"]

            distance, path = dijkstra(
                graph,
                ambulance_location,
                emergency_location
            )

            travel_times[ambulance_id][emergency_id] = distance

            routes[ambulance_id][emergency_id] = path

    return travel_times, routes

# AMBULANCE ALLOCATION

def allocate_ambulances(ambulances, emergencies, travel_times, routes):

    assignments = {}
    waiting_queue = []

    # Sort emergencies from highest priority to lowest priority
    sorted_emergencies = sorted(
        emergencies.items(),
        key=lambda item: severity_priority[item[1]["severity"]],
        reverse=True
    )

    # Keep track of ambulances that are still available
    available_ambulances = {
        ambulance_id
        for ambulance_id, details in ambulances.items()
        if details["status"] == "Available"
    }

    for emergency_id, emergency_details in sorted_emergencies:

        if not available_ambulances:
            assignments[emergency_id] = {
                "ambulance": None,
                "travel_time": None,
                "route": None,
                "status": "Waiting",
                "priority": severity_priority[emergency_details["severity"]]
            }

            waiting_queue.append(emergency_id)

            continue

        # Find the available ambulance with minimum travel time
        selected_ambulance = min(
            available_ambulances,
            key=lambda ambulance_id:
            travel_times[ambulance_id][emergency_id]
        )

        travel_time = travel_times[
            selected_ambulance
        ][emergency_id]

        route = routes[
            selected_ambulance
        ][emergency_id]

        # Store the assignment
        assignments[emergency_id] = {
            "ambulance": selected_ambulance,
            "travel_time": travel_time,
            "route": route,
            "status": "Assigned"
        }

        # Mark ambulance as unavailable
        available_ambulances.remove(selected_ambulance)
        ambulances[selected_ambulance]["status"] = "Unavailable"

    return assignments, waiting_queue

# SIMULATE AMBULANCE COMPLETION

def simulate_ambulance_completion(
    ambulances, assignments, emergencies
):
    print("\n")
    print("AUTOMATIC AMBULANCE COMPLETION")

    # Find ambulances currently handling assigned emergencies.
    active_emergencies = []

    for emergency_id, details in assignments.items():

        ambulance_id = details["ambulance"]

        if (
            details["status"] == "Assigned"
            and ambulance_id is not None
            and ambulances[ambulance_id]["status"] == "Unavailable"
        ):
            active_emergencies.append(
                (ambulance_id, emergency_id, details)
            )

    # Stop if no ambulance has an assigned emergency.
    if not active_emergencies:
        print("No active ambulance assignments to complete.")
        return False

    # Simulate the next completion using the shortest
    # recorded response time as a simple proxy.
    ambulance_id, emergency_id, details = min(
        active_emergencies,
        key=lambda item: item[2]["travel_time"]
    )

    # Mark the emergency as completed.
    details["status"] = "Completed"

    # The ambulance is now at the emergency location.
    ambulances[ambulance_id]["location"] = (
        emergencies[emergency_id]["location"]
    )

    # Make the ambulance available for reassignment.
    ambulances[ambulance_id]["status"] = "Available"

    print("\nEmergency completed automatically:", emergency_id)
    print("Ambulance released:", ambulance_id)
    print(
        "Ambulance is now available at:",
        ambulances[ambulance_id]["location"]
    )

    return True

# DYNAMICALLY ASSIGN WAITING EMERGENCIES

def assign_waiting_emergencies(
    ambulances,
    emergencies,
    assignments,
    waiting_queue,
    travel_times,
    routes
):

    print("\nChecking waiting emergencies...")

    available_ambulances = {
        ambulance_id
        for ambulance_id, details in ambulances.items()
        if details["status"] == "Available"
    }

    # Process waiting emergencies according to priority
    waiting_queue.sort(
        key=lambda emergency_id:
        severity_priority[emergencies[emergency_id]["severity"]],
        reverse=True
    )

    for emergency_id in waiting_queue[:]:

        if not available_ambulances:
            break

        selected_ambulance = min(
            available_ambulances,
            key=lambda ambulance_id:
            travel_times[ambulance_id][emergency_id]
        )

        travel_time = travel_times[
            selected_ambulance
        ][emergency_id]

        route = routes[
            selected_ambulance
        ][emergency_id]

        assignments[emergency_id] = {
            "ambulance": selected_ambulance,
            "travel_time": travel_time,
            "route": route,
            "status": "Assigned",
            "priority": severity_priority[
                emergencies[emergency_id]["severity"]
            ]
        }

        available_ambulances.remove(selected_ambulance)
        ambulances[selected_ambulance]["status"] = "Unavailable"
        waiting_queue.remove(emergency_id)

        print(
            emergency_id,
            "is now assigned to",
            selected_ambulance,
            "| Response Time:",
            travel_time,
            "minutes"
        )

    return assignments, waiting_queue

# DISPLAY TRAVEL-TIME MATRIX

def display_travel_time_matrix(travel_times):

    print("\nTravel-Time Matrix:")

    print("       E1    E2    E3")

    for ambulance_id in travel_times:

        print(
            ambulance_id,
            "   ",
            travel_times[ambulance_id]["E1"],
            "     ",
            travel_times[ambulance_id]["E2"],
            "     ",
            travel_times[ambulance_id]["E3"]
        )

# DISPLAY ROUTES

def display_routes(travel_times, routes):

    print("\nRoutes:")

    for ambulance_id in routes:

        for emergency_id in routes[ambulance_id]:

            path = routes[ambulance_id][emergency_id]

            distance = travel_times[ambulance_id][emergency_id]

            print(
                ambulance_id,
                "->",
                emergency_id,
                ":",
                " -> ".join(path),
                "|",
                distance,
                "minutes"
            )

# RUN SCENARIO 1

def run_scenario_1():

    test_emergencies = {
        "E1": {"location": "N3", "severity": "Critical"},
        "E2": {"location": "N5", "severity": "Serious"},
        "E3": {"location": "N4", "severity": "Moderate"},
        "E4": {"location": "N1", "severity": "Critical"}
    }

    test_ambulances = {
        "A1": {"location": "N1", "status": "Available"},
        "A2": {"location": "N4", "status": "Available"},
        "A3": {"location": "N2", "status": "Available"}
    }

    travel_times, routes = create_travel_time_matrix(
        graph,
        test_ambulances,
        test_emergencies
    )

    assignments, waiting_queue = allocate_ambulances(
        test_ambulances,
        test_emergencies,
        travel_times,
        routes
    )

    print("\nScenario 1: More Emergencies Than Ambulances")

    for emergency_id, details in assignments.items():

        print(
            emergency_id,
            "->",
            details["ambulance"],
            "|",
            details["status"],
            "|",
            details["travel_time"],
            "minutes"
        )

# RUN SCENARIO 2

def run_scenario_2():

    test_emergencies = {
        "E1": {"location": "N3", "severity": "Critical"},
        "E2": {"location": "N3", "severity": "Serious"},
        "E3": {"location": "N3", "severity": "Moderate"}
    }

    test_ambulances = {
        "A1": {"location": "N1", "status": "Available"},
        "A2": {"location": "N4", "status": "Available"},
        "A3": {"location": "N2", "status": "Available"}
    }

    travel_times, routes = create_travel_time_matrix(
        graph,
        test_ambulances,
        test_emergencies
    )

    assignments, waiting_queue = allocate_ambulances(
        test_ambulances,
        test_emergencies,
        travel_times,
        routes
    )

    print("\nScenario 2: Multiple Emergencies at Same Location")

    for emergency_id, details in assignments.items():

        print(
            emergency_id,
            "->",
            details["ambulance"],
            "|",
            details["status"],
            "|",
            details["travel_time"],
            "minutes"
        )

# RUN SCENARIO 3

def run_scenario_3():

    test_emergencies = {
        "E1": {"location": "N3", "severity": "Critical"},
        "E2": {"location": "N5", "severity": "Serious"},
        "E3": {"location": "N4", "severity": "Moderate"}
    }

    test_ambulances = {
        "A1": {"location": "N1", "status": "Available"},
        "A2": {"location": "N4", "status": "Unavailable"},
        "A3": {"location": "N2", "status": "Available"}
    }

    travel_times, routes = create_travel_time_matrix(
        graph,
        test_ambulances,
        test_emergencies
    )

    assignments, waiting_queue = allocate_ambulances(
        test_ambulances,
        test_emergencies,
        travel_times,
        routes
    )

    print("\nScenario 3: One Ambulance Unavailable")

    for emergency_id, details in assignments.items():

        print(
            emergency_id,
            "->",
            details["ambulance"],
            "|",
            details["status"],
            "|",
            details["travel_time"],
            "minutes"
        )

# DISPLAY FINAL RESULTS

def display_final_results(assignments):

    print("\n")
    print("FINAL AMBULANCE ALLOCATION RESULTS")

    assigned_count = 0
    completed_count = 0
    waiting_count = 0
    total_response_time = 0

    for emergency_id, details in assignments.items():

        print("\nEmergency:", emergency_id)

        if details["status"] == "Assigned":

            assigned_count += 1
            total_response_time += details["travel_time"]

            print("Ambulance:", details["ambulance"])
            print("Status:", details["status"])
            print("Response Time:", details["travel_time"], "minutes")
            print("Route:", " -> ".join(details["route"]))

        elif details["status"] == "Completed":

            completed_count += 1
            total_response_time += details["travel_time"]

            print("Ambulance:", details["ambulance"])
            print("Status:", details["status"])
            print("Response Time:", details["travel_time"], "minutes")
            print("Route:", " -> ".join(details["route"]))

        else:

            waiting_count += 1

            print("Ambulance: None")
            print("Status:", details["status"])
            print("Priority:", details["priority"])
            print("Reason: No ambulance available")
            print("Response Time: Not available")
            print("Route: Not available")

    print("SUMMARY")

    total_emergencies = len(assignments)
    dispatched_count = assigned_count + completed_count

    print("Total Emergencies:", total_emergencies)
    print("Assigned Emergencies:", assigned_count)
    print("Completed Emergencies:", completed_count)
    print("Waiting Emergencies:", waiting_count)

    if dispatched_count > 0:

        average_response_time = (
            total_response_time / dispatched_count
        )

        print(
            "Total Recorded Travel Time:",
            total_response_time,
            "minutes"
        )

        print(
            "Average Recorded Travel Time:",
            round(average_response_time, 2),
            "minutes"
        )

    else:

        print("Total Response Time: Not available")
        print("Average Response Time: Not available")

    print()

# GET EMERGENCY INPUT FROM USER

def get_emergency_input():

    emergencies = {}

    print("ENTER EMERGENCY DETAILS")
    
    while True:
        try:
            number_of_emergencies = int(
                input("\nEnter number of emergencies: ")
            )

            if number_of_emergencies <= 0:
                print("Please enter a number greater than zero.")
                continue

            break

        except ValueError:
            print("Invalid input. Please enter a whole number.")

    print("\nAvailable Locations:")
    print(", ".join(graph.keys()))

    print("\nSeverity Levels:")
    print("1. Critical")
    print("2. Serious")
    print("3. Moderate")

    for i in range(1, number_of_emergencies + 1):

        print("\nEmergency", i)

        location = input(
            "Enter emergency location: "
        ).upper()

        while location not in graph:
            print("Invalid location. Please enter a valid location.")
            location = input(
                "Enter emergency location: "
            ).upper()

        severity_choice = input(
            "Enter severity (1/2/3): "
        )

        while severity_choice not in ["1", "2", "3"]:
            print("Invalid severity. Please enter 1, 2 or 3.")
            severity_choice = input(
                "Enter severity (1/2/3): "
            )

        if severity_choice == "1":
            severity = "Critical"
            priority = 3

        elif severity_choice == "2":
            severity = "Serious"
            priority = 2

        else:
            severity = "Moderate"
            priority = 1

        emergency_id = "E" + str(i)

        emergencies[emergency_id] = {
            "location": location,
            "severity": severity,
            "priority": priority
        }

    return emergencies

# MAIN PROGRAM

def main():

    print("\n")
    print("DYNAMIC AMBULANCE ALLOCATION SYSTEM")

    emergencies = get_emergency_input()

    print("\nCalculating shortest routes...")

    travel_times, routes = create_travel_time_matrix(
        graph,
        ambulances,
        emergencies
    )

    print("Shortest routes calculated successfully.")

    assignments, waiting_queue = allocate_ambulances(
        ambulances,
        emergencies,
        travel_times,
        routes
    )

    display_final_results(assignments)

    if waiting_queue:
        print("Waiting Queue:", " -> ".join(waiting_queue))
    else:
        print("Waiting Queue: Empty\n")
    
    while any(
        details["status"] == "Assigned"
        for details in assignments.values()
    ):

        # Automatically complete the next assigned emergency.
        completed = simulate_ambulance_completion(
            ambulances,
            assignments,
            emergencies
        )

        if not completed:
            print("Automatic processing stopped.")
            break

        # Recalculate routes from current ambulance locations.
        travel_times, routes = create_travel_time_matrix(
            graph,
            ambulances,
            emergencies
        )

        # Reassign available ambulances to waiting emergencies.
        assignments, waiting_queue = assign_waiting_emergencies(
            ambulances,
            emergencies,
            assignments,
            waiting_queue,
            travel_times,
            routes
        )

        print("\nUpdated Waiting Queue:")

        if waiting_queue:
            print(" -> ".join(waiting_queue))
        else:
            print("Empty")

        display_final_results(assignments)

# START PROGRAM

if __name__ == "__main__":
    main()
