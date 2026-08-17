from typing import Dict, Any


VEHICLE_WEIGHTS = {
    "car": 1.0,
    "motorcycle": 0.6,
    "bus": 2.5,
    "truck": 2.5,
}


def calculate_traffic_pressure(counts: Dict[str, int]) -> float:
    pressure = 0.0

    for vehicle_type, count in counts.items():
        weight = VEHICLE_WEIGHTS.get(vehicle_type, 1.0)
        pressure += count * weight

    return round(pressure, 2)


def calculate_density(total_vehicles: int, threshold: int = 50) -> str:
    if total_vehicles >= threshold:
        return "HIGH"

    if total_vehicles >= max(0, threshold - 20):
        return "MEDIUM"

    return "LOW"


def calculate_green_time(
    density: str,
    traffic_pressure: float,
    queue_length_m: float = 0,
    avg_wait_seconds: float = 0,
    emergency_detected: bool = False,
) -> int:

    if emergency_detected:
        return 90

    if density == "HIGH":
        green_time = 60
    elif density == "MEDIUM":
        green_time = 40
    else:
        green_time = 25

    if queue_length_m >= 50:
        green_time += 15
    elif queue_length_m >= 30:
        green_time += 10
    elif queue_length_m >= 15:
        green_time += 5

    if avg_wait_seconds >= 90:
        green_time += 10
    elif avg_wait_seconds >= 60:
        green_time += 5

    if traffic_pressure >= 80:
        green_time += 10
    elif traffic_pressure >= 50:
        green_time += 5

    return min(90, max(20, green_time))


def generate_transportation_decision(
    counts: Dict[str, int],
    queue_length_m: float = 0,
    avg_speed_kmh: float = 0,
    avg_wait_seconds: float = 0,
    threshold: int = 50,
    emergency_detected: bool = False,
    emergency_type: str = None,
) -> Dict[str, Any]:

    total_vehicles = sum(counts.values())

    density = calculate_density(
        total_vehicles,
        threshold
    )

    traffic_pressure = calculate_traffic_pressure(
        counts
    )

    green_time = calculate_green_time(
        density=density,
        traffic_pressure=traffic_pressure,
        queue_length_m=queue_length_m,
        avg_wait_seconds=avg_wait_seconds,
        emergency_detected=emergency_detected,
    )

    if emergency_detected:
        decision = "EMERGENCY PRIORITY"
        reason = (
            f"{emergency_type or 'Emergency vehicle'} detected. "
            "Priority green time is recommended."
        )

    elif density == "HIGH":
        decision = "EXTEND GREEN"
        reason = (
            "High traffic density detected. "
            "Longer green time is recommended to reduce congestion."
        )

    elif density == "MEDIUM":
        decision = "MODERATE GREEN"
        reason = (
            "Moderate traffic detected. "
            "Balanced green time is recommended."
        )

    else:
        decision = "NORMAL GREEN"
        reason = (
            "Traffic is relatively low. "
            "Normal green time is sufficient."
        )

    if queue_length_m >= 50:
        reason += " Queue length is also high."

    return {
        "total_vehicles": total_vehicles,
        "traffic_pressure": traffic_pressure,
        "density": density,
        "queue_length_m": round(queue_length_m, 1),
        "avg_speed_kmh": round(avg_speed_kmh, 1),
        "avg_wait_seconds": round(avg_wait_seconds, 1),
        "recommended_green_seconds": green_time,
        "decision": decision,
        "reason": reason,
        "emergency": {
            "detected": emergency_detected,
            "type": emergency_type,
        },
    }
