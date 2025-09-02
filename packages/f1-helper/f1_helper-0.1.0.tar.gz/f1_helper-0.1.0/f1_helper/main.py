import fastf1
import fastf1.ergast as ergast
from datetime import datetime
from tabulate import tabulate

# --- F1 Points System ---
GP_POINTS = 25
SPRINT_POINTS = 8
FASTEST_LAP = 1


def max_points_remaining(races_left, sprints_left, is_constructor=False):
    """Calculate maximum possible points left in the season."""
    per_gp = GP_POINTS + FASTEST_LAP
    per_sprint = SPRINT_POINTS
    if is_constructor:
        per_gp = (per_gp*2) - 8
        per_sprint = (per_sprint*2) - 1
    return races_left * per_gp + sprints_left * per_sprint


def check_driver_simple(driver_name, year=datetime.now().year):
    """Simple WDC contention check."""
    erg = ergast.Ergast()
    standings = erg.get_driver_standings(season=year).content[0]

    # Find driver index
    driver_idx = None
    for i in range(len(standings)):
        full_name = f"{standings.givenName[i]} {standings.familyName[i]}".lower()
        if driver_name.lower() in full_name:
            driver_idx = i
            break
    if driver_idx is None:
        print(f"Driver '{driver_name}' not found!")
        return

    # Leader
    leader_idx = 0
    driver_points = float(standings.points[driver_idx])
    leader_points = float(standings.points[leader_idx])

    # Upcoming events
    schedule = fastf1.get_event_schedule(year, include_testing=False)
    upcoming = schedule[schedule['EventDate'] > datetime.today()]

    gp_left = len(upcoming)
    sprint_left = upcoming['EventFormat'].str.lower().str.contains('sprint').sum()

    max_remaining = max_points_remaining(gp_left, sprint_left, is_constructor=False)

    print(f"\n=== Driver Championship Check: {standings.givenName[driver_idx]} {standings.familyName[driver_idx]} ===")
    print(f"Current Points: {driver_points}")
    print(f"Leader: {standings.givenName[leader_idx]} {standings.familyName[leader_idx]} ({leader_points})")
    print(f"Races left: {gp_left}, Sprint weekends left: {sprint_left}")
    print(f"Max points remaining: {max_remaining}")

    if driver_points + max_remaining > leader_points:
        print("🎉 Good news! Your driver is still in the running for the championship!")
    else:
        print("😢 Sorry, it looks like the championship is out of reach now.")


def check_driver_detailed(driver_name, year=datetime.now().year):
    """Detailed per-weekend scenario with realistic cumulative points and tie handling."""
    erg = ergast.Ergast()
    standings = erg.get_driver_standings(season=year).content[0]

    # Find driver index
    driver_idx = None
    for i in range(len(standings)):
        full_name = f"{standings.givenName[i]} {standings.familyName[i]}".lower()
        if driver_name.lower() in full_name:
            driver_idx = i
            break
    if driver_idx is None:
        print(f"Driver '{driver_name}' not found!")
        return

    # Leader and rival
    leader_idx = 0
    rival_idx = 1 if driver_idx == leader_idx else leader_idx

    driver_points = float(standings.points[driver_idx])
    rival_points = float(standings.points[rival_idx])

    driver_name_full = f"{standings.givenName[driver_idx]} {standings.familyName[driver_idx]}"
    rival_name_full = f"{standings.givenName[rival_idx]} {standings.familyName[rival_idx]}"

    # Upcoming events
    schedule = fastf1.get_event_schedule(year, include_testing=False)
    upcoming = schedule[schedule['EventDate'] > datetime.today()]

    weekends = []
    for _, race in upcoming.iterrows():
        is_sprint = 'Sprint Weekend' if 'sprint' in race["EventFormat"].lower() else 'Normal GP'
        max_driver = GP_POINTS + FASTEST_LAP
        if is_sprint == 'Sprint':
            max_driver += SPRINT_POINTS
        weekends.append({
            "name": race["OfficialEventName"],
            "date": race["EventDate"].strftime("%Y-%m-%d"),
            "type": is_sprint,
            "max_driver": max_driver
        })

    total_max_driver = sum(w["max_driver"] for w in weekends)

    if driver_points + total_max_driver <= rival_points:
        print(f"\n😓 {driver_name_full} can't overtake {rival_name_full} even by scoring maximum points in the remaining races.")
        print(f"Points gap: {rival_points - driver_points}, Maximum points still up for grabs: {total_max_driver}")
        return

    cumulative_driver = driver_points
    cumulative_rival = rival_points
    table = []

    for i, w in enumerate(weekends):
        remaining_max_driver = sum(week["max_driver"] for week in weekends[i:])
        rival_max_allowed = remaining_max_driver + cumulative_driver - cumulative_rival - 1

        rival_max_allowed = min(rival_max_allowed, w["max_driver"])
        rival_max_allowed = max(rival_max_allowed, 0)

        table.append([
            w["name"],
            w["date"],
            w["type"],
            w["max_driver"],
            round(rival_max_allowed, 1)
        ])

        cumulative_driver += w["max_driver"]
        cumulative_rival += rival_max_allowed

    sprint_count = sum(1 for w in weekends if w["type"] == 'Sprint Weekend')

    print(f"\n=== Championship Scenario: {driver_name_full} vs {rival_name_full} ===")
    print(f"{driver_name_full} Points: {driver_points}")
    print(f"{rival_name_full} Points: {rival_points} (rival)")
    print(f"Remaining Races: {len(weekends)}, Sprint Weekends: {sprint_count}")
    print(f"Total max possible points for {driver_name_full}: {total_max_driver}\n")

    print(tabulate(
        table,
        headers=["GP Name", "Date", "Type", f"{driver_name_full} Max Points", f"{rival_name_full} Max Allowed"],
        tablefmt="fancy_grid"
    ))


def check_constructor(team_name, year=datetime.now().year):
    """Check if a constructor can still win the WCC."""
    erg = ergast.Ergast()
    standings = erg.get_constructor_standings(season=year).content[0]

    team_idx = None
    for i in range(len(standings)):
        if team_name.lower() in standings.constructorId[i].lower():
            team_idx = i
            break
    if team_idx is None:
        print(f"❌ Constructor '{team_name}' not found!")
        return

    team_points = float(standings.points[team_idx])
    leader_points = float(standings.points[0])

    schedule = fastf1.get_event_schedule(year, include_testing=False)
    upcoming = schedule[schedule['EventDate'] > datetime.today()]

    gp_left = len(upcoming)
    sprint_left = upcoming['EventFormat'].str.lower().str.contains('sprint').sum()
    max_remaining = max_points_remaining(gp_left, sprint_left, is_constructor=True)

    print(f"\n=== Constructor Championship Check: {standings.constructorName[team_idx]} ===")
    print(f"Current Points: {team_points}")
    print(f"Leader: {standings.constructorName[0]} ({leader_points})")
    print(f"Races left: {gp_left}, Sprint weekends left: {sprint_left}")
    print(f"Max points remaining: {max_remaining}")

    if team_points + max_remaining >= leader_points:
        print("🎉 The team is still fighting for the Constructors' Championship!")
    else:
        print("😢 The championship is out of reach for the team now.")


def main():
    """Main CLI menu."""
    while True:
        print("\n--- F1 Championship Helper ---")
        print("1. Check Driver WDC Contention (simple)")
        print("2. Check Driver WDC Detailed Scenario")
        print("3. Check Constructor WCC Contention")
        print("4. Exit")
        choice = input("Select an option (1-4): ").strip()

        if choice == "1":
            driver_name = input("Enter Driver Name: ").strip()
            year = datetime.now().year
            check_driver_simple(driver_name, year)
        elif choice == "2":
            driver_name = input("Enter Driver Name: ").strip()
            year = datetime.now().year
            check_driver_detailed(driver_name, year)
        elif choice == "3":
            team_name = input("Enter Constructor Name: ").strip()
            year = datetime.now().year
            check_constructor(team_name, year)
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice! Please select 1-4.")
